---
name: batch-task-create
description: Creates a Prolific AI Task Builder batch from a researcher-provided dataset by generating the dataset schema, building the `batch_items` layout, and executing the CLI workflow. Use when a researcher wants participants to evaluate or annotate their own data (text, image, audio or video). Stops at a set-up, previewable batch and does not create a study.
version: 0.1.0
---

## Create Batch From Dataset

When a researcher wants to create a Prolific batch from a dataset, do the work end to end: inspect the dataset, create the schema, create the `batch_items` layout, and use the Prolific CLI to create the dataset and batch whenever the environment allows it.

Do **not** stop at generic advice if you can create the files and run the commands directly.

### Scope

This skill ends with a batch that is set up and can be previewed. Do **not** create or publish a study: that spends money and is a separate step the researcher asks for explicitly.

### Prerequisites

- The Prolific CLI is installed (`prolific --version`).
- `PROLIFIC_TOKEN` is set (`prolific whoami` confirms it). Never print or echo the token. If it is missing, say so and stop.

### Bundled references

This skill includes its own local examples so it does not depend on the Prolific CLI repo:

- `examples/audio-comparison-dataset-schema.json`
- `examples/audio-comparison-batch-items.json`

Use them as grounding for schema structure and `batch_items` structure.

### Step 1: Inspect the CLI commands first

Mandatory: inspect the relevant CLI help before acting so flags and required inputs are correct.

```bash
prolific aitaskbuilder dataset create --help
prolific aitaskbuilder dataset upload --help
prolific aitaskbuilder batch create --help
```

If you need to preview or iterate on the layout, also inspect:

```bash
prolific aitaskbuilder batch setup --help
prolific aitaskbuilder batch preview --help
prolific aitaskbuilder batch update --help
```

### Step 2: Gather the minimum required inputs

You need enough information to create both the dataset and the batch:

- **Dataset file** — usually CSV or JSONL
- **Workspace ID**
- **Dataset name**
- **Batch name**
- **Task name**
- **Task introduction**
- **Task steps**
- **Participant experience goal** — what the participant should see and answer

If a value is missing but can be drafted safely from the user’s request, draft it. If the missing value changes the structure materially, ask for clarification.

Do **not** guess a workspace ID.

### Step 3: Inspect the dataset and create the schema

Read a few lines from the dataset file and infer the schema from its fields and sample values. The dataset file might be big, so do not read the whole file if you can sample it.

Use these field types:

- **`text`** — prompts, transcripts, instructions, titles, descriptions, plain values shown to participants
- **`image_url`** — image URLs rendered to participants
- **`audio_url`** — audio URLs used in audio-review layouts
- **`video_url`** — video URLs used in video-review layouts
- **`metadata`** — internal fields that should travel with the data but are not shown directly
- **`task_group_id`** — only when the researcher needs rows grouped into the same participant task

Guidelines:

- Reuse the exact dataset column names; do not rename fields casually
- Prefer **`strict: true`** for curated datasets unless the researcher clearly needs partially populated records
- Use **`metadata`** for bookkeeping fields that should not appear in the participant layout
- Add **`label`** values when they improve readability

With `strict: true` every record must carry every declared field, and undeclared fields are rejected.

Create the dataset **with** the schema (`--schema`). A dataset created without one stalls in `pending_schema` and imports nothing.

If the dataset is CSV with long text, commas, line breaks or `|` characters, convert it to JSONL first (one JSON object per line). In testing, a schema-first CSV with long text containing such characters was parsed with the whole header line as a single field and every row was rejected (cause not confirmed); the same data as JSONL imported cleanly. For `dataset upload`, let the CLI detect the format from the file extension; do not pass `--format jsonl`, which led to a doubled extension and a failed request.

Create a local schema file such as:

```bash
dataset-schema.json
```

### Step 4: Design the participant layout and create batch_items

Build `batch_items` as a **non-empty JSON array** of pages:

1. **Pages** — one participant screen each
2. **Rows** — vertical sections on the page
3. **Columns** — one or two columns per row
4. **Items** — content, dataset references, or response inputs

Common item types:

- **`rich_text`**
- **`image`**
- **`dataset_field`**
- **`free_text`**
- **`free_text_with_unit`**
- **`multiple_choice`**
- **`multiple_choice_with_free_text`**

Layout heuristics:

- Use **one column** for simple linear tasks
- Use **two columns** for direct comparisons
- Put **instructions first**
- Then place the current datapoint content
- Then place the response inputs nearest to the content they refer to
- No need for separate title/label items for the dataset fields. The layout already shows the field label and value, so extra labels are redundant.

