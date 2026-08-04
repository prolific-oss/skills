---
name: batch-task-create
description: Creates a Prolific AI Task Builder batch from a researcher-provided dataset by generating the dataset schema, building the `batch_items` layout, and executing the CLI workflow.
version: 0.1.0
---

## Create Batch From Dataset

When a researcher wants to create a Prolific batch from a dataset, do the work end to end: inspect the dataset, create the schema, create the `batch_items` layout, and use the Prolific CLI to create the dataset and batch whenever the environment allows it.

Do **not** stop at generic advice if you can create the files and run the commands directly.

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

Set up the task structure — group the dataset rows into participant tasks with `--tasks-per-group`:

```bash
prolific aitaskbuilder batch setup -b "<batch_id>" -d "<dataset_id>" --tasks-per-group <n>
```

If the researcher wants to inspect the participant experience before attaching the batch to a study, preview it:

```bash
prolific aitaskbuilder batch preview "<batch_id>"
```

### Step 6: Recover from schema or layout validation failures

If dataset creation, upload, or batch creation fails, fix the concrete problem and retry when appropriate.

Pay special attention to:

- schema field types that do not match the dataset content
- missing required schema fields in strict mode
- invalid URL media fields
- malformed `batch_items`
- `multiple_choice.answer_limit` exceeding the number of options
- bad `dataset_field` references

If the API returns `INVALID_BATCH_ITEMS`, use the reported page / row / column / item location to correct the failing element precisely.

### Step 7: Deliver the result clearly

Your final output should include:

1. The created **dataset schema**
2. The created **`batch_items` JSON**
3. The important created resource IDs if the CLI commands succeeded
4. A short plain-language explanation of the participant layout

If execution was blocked, say exactly what is missing or what failed. Do not pretend the dataset or batch was created if it was not.
