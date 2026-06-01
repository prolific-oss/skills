"""
Eval runner for the recommend-study-filters skill.

Usage
-----
    python run_evals.py                 # run with skill (default)
    python run_evals.py --without-skill # baseline without skill
    python run_evals.py --both          # both experiments for side-by-side comparison
    python run_evals.py --max-turns 15

Requirements
------------
    pip install anthropic langfuse langsmith claude-agent-sdk python-dotenv

Environment variables (copy .env.example to .env):
    ANTHROPIC_API_KEY
    PROLIFIC_TEST_TOKEN  (preferred) or PROLIFIC_TOKEN
    LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
    LANGFUSE_USER_ID  (optional; attributes eval traces to a Langfuse user)
    OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_EXPORTER_OTLP_HEADERS
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import uuid
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from langfuse import Evaluation, get_client, observe, propagate_attributes
from langsmith.integrations.claude_agent_sdk import configure_claude_agent_sdk

_EVALS_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(_EVALS_ROOT))

from _shared.judge import grade_assertions  # noqa: E402
from _shared.runner import run_claude_code  # noqa: E402
from _shared.sandbox import build_agent_env, ensure_prolific_binary  # noqa: E402

SKILL_PATH = Path(__file__).parents[2] / "skills" / "recommend-study-filters" / "SKILL.md"
EVALS_PATH = Path(__file__).parent / "evals.json"

JUDGE_MODEL = "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Dataset sync
# ---------------------------------------------------------------------------

def load_evals() -> dict:
    with open(EVALS_PATH) as f:
        return json.load(f)


def sync_dataset(langfuse, evals_data: dict) -> str:
    """Sync evals.json to a Langfuse Dataset. Safe to call on every run."""
    dataset_name = f"skill-evals-{evals_data['skill_name']}"
    langfuse.create_dataset(
        name=dataset_name,
        description=f"Evals for the {evals_data['skill_name']} skill",
    )
    for case in evals_data["evals"]:
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            id=f"{evals_data['skill_name']}-{case['id']}",
            input={"prompt": case["prompt"]},
            expected_output=case["expected_output"],
            metadata={"id": case["id"], "assertions": case.get("assertions", [])},
        )
    return dataset_name


# ---------------------------------------------------------------------------
# Skill injection
# ---------------------------------------------------------------------------

def _inject_skill(cwd: str) -> None:
    """Write the skill into CLAUDE.md so the agent reads it as project context."""
    with open(os.path.join(cwd, "CLAUDE.md"), "w") as f:
        f.write(SKILL_PATH.read_text())

# ---------------------------------------------------------------------------
# Experiment
# ---------------------------------------------------------------------------

@observe(name="run_experiment")
def run_experiment(
    langfuse,
    anthropic_client: anthropic.Anthropic,
    dataset_name: str,
    with_skill: bool,
    prolific_bin: Path,
    args: argparse.Namespace,
) -> None:
    experiment_name = (
        f"recommend-study-filters-{'with' if with_skill else 'without'}-skill"
    )
    session_id = f"eval-recommend-filters-{uuid.uuid4().hex[:8]}"
    print(f"\nRunning experiment: {experiment_name} (session: {session_id})")

    dataset = langfuse.get_dataset(dataset_name)

    async def task(*, item, **kwargs) -> dict:
        prompt = item.input["prompt"]
        item_cwd = tempfile.mkdtemp(prefix="eval-recommend-filters-")
        try:
            if with_skill:
                _inject_skill(item_cwd)
            agent_env = build_agent_env(item_cwd, prolific_bin)
            result = await run_claude_code(prompt, args.max_turns, item_cwd, agent_env)
            return result
        finally:
            shutil.rmtree(item_cwd, ignore_errors=True)

    def evaluator(*, input, output, expected_output, metadata, **kwargs) -> list[dict]:
        assertions = (metadata or {}).get("assertions", [])
        if not assertions:
            return []
        grades = grade_assertions(
            anthropic_client, (output or {}).get("output", ""), assertions, JUDGE_MODEL
        )
        passed = sum(1 for g in grades if g["passed"])
        pass_rate = passed / len(grades) if grades else 0.0
        status = "PASS" if pass_rate == 1.0 else "FAIL"
        return [
            Evaluation(
                name="pass_fail",
                value=status,
                comment=json.dumps(grades, indent=2),
            )
        ]

    with_or_without = "with-skill" if with_skill else "without-skill"

    attrs = {
        "session_id": session_id,
        "tags": ["prolific-cli", "filters", "test", with_or_without],
    }
    if user_id := os.getenv("LANGFUSE_USER_ID"):
        attrs["user_id"] = user_id

    with propagate_attributes(**attrs):
        dataset.run_experiment(
            name=experiment_name,
            task=task,
            evaluators=[evaluator],
            max_concurrency=1,
            metadata={"max_turns": args.max_turns, "with_skill": with_skill},
            description=f"recommend-study-filters {with_or_without} skill",
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run evals for the recommend-study-filters skill"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--without-skill",
        action="store_true",
        help="Run baseline without the skill",
    )
    group.add_argument(
        "--both",
        action="store_true",
        help="Run with-skill then without-skill for side-by-side Langfuse comparison",
    )
    parser.add_argument("--max-turns", type=int, default=10)
    return parser.parse_args()


def main() -> None:
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        raise FileNotFoundError(
            f".env file not found at {env_file}\n"
            f"Run: cp {env_file.parent / '.env.example'} {env_file}  then fill in your credentials."
        )
    load_dotenv(env_file, override=True)

    os.environ.pop("CLAUDECODE", None)
    os.environ["LANGSMITH_OTEL_ENABLED"] = "true"
    os.environ["LANGSMITH_OTEL_ONLY"] = "true"
    os.environ["LANGSMITH_TRACING"] = "true"

    langfuse = get_client()
    anthropic_client = anthropic.Anthropic()
    configure_claude_agent_sdk()

    prolific_bin = ensure_prolific_binary()

    args = parse_args()
    evals_data = load_evals()
    dataset_name = sync_dataset(langfuse, evals_data)

    if args.both:
        run_experiment(langfuse, anthropic_client, dataset_name, True, prolific_bin, args)
        run_experiment(langfuse, anthropic_client, dataset_name, False, prolific_bin, args)
    else:
        run_experiment(
            langfuse, anthropic_client, dataset_name,
            not args.without_skill, prolific_bin, args,
        )

    langfuse.flush()
    print(f"\nDone. View results on Langfuse - dataset: {dataset_name})")


if __name__ == "__main__":
    main()
