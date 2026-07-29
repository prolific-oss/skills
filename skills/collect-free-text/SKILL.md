---
name: collect-free-text
description: Ask Prolific participants one or more open-ended questions and collect their free-text answers, then watch the responses arrive. Use when the user wants to "ask on Prolific", poll or survey N people a question, run a quick open-ended / free-text study, or gather written responses from real participants.
version: 0.3.0
---

## Collect Free-Text Data from Prolific

Turn a plain request like *"ask on Prolific to 100 people: who do you think is
going to win the world cup?"* into a live study that recruits real participants
and streams their written answers back.

This uses Prolific's **AI Task Builder Collection** flow through the Prolific
CLI: build a collection with a `free_text` question, create a study from it,
publish it to N participants, then export their responses.

> **Publishing spends real money.** A published study is paid for out of the
> workspace wallet (participant rewards **plus** Prolific's service fee). Never
> publish without the explicit confirmation in Step 5. When in doubt, stop at
> the draft.

If the `prolific` CLI is not installed or not authenticated, do **not** guess or
fabricate results. Tell the user and point them to set up the CLI (`prolific
--help` and the config at `$HOME/.config/prolific-oss/prolific.yaml`).

### Step 1: Ground yourself in the current CLI

Mandatory: the flags below can change between CLI versions, so read the help for
the two commands you will drive before building anything.

```bash
prolific collection create --help
prolific collection publish --help
```

### Step 2: Gather the parameters

From the user's request, pin down each of these. Ask only for what is missing —
infer sensible defaults for the rest and state them.

- **Question(s)** — the open-ended prompt(s) to ask. One is typical; a short
  list is fine.
- **Participants (N)** — how many people to recruit.
- **Estimated completion time** — minutes to answer. Default `1` for a single
  short question, `2` for a few.
- **Reward per participant** — in **integer cents** (USD) or pence (GBP).
  Respect Prolific's fair-pay rules:
  - **Minimum: £6 / $8 per hour.** Studies below this are flagged as
    *underpaying* and may be blocked.
  - **Recommended: £9 / $12 per hour or more** for better, faster data.
  - For a 1-minute task that is ~`$0.15` minimum, ~`$0.20` at the recommended
    rate. Default to the **recommended** rate, not the floor.

Resolve the **workspace** the study belongs to (its wallet pays for the study):

```bash
prolific workspace list
```

Use the workspace the user names; if there is more than one and they did not
say, ask which to use. Note its ID for the next step.

### Step 3: Create the collection

Write a collection definition to a temp JSON file, one `free_text` page item per
question, then create it.

```json
{
  "workspace_id": "<workspace-id>",
  "name": "<short study name>",
  "task_details": {
    "task_name": "<short study name>",
    "task_introduction": "<p>Thanks for taking part! Please answer the question below.</p>",
    "task_steps": "<ol><li>Read the question.</li><li>Type your answer.</li><li>Submit.</li></ol>"
  },
  "collection_items": [
    {
      "order": 0,
      "page_items": [
        { "order": 0, "type": "free_text", "description": "<the question>" }
      ]
    }
  ]
}
```

```bash
prolific collection create -t /tmp/prolific-collection.json
```

Capture the **collection ID** from the output — every later step needs it.

### Step 4: Create a DRAFT study (no spend)

Create the study from the collection but **do not publish yet**. Write a study
template so reward and completion time are explicit (not left to defaults), then
publish it in `--draft` status.

```json
{
  "name": "<short study name>",
  "description": "<p>Answer one quick question.</p>",
  "prolific_id_option": "not_required",
  "total_available_places": <N>,
  "estimated_completion_time": <minutes>,
  "reward": <cents>,
  "device_compatibility": ["desktop", "tablet", "mobile"],
  "completion_codes": [
    { "code": "<8-CHAR-CODE>", "code_type": "COMPLETED",
      "actions": [{ "action": "AUTOMATICALLY_APPROVE" }] }
  ]
}
```

```bash
prolific collection publish <collection-id> -t /tmp/prolific-study.json --draft
```

Capture the **study ID** from the output. (`collection publish` automatically
wires the collection into the study as `data_collection_id` with method
`AI_TASK_BUILDER_COLLECTION`.)

### Step 5: Verify the cost, then get explicit confirmation — MANDATORY

Before spending anything, inspect the draft exactly as Prolific will bill it:

```bash
prolific study view <study-id>
```

Confirm the `reward`, `estimated_completion_time`, `total_available_places`, and
that the study is **not** flagged as underpaying. Then present the cost to the
user in plain terms:

- **Participant payout** = `reward × N`.
- **Total charged** ≈ `reward × N × 1.4` — Prolific adds a service fee (~40%) on
  top of rewards; the exact figure is shown in `study view` / the dashboard.

Optionally let them preview the participant experience:

```bash
prolific collection preview <collection-id>   # opens in the browser
prolific study view <study-id> -W             # opens the draft study page
```

Ask the user to confirm they want to publish and spend. **Only proceed to Step 6
on an explicit yes.** If they decline, leave the draft in place — they can
publish it later from the dashboard or by re-running Step 6.

### Step 6: Publish (spends money)

```bash
prolific study transition <study-id> -a PUBLISH
```

The study is now live and participants can start submitting.

### Step 7: Watch the responses arrive

Poll progress — how many of the N places are filled, by submission status:

```bash
prolific study submission-counts <study-id> --json
prolific submission list -s <study-id> --json
```

To read the actual free-text answers, export the collection (an async ZIP the
CLI polls for and downloads):

```bash
prolific collection export <collection-id> -o /tmp/prolific-export.zip
```

Inside the archive:

- **`responses.jsonl`** — one record per submission. Each answer lives at
  `responses.<instruction_id>.value`, alongside `submission_id` and
  `participant_id`.
- **`collection.json`** — maps each `instruction_id` back to its question text.

Read `responses.jsonl`, map instruction IDs to questions via `collection.json`,
and present the answers clearly (a list, and/or a short themes summary). Re-run
the export to pull the latest as more responses land; the study keeps running on
Prolific until all places are filled. To keep refreshing on an interval, poll
`submission-counts` periodically and re-export when the count grows.

### Notes & guardrails

- **Money is real.** Never publish or transition to `PUBLISH` without the Step 5
  confirmation. Prefer leaving a draft over spending on assumptions.
- **Fair pay.** If the chosen reward implies an hourly rate below Prolific's
  minimum, warn the user and suggest raising it — Prolific may block an
  underpaying study.
- **Don't fabricate.** If a CLI command fails (not installed, not authenticated,
  no wallet funds), report the actual error and the fix; never invent a
  collection ID, study ID, or responses.
- **Targeting.** To restrict who can answer (country, age, etc.), combine this
  with the `recommend-study-filters` skill and add the resulting
  `eligibility_requirements` to the Step 4 study template.