Layout rules that are easy to get wrong:

- Set `"disable_dropdown": true` on every `multiple_choice`. Without it, a short list can still render as a dropdown instead of radio buttons.
- Free-text boxes are **required** unless the item has `"optional": true`, even if the question text says "(optional)".
- Instruction items take `description` for the question text and `helper_text` for guidance. They have no `title` field, and `order` must not be set because position in the layout sets the order.
- Both columns in a row take the height of the taller one, which leaves blank space under the shorter. Pair items of similar length, and use one column for pages with long text.
- A dataset field can appear only once per page, and `metadata` fields cannot be placed in the layout at all.
- A page with `"display_position": "intro"` or `"outro"` renders once instead of once per row, and may contain only `rich_text` or `image` items.
- `rich_text` accepts markdown or basic HTML. Do not use `style` attributes; the API rejects them. A markdown table needs a blank line before it.
- Define questions inline in `batch_items`. Do not add instructions with the separate `batch instructions` command; that endpoint is deprecated for batches that use `batch_items`.

For batch task layouts, use `examples/audio-comparison-batch-items.json` as the example json file
Create a local layout file such as:

```bash
batch-items.json
```

### Step 5: Execute the CLI workflow

Unless blocked by missing credentials, missing required user input, or an unavailable CLI, perform the workflow with the CLI instead of only describing it.

Typical command sequence:

```bash
prolific aitaskbuilder dataset create -n "<dataset_name>" -w <workspace_id> --schema dataset-schema.json
prolific aitaskbuilder dataset upload -d "<dataset_id>" -f "<dataset_file>"
prolific aitaskbuilder batch create -n "<batch_name>" -w <workspace_id> -d "<dataset_id>" --task-name "<task_name>" --task-introduction "<task_introduction>" --task-steps "<task_steps>" --batch-items-file batch-items.json
```

Capture and reuse the IDs returned by the CLI.

After `dataset upload`, read the printed `Accepted` and `Rejected` counts. Stop and fix the data or schema if `Rejected` is not 0 or `Accepted` does not match the row count. Do not create the batch on a partly imported dataset.

`batch create` requires `--task-name`, `--task-introduction` and `--task-steps`. The introduction and steps accept basic HTML. Quote them carefully, since apostrophes and double quotes inside the value break the shell command.

Set up the task structure — group the dataset rows into participant tasks with `--tasks-per-group`. One group is one submission for a participant, so choose it from how long a group should take. The default is 1. Setup needs rows in the dataset, runs once per batch, and cannot be repeated.

```bash
prolific aitaskbuilder batch setup -b "<batch_id>" -d "<dataset_id>" --tasks-per-group <n>
```

If the researcher wants to inspect the participant experience before attaching the batch to a study, preview it:

```bash
prolific aitaskbuilder batch preview "<batch_id>"
```

Preview needs a set-up batch. To change the layout or task text after setup, use `prolific aitaskbuilder batch update` with a new `batch_items` file or new task details; this works on a batch that is already set up, so a new batch is not needed. Re-run the preview afterwards.

Note: the help text for `batch setup` says instructions must be added first. That describes the older layout-less flow. With `batch_items`, the questions are already part of the layout.

### Step 6: Recover from schema or layout validation failures

If dataset creation, upload, or batch creation fails, fix the concrete problem and retry when appropriate.

Pay special attention to:

- schema field types that do not match the dataset content
- missing required schema fields in strict mode
- invalid URL media fields
- malformed `batch_items`
- `multiple_choice.answer_limit` exceeding the number of options
- bad `dataset_field` references
- a `dataset_field` that points at a `metadata` field, or the same field used twice on one page
- a dataset stuck in `pending_schema` (created without a schema) or an import reported as `partial` (check the rejected count and errors)
- `batch create` returning 400 because the task introduction or steps are missing
- `batch setup` returning 400 because the dataset has no rows
- a `403 Forbidden` on `batch create` or `batch update` after adding `rich_text`: remove any `style` attributes

If the API returns `INVALID_BATCH_ITEMS`, use the reported page / row / column / item location to correct the failing element precisely.

### Step 7: Deliver the result clearly

Your final output should include:

1. The created **dataset schema**
2. The created **`batch_items` JSON**
3. The important created resource IDs if the CLI commands succeeded
4. A short plain-language explanation of the participant layout
5. Which dataset fields participants see and which are hidden (`metadata`). Hidden fields are not shown to participants but stay in the dataset, report and export, so they are not a place for secrets.
6. The preview command, and that no study has been created

If execution was blocked, say exactly what is missing or what failed. Do not pretend the dataset or batch was created if it was not.
