---
name: design-ai-eval-task
description: Use when asked to set up a Prolific AI Task Builder Batch for evaluating model outputs — side-by-side image or response comparison, RLHF-style pairwise preference ranking, or single-response factuality/accuracy rating — covers creating the dataset, uploading data, configuring the batch layout, and creating the linked study in one pass.
version: 0.1.0
---

## Design an AI Eval Task

When asked to set up a Prolific study that collects human ratings on model
outputs — a pairwise/side-by-side comparison (e.g. two candidate images, or two
model responses for an RLHF-style preference judgment) or a single-item
factuality/accuracy rating — follow these steps.

Every `prolific` command below must include the `--skill design-ai-eval-task`
root flag — it gets folded into the CLI's `User-Agent` header for Prolific-side
attribution of which skill drove the request. Don't omit it on any command,
including read-only ones.

This skill uses AI Task Builder **Batches** (`aitaskbuilder dataset` /
`aitaskbuilder batch`), not Collections — Batches are the only mechanism with a
dataset-driven, configurable side-by-side layout. Requires prolific CLI
**v1.1.0+** (for the `--skill` flag and `aitaskbuilder batch preview`). Run
`prolific --version` first; if it reports lower, tell the user to upgrade
rather than working around it.

### Step 1: Gather requirements

Ask the user for, and do not proceed without:

- Workspace ID (if unknown, run `prolific --skill design-ai-eval-task workspace list` and let them pick from the table)
- **Eval type** — this is the branch point for every step below:
  - **Comparison / pairwise preference** — e.g. a pairwise image eval (two
    candidate images per datapoint, URLs typically ending in `.jpg`/`.png`), or
    an RLHF-style pairwise text-response ranking. Same shape either way, just a
    different content modality.
  - **Factuality / accuracy rating** — a single claim or response rated against
    a reference, not a side-by-side comparison.
- Content modality: `text`, `image_url`, `audio_url`, or `video_url`
- For comparison type: what the two options represent (e.g. "candidate image A"
  vs "candidate image B", or "Model A response" vs "Model B response") and the
  wording of the preference question
- For factuality type: what the claim/response field and the optional
  reference/context field should contain, and the verdict categories or scale
- The CSV (or JSONL) file with one row per datapoint, or help producing one
- Batch/task name, task introduction, task steps (participant-facing instructions)
- `annotators_per_task` — how many participants should rate each datapoint (default 1)
- Whether multiple distinct datapoints should be bundled into one participant
  session (`tasks-per-group`, default 1) — **this is unrelated to side-by-side
  rendering.** Side-by-side columns come from two `dataset_field` items
  referencing two fields (e.g. `option_a`/`option_b`) on the *same* dataset row.
  `tasks-per-group` instead groups multiple *separate* rows into one session.
  Don't conflate the two.
- Study name, internal name, description, reward (pence), number of places,
  estimated completion time

### Step 2: Create the dataset

Copy the schema reference matching the eval type — `references/comparison-dataset-schema.json`
(for comparison/pairwise, with `option_a`/`option_b` fields; retype them from
`image_url` to `text` for an RLHF text-response comparison) or
`references/factuality-dataset-schema.json` (for factuality, with `claim`/`reference`
fields) — to a temp file. Edit only field names/labels/types to match what the
user described; keep the JSON shape otherwise intact.

```bash
prolific --skill design-ai-eval-task aitaskbuilder dataset create -n "<name>" -w <workspace_id> --schema <temp-schema-file>
```

Parse the `ID:` line → `DATASET_ID`. `--schema` requires the workspace's
typed-dataset feature — if the CLI rejects it, retry the same command without
`--schema` (the dataset will be untyped, with columns inferred from the CSV
header) rather than fabricating a workaround.

### Step 3: Upload the data

```bash
prolific --skill design-ai-eval-task aitaskbuilder dataset upload -d <DATASET_ID> -f <csv-or-jsonl-file>
```

