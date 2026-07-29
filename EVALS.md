# Skill Evals

Evals measure whether a skill actually improves agent behaviour. Each skill's eval runs the same prompts **with** and **without** the skill injected, then scores the outputs — giving you evidence of whether the skill is pulling its weight.

## Structure

```
evals/
├── pyproject.toml                   # shared dependencies (uv)
├── .env.example                     # copy to .env — credentials shared by every skill's evals
├── run_evals.py                     # single entry point for all skills, takes a skill name argument
├── _cache/                          # downloaded Prolific CLI binaries (gitignored)
├── _shared/
│   ├── sandbox.py                   # downloads the Prolific CLI binary; builds the agent's env
│   ├── runner.py                    # wraps Claude Agent SDK for a single eval item
│   ├── judge.py                     # LLM-as-judge: grades assertions against agent output
│   └── media.py                     # optional LangfuseMedia file attachments for eval cases
└── recommend-study-filters/
    └── evals.json                   # the eval dataset (prompts + assertions) — nothing else needed
```

`run_evals.py` and `.env`/`.env.example` are shared across every skill — there is exactly one of each in `evals/`, not one per skill folder. A skill's eval folder only ever needs its `evals.json` (plus optional fixtures if using file attachments).

## How an eval run works

1. **Load dataset** — `evals.json` is read and synced to a Langfuse Dataset. Each item has a `prompt` and a list of `assertions`.

2. **Inject the skill (or not)** — for the "with skill" experiment, the skill's `SKILL.md` is written to `CLAUDE.md` in a temp directory. The agent reads it as project context. For "without skill", that file is absent.

3. **Run the agent** — `runner.py` spins up a Claude Code agent via the Claude Agent SDK in the temp directory. The agent has the Prolific CLI on its `PATH` and a Prolific token in its environment; Langfuse credentials are blanked so the subprocess doesn't emit its own orphaned traces.

4. **Grade the output** — `judge.py` asks a fast LLM (Claude Haiku) to check each assertion against the agent's output, returning `passed: true/false` plus a direct quote as evidence.

5. **Record results** — pass/fail scores and grades are written back to Langfuse as `Evaluation` objects on each dataset run item. Two named experiments are created (`with-skill` / `without-skill`) so you can compare them side-by-side in the Langfuse UI.

## The eval loop

```
[Langfuse]                                    [Langfuse]                          [Langfuse]
┌───────────────────────┐                ┌──────────────────────┐            ┌─────────────────────┐
│  Dataset of user      │───────────────►│  Eval run with       │───────────►│       Results       │
│  prompts              │                │  ✳ Claude agent SDK  │            │                     │
└───────────────────────┘                └──────────────────────┘            └──────────┬──────────┘
         ▲                                                                              │
         │                                                                              ▼
┌────────┴──────────────┐                                                    ┌─────────────────────┐
│  Improve skill        │◄──────────────────────────────────────────────────-│                     │
│  [Locally]            │                                                    │       Scoring       │
└───────────────────────┘                                                    └─────────────────────┘
```

## Adding a new skill eval

1. Create `evals/<skill-name>/evals.json` with prompts and assertions.
2. That's it — no new `run_evals.py` or `.env.example` needed. Run it with: `uv run run_evals.py <skill-name> --both` from `evals/`.

Pass `--tag <name>` (repeatable) to attach skill-specific Langfuse tags for a run, e.g. `--tag eligibility --tag participant-group`.

### Eval file structure

Every entry in `evals.json` has three fields:

| Field             | Purpose                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `prompt`          | A realistic, natural-language user request                                                               |
| `expected_output` | A prose description of correct agent behaviour, grounding filter_ids and values against the real catalog |
| `assertions`      | A list of strings, each passed as a prompt to an LLM-as-judge                                            |

Optional file attachments can also be declared on any eval case:

| Field   | Purpose                                                                 |
| ------- | ----------------------------------------------------------------------- |
| `files` | Optional list of `{ "path": "...", "role": "..." }` fixture attachments |

Example:

```json
"files": [
  { "path": "fixtures/dummy_spec.md", "role": "context" },
  { "path": "fixtures/responses-dataset.csv", "role": "dataset" }
]
```

`role` is optional prompt metadata. Attachments are uploaded with
`LangfuseMedia` on dataset sync and materialized into the agent working
directory at run time via `LangfuseMediaReference.fetch_bytes()`
(`evals/_shared/media.py`). Requires `langfuse>=4.10.0`. Skills without
`files` are unchanged.

Example:

```json
{
  "id": 1,
  "prompt": "I want to study online learning habits among working-age adults in the UK who hold at least a university degree",
  "expected_output": "The agent fetches the filter list, recommends a UK country of residence filter (using current-country-of-residence or uk-country-of-residence), an education level filter targeting university-degree holders or above (choices 4, 5, or 6 in highest-education-level-completed), and an age filter for working-age adults (e.g. 18–65 using the age filter). Each recommendation includes the filter_id and selected values.",
  "assertions": [
    "The agent runs 'prolific filters' before making any recommendations",
    "The agent recommends a filter targeting UK-based participants and provides its filter_id",
    "The agent recommends an education filter targeting university degree level or above and provides its filter_id",
    "The agent recommends an age filter for working-age adults (e.g. lower bound 18, upper bound 65) and provides its filter_id",
    "The agent provides filter_id values for every filter it recommends",
    "The agent formats at least one recommendation with selected_values or selected_range in the Prolific API JSON structure"
  ]
}
```

## Running

### First-time setup

Sign up for [Langfuse](https://cloud.langfuse.com/) and create a project. Then copy `.env.example` to `.env` in `evals/` (shared by every skill's evals) and set:

- `ANTHROPIC_API_KEY`
- `PROLIFIC_TEST_TOKEN`
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`
- `LANGFUSE_USER_ID` (optional — attributes traces to your Langfuse user)

### Run

```bash
cd evals

uv run run_evals.py recommend-study-filters           # with skill (default)
uv run run_evals.py recommend-study-filters --without-skill
uv run run_evals.py recommend-study-filters --both    # A/B comparison
uv run run_evals.py recommend-study-filters --max-turns 15
```
