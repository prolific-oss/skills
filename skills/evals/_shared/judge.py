"""LLM-as-judge grader for skill eval assertions."""

from __future__ import annotations

import json

import anthropic
from langfuse import observe


@observe(name="grade_assertions")
def grade_assertions(
    anthropic_client: anthropic.Anthropic,
    output: str,
    assertions: list[str],
    model: str,
) -> list[dict]:
    """
    Grade each assertion against the agent output using a fast LLM judge.

    The judge is asked for concrete evidence (a direct quote) rather than a
    bare pass/fail so grades are auditable in the Langfuse UI.

    Assertions travel from evals.json → Langfuse dataset item metadata →
    evaluator closure → here, keeping the judge itself skill-agnostic.
    """
    results = []
    for assertion in assertions:
        grading_prompt = (
            "You are grading an AI agent response against a single assertion.\n\n"
            f"Agent response:\n{output}\n\n"
            f"Assertion to check: {assertion}\n\n"
            "Reply with valid JSON only — no prose before or after:\n"
            '{"passed": true or false, "evidence": "direct quote or specific reference from the response"}'
        )
        resp = anthropic_client.messages.create(
            model=model,
            max_tokens=256,
            temperature=0,
            messages=[{"role": "user", "content": grading_prompt}],
        )
        try:
            raw = resp.content[0].text.strip()
            if raw.startswith("```"):
                lines = raw.splitlines()
                raw = "\n".join(lines[1:-1])
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"passed": False, "evidence": "Judge returned unparseable response"}
        result["assertion"] = assertion
        results.append(result)
    return results