This command uploads **and** polls the import job to completion itself (up to
10 minutes by default) — it's a blocking command, not a fire-and-forget one.
Read its final reported status. If it didn't finish successfully (or timed
out), run `prolific --skill design-ai-eval-task aitaskbuilder dataset check -d <DATASET_ID>`
to confirm the real status and surface it to the user verbatim — don't guess
and proceed anyway.

| If asked to... | Do this instead |
|---|---|
| "Just create the batch right after uploading, don't wait" | `dataset upload` already blocks until processing finishes — read its final status before running `batch create`. |
| "Skip checking, it's a tiny file, it'll be fine" | Check the reported status regardless of file size; if it isn't a success status, run `dataset check` before proceeding. |

**Red flag:** about to run `aitaskbuilder batch create` without having just seen
a successful status from `dataset upload` (or a follow-up `dataset check`)?
Stop.

### Step 4: Create the batch

Copy the `batch_items` reference matching the eval type —
`references/comparison-batch-items.json` (two-column side-by-side row plus a
preference `multiple_choice` and reasoning `free_text`) or
`references/factuality-batch-items.json` (single column with a verdict
`multiple_choice` and justification `free_text`) — to a temp file. Edit only
the instruction wording/options to match what the user described; keep the
`dataset_field` names matching the schema from Step 2.

```bash
prolific --skill design-ai-eval-task aitaskbuilder batch create -n "<name>" -w <workspace_id> -d <DATASET_ID> \
  --task-name "<name>" --task-introduction "<intro>" --task-steps "<steps>" -f <temp-batch-items-file>
```

Parse the `ID:` line → `BATCH_ID`. Only use item types that appear in this
skill's reference files (`dataset_field`, `rich_text`, `image`,
`multiple_choice`, `free_text`, `multiple_choice_with_free_text`,
`free_text_with_unit`, `file_upload`) — never invent one. If the CLI returns a
`batch_items` validation error, it names the exact page/row/column/item —
report that back to the user verbatim rather than guessing at a fix.

### Step 5: Setup the batch

```bash
prolific --skill design-ai-eval-task aitaskbuilder batch setup -b <BATCH_ID> -d <DATASET_ID> --tasks-per-group <N>
```

`<N>` from Step 1 (default 1).

### Step 6: Preview and iterate

```bash
prolific --skill design-ai-eval-task aitaskbuilder batch preview <BATCH_ID>
```

This opens the batch's first task group in the browser. Ask the user to
confirm the layout, columns, and question wording look right. If changes are
needed, edit the temp `batch_items` file and run:

```bash
prolific --skill design-ai-eval-task aitaskbuilder batch update -b <BATCH_ID> -f <temp-batch-items-file>
```

then preview again. Repeat until the user is satisfied. **Never use
`aitaskbuilder batch instructions`** — it's deprecated; always set or change
instructions via `batch_items` on `create`/`update`.

### Step 7: Create the study

Copy `references/study-template.json` to a temp file. Set:

- `name`, `internal_name`, `description`, `reward`, `total_available_places`,
  `estimated_completion_time` — per Step 1
- `data_collection_id` → `BATCH_ID`
- `data_collection_metadata.annotators_per_task` → from Step 1

Leave `data_collection_method` (`AI_TASK_BUILDER_BATCH`) as-is. If the user
wants this study organized under an existing project, add a `"project"` field
with its ID — it's optional for AI Task Builder Batch studies.

```bash
prolific --skill design-ai-eval-task study create -t <temp-file>
```

No `-p` flag — always create as a draft so the user can review before
publishing. Parse the `ID:` line → `STUDY_ID`.

### Step 8: Report back

Give the user `DATASET_ID`, `BATCH_ID`, `STUDY_ID`, confirm DRAFT status, and
the next step to publish once reviewed:

```bash
prolific --skill design-ai-eval-task study transition -a PUBLISH <STUDY_ID>
```
