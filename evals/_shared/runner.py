"""Claude Agent SDK wrapper for running a single eval item."""

from __future__ import annotations

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
)
from claude_agent_sdk.types import TextBlock, ToolUseBlock


async def run_claude_code(
    prompt: str,
    max_turns: int,
    item_cwd: str,
    agent_env: dict[str, str],
) -> dict:
    """
    Run Claude Code for a single eval item via ClaudeSDKClient.

    agent_env should come from build_agent_env() — it includes the prolific
    binary on PATH, the Prolific token, and blanked Langfuse credentials.

    setting_sources=["project"] restricts the agent to reading settings from
    item_cwd only, so the with-skill / without-skill split is fully controlled
    by whether CLAUDE.md was written to that directory.
    """
    stderr_lines: list[str] = []
    options = ClaudeAgentOptions(
        max_turns=max_turns,
        cwd=item_cwd,
        # bypassPermissions silently blocked the agent from running CLI commands
        # in this sandbox for an unknown reason; auto is less permissive but works.
        permission_mode="auto",
        setting_sources=["project"],
        stderr=lambda line: stderr_lines.append(line),
        env=agent_env,
    )

    last_assistant_text: list[str] = []
    all_text: list[str] = []
    result_text: str | None = None
    session_meta: dict = {}

    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                last_assistant_text = []
                for block in message.content:
                    if isinstance(block, TextBlock):
                        all_text.append(block.text)
                        last_assistant_text.append(block.text)
                    elif isinstance(block, ToolUseBlock):
                        tool_line = f"[tool_use: {block.name}] {block.input}"
                        all_text.append(tool_line)
                        last_assistant_text.append(tool_line)
            elif isinstance(message, ResultMessage):
                result_text = message.result
                session_meta = {
                    "duration_ms": message.duration_ms,
                    "duration_api_ms": message.duration_api_ms,
                    "num_turns": message.num_turns,
                    "session_id": message.session_id,
                    "total_cost_usd": message.total_cost_usd,
                    "is_error": message.is_error,
                }

    output = "\n".join(all_text) or result_text or ""
    return {"output": output, "session_meta": session_meta, "stderr": "\n".join(stderr_lines)}
