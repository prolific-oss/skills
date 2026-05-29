# Skill Evals

Evals measure whether a skill actually improves agent behaviour. Each skill's eval runs the same prompts **with** and **without** the skill injected, then scores the outputs — giving you evidence of whether the skill is pulling its weight.

## Structure

```
evals/
├── pyproject.toml                   # shared dependencies (uv)
├── _cache/                          # downloaded Prolific CLI binaries (gitignored)
├── _shared/
│   ├── sandbox.py                   # downloads the Prolific CLI binary; builds the agent's env
│   ├── runner.py                    # wraps Claude Agent SDK for a single eval item
│   └── judge.py                     # LLM-as-judge: grades assertions against agent output
└── recommend-study-filters/
    ├── evals.json                   # the eval dataset (prompts + assertions)
    ├── run_evals.py                  # entry point — wires everything together
    └── .env                         # credentials (gitignored; copy from .env.example)
```

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
2. Create `evals/<skill-name>/run_evals.py` — copy `recommend-study-filters/run_evals.py` as a template and update `SKILL_PATH` (point at `skills/<skill-name>/SKILL.md`) and `EVALS_PATH`.
3. Add a `.env.example` alongside it (copy and adjust the existing one).
4. Run with: `uv run <skill-name>/run_evals.py --both` from `evals/`.

### Eval file structure

Every entry in `evals.json` has three fields:

| Field             | Purpose                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `prompt`          | A realistic, natural-language user request                                                               |
| `expected_output` | A prose description of correct agent behaviour, grounding filter_ids and values against the real catalog |
| `assertions`      | A list of strings, each passed as a prompt to an LLM-as-judge                                            |

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

Sign up for [Langfuse](https://cloud.langfuse.com/) and create a project. Then copy `.env.example` to `.env` in `evals/recommend-study-filters/` and set:

- `ANTHROPIC_API_KEY`
- `PROLIFIC_TEST_TOKEN`
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`
- `LANGFUSE_USER_ID` (optional — attributes traces to your Langfuse user)

### Run

```bash
cd evals

uv run recommend-study-filters/run_evals.py           # with skill (default)
uv run recommend-study-filters/run_evals.py --without-skill
uv run recommend-study-filters/run_evals.py --both    # A/B comparison
uv run recommend-study-filters/run_evals.py --max-turns 15
```
