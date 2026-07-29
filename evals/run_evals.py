"""
Shared eval runner for Prolific automation skills.

One script for every skill — pass the skill's folder name (same name under
both skills/ and evals/) as the first argument.

Usage
-----
    python run_evals.py <skill-name>                 # run with skill (default)
    python run_evals.py <skill-name> --without-skill # baseline without skill
    python run_evals.py <skill-name> --both          # both experiments for side-by-side comparison
    python run_evals.py <skill-name> --max-turns 15
    python run_evals.py <skill-name> --tag eligibility --tag participant-group

Requirements
------------
    pip install anthropic langfuse langsmith claude-agent-sdk python-dotenv

Environment variables (copy .env.example to .env in this directory — evals/,
not evals/<skill-name>/; credentials are shared across all skills' evals):
    ANTHROPIC_API_KEY
    PROLIFIC_TEST_TOKEN  (preferred) or PROLIFIC_TOKEN
    LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_BASE_URL
    LANGFUSE_USER_ID  (optional; attributes eval traces to a Langfuse user)
    OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_EXPORTER_OTLP_HEADERS

Adding a new skill's eval
--------------------------
No new run_evals.py needed. Add evals/<skill-name>/evals.json (see EVALS.md
for the schema) and run this script with that skill name.
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

_EVALS_ROOT = Path(__file__).parent
_SKILLS_ROOT = _EVALS_ROOT.parent / "skills"
sys.path.insert(0, str(_EVALS_ROOT))

from _shared.judge import grade_assertions  # noqa: E402
from _shared.runner import run_claude_code  # noqa: E402
from _shared.sandbox import build_agent_env, ensure_prolific_binary  # noqa: E402

JUDGE_MODEL = "claude-haiku-4-5-20251001"


# ---------------------------------------------------------------------------
# Dataset sync
# ---------------------------------------------------------------------------

def load_evals(evals_path: Path) -> dict:
    with open(evals_path) as f:
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

def _inject_skill(cwd: str, skill_path: Path) -> None:
    """Write the skill into CLAUDE.md so the agent reads it as project context."""
    with open(os.path.join(cwd, "CLAUDE.md"), "w") as f:
        f.write(skill_path.read_text())

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
    skill_name: str,
    skill_path: Path,
    tags: list[str],
) -> None:
    experiment_name = f"{skill_name}-{'with' if with_skill else 'without'}-skill"
    session_id = f"eval-{skill_name}-{uuid.uuid4().hex[:8]}"
    print(f"\nRunning experiment: {experiment_name} (session: {session_id})")

    dataset = langfuse.get_dataset(dataset_name)

    async def task(*, item, **kwargs) -> dict:
        prompt = item.input["prompt"]
        item_cwd = tempfile.mkdtemp(prefix=f"eval-{skill_name}-")
        try:
            if with_skill:
                _inject_skill(item_cwd, skill_path)
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
        "tags": [*tags, "test", with_or_without],
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
            description=f"{skill_name} {with_or_without} skill",
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run evals for a Prolific automation skill"
    )
    parser.add_argument(
        "skill_name",
        help="Skill folder name, matching both skills/<name>/SKILL.md and evals/<name>/evals.json",
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
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Extra Langfuse tag for this skill's runs (repeatable)",
    )
    return parser.parse_args()


def main() -> None:
    env_file = _EVALS_ROOT / ".env"
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

    args = parse_args()
    skill_name = args.skill_name
    skill_path = _SKILLS_ROOT / skill_name / "SKILL.md"
    evals_path = _EVALS_ROOT / skill_name / "evals.json"

    if not skill_path.exists():
        raise FileNotFoundError(f"No SKILL.md found at {skill_path}")
    if not evals_path.exists():
        raise FileNotFoundError(f"No evals.json found at {evals_path}")

    langfuse = get_client()
    anthropic_client = anthropic.Anthropic()
    configure_claude_agent_sdk()

    prolific_bin = ensure_prolific_binary()

    evals_data = load_evals(evals_path)
    dataset_name = sync_dataset(langfuse, evals_data)

    tags = ["prolific-cli", *args.tag]

    if args.both:
        run_experiment(
            langfuse, anthropic_client, dataset_name, True,
            prolific_bin, args, skill_name, skill_path, tags,
        )
        run_experiment(
            langfuse, anthropic_client, dataset_name, False,
            prolific_bin, args, skill_name, skill_path, tags,
        )
    else:
        run_experiment(
            langfuse, anthropic_client, dataset_name, not args.without_skill,
            prolific_bin, args, skill_name, skill_path, tags,
        )

    langfuse.flush()
    print(f"\nDone. View results on Langfuse - dataset: {dataset_name})")


if __name__ == "__main__":
    main()
