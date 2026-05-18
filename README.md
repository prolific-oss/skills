# Prolific Skills

Official skills from Prolific for AI workflows and research following the [agentskills.io](https://agentskills.io) specification.

Includes `prolific-beta-skills` plugin for skills that are currently being evaluated, but made available for experimentation and feedback.

## Installation

```bash
npx skills add prolific/skills
```

Or install individual skills:

```bash
# example prolific skill only
npx skills add prolific/skills --skill recommend-study-filters
```

## Documentation

- [Prolific Documentation](https://docs.prolific.com/documentation/get-started/overview)
- [API Reference](https://docs.prolific.com/api-reference/introduction)
- [Prolific CLI](https://docs.prolific.com/documentation/tooling/prolific-cli)

## Evals

In order to assure the performance of skills with a data driven approach, we co-locate and run evals for each skill. Each skill eval has a 'dataset' of eval parameters based on real world articulations from users of that skill.

These are:

- a prompt
- an expected output
- assertions that will themselves be passed as prompts to an LLMJ (LLM-as-judge) to gauge against failure modes.

We use Langfuse as the telemetry layer and platform for skill tracing, prompt management, and evaluation - but the eval parameters themselves are platform and tool agnostic.

Here is an example of an eval config:

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

## Running the Evals

Go to [Langfuse](https://cloud.langfuse.com/) and create an account. Langfuse also provides [skills](https://github.com/langfuse/skills).

Create a .env file in skills/evals/recommend-study-filters/ based on the .env.example and set:

- ANTHROPIC_API_KEY,
- PROLIFIC_TEST_TOKEN,
- LANGFUSE_SECRET_KEY
- LANGFUSE_PUBLIC_KEY
- LANGFUSE_BASE_URL

Then you can run the following to run the evals in different ways.

```
  cd skills/evals

  python recommend-study-filters/run_evals.py                 # with skill (default)
  python recommend-study-filters/run_evals.py --without-skill # baseline without skill
  python recommend-study-filters/run_evals.py --both          # both, side-by-side in Langfuse
  python recommend-study-filters/run_evals.py --max-turns 15  # override turn limit (default: 10)
```

---

## Writing Evals for Prolific Skills

This section is a guide to writing high-quality evals for skills in this repo

### The Eval Loop

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

---

### Eval File Structure

Each skill's evals are coloacted with the skill.

```
skills/
  recommend-study-filters.md     ← the skill
  evals/
    recommend-study-filters/
      evals.json                  ← eval dataset
      run_evals.py                ← eval runner
```

Every entry in `evals.json` has three fields:

| Field             | Purpose                                                                                                  |
| ----------------- | -------------------------------------------------------------------------------------------------------- |
| `prompt`          | A realistic, natural-language user request                                                               |
| `expected_output` | A prose description of correct agent behaviour, grounding filter_ids and values against the real catalog |
| `assertions`      | A list of strings, each passed as a prompt to an LLM-as-judge                                            |

---

## License

CC0 1.0 Universal

## Author

[Prolific](https://www.prolific.com/)
