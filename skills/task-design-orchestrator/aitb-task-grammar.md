# AI Task Builder task grammar

The shared grammar every task type is built from. The orchestrator and all task-type
sub-skills assemble the same objects: a dataset schema, `task_details`, and a
`batch_items` layout. A task type is a particular arrangement of these, not a
different mechanism.

Read this once. Sub-skills should reference it rather than restate it.

## Contents
1. Batch vs Collection
2. Dataset schema (V4)
3. Blinding via metadata
4. Task grouping
5. task_details (shown once)
6. batch_items layout
7. Item types
8. Constraints and validation
9. Lifecycle and the no-edit-after-setup rule
10. Transport (CLI and API)
11. Study link fields

---

## 1. Batch vs Collection

Two modes, set on the study by `data_collection_method`:

- `AI_TASK_BUILDER_BATCH`: the researcher provides data, participants evaluate it.
  Datapoints are distributed across participants by Taskflow. This is the eval and
  annotation path, and the only one this orchestrator builds.
- `AI_TASK_BUILDER_COLLECTION`: participants produce original data. Same flow for all
  participants, page based. Out of scope here.

If the input resolves to a collection, stop and route to the collection path, not to
this orchestrator's sub-skills.

## 2. Dataset schema (V4)

The dataset is created and owned by Skill 2. The orchestrator consumes a ready
`dataset_id` and reads its schema. Schema fields are typed:

- `text`: shown to the participant.
- `image_url`: shown to the participant (must resolve to a public HTTPS URL).
- `metadata`: not shown. Holds anything the participant must not see.
- `task_group_id`: not shown. Groups datapoints into one submission.

Only `text` and `image_url` can be placed on screen. `metadata` and `task_group_id`
are rejected if referenced in the layout.

## 3. Blinding via metadata

Blinding is a dataset decision, not a layout one. To hide which system produced
which response in a comparison, the true model identity for each side is stored in
`metadata` fields, so it is never displayable. Position randomisation (which side is
A and which is B) is also handled in the dataset by Skill 2, with the true mapping
kept in `metadata`. The orchestrator does not shuffle anything at layout time,
because a layout is fixed per page.

## 4. Task grouping

A submission can cover more than one datapoint. Two ways to control this:

- A `task_group_id` field in the schema groups datapoints with the same value into
  one submission. Takes precedence when present.
- Otherwise `tasks_per_group` set at setup assigns that many datapoints per
  submission at random.

`tasks_per_group` is the number of datapoints a participant sees in one sitting, and
that sitting is one Prolific submission.

## 5. task_details (shown once)

Set at batch creation:

- `task_name`: internal name of the task.
- `task_introduction`: HTML, basic tags only.
- `task_steps`: HTML, basic tags only.

`task_details` is the batch-level content that sits outside the per-datapoint loop.
Onboarding belongs here (and, if larger, in the study description owned by Skill 6),
not in `batch_items`, because a `batch_items` page repeats once per datapoint. Whether
`task_details` renders once per submission or once per datapoint under grouping is not
stated in the docs and should be confirmed by a small test before relying on it.

## 6. batch_items layout

`batch_items` is the participant screen. It is a four level nested structure:

```
batch_items = Page[]
Page        = { rows: Row[] }
Row         = { columns: Column[] }   // 1 to 2 columns
Column      = { items: ColumnItem[] }
```

- A page repeats once per datapoint.
- A row stacks down the screen.
- A column sits across the row, maximum two per row.
- An item renders top to bottom within its column.

Always define instructions inline in `batch_items`. The standalone instructions
endpoint is legacy and is rejected once `batch_items` is set.

## 7. Item types

Three categories.

**Dataset field.** Pulls a schema value onto the screen.
```json
{ "type": "dataset_field", "field": "response_a" }
```
`field` must match a `text` or `image_url` schema field exactly (case sensitive).

**Content blocks (display only).**
```json
{ "type": "rich_text", "content": "<p>Rate for accuracy.</p>", "content_format": "html" }
{ "type": "image", "url": "https://.../ref.png", "alt_text": "Reference", "caption": "Fig 1" }
```
`content_format` is `html` (default) or `markdown`. Image `url` must be HTTPS.

**Inputs (questions).** Supported types:
- `free_text` (optional `helper_text`)
- `free_text_with_unit`
- `multiple_choice` (`description`, `answer_limit`, `options` as `{label, value}` pairs)
- `multiple_choice_with_free_text`
- `file_upload`

```json
{
  "type": "multiple_choice",
  "description": "Which response is more accurate?",
  "answer_limit": 1,
  "options": [
    { "label": "Response A", "value": "a" },
    { "label": "Response B", "value": "b" },
    { "label": "Tie",        "value": "tie" }
  ]
}
```

Audio and video stimuli are on the roadmap and will arrive as new item types without
breaking existing layouts, so treat modality as an axis, not a fixed set.

## 8. Constraints and validation

Structural:
- Maximum two columns per row.
- Each page needs at least one row, each row at least one column, each column at
  least one item.
- No limit on rows or on items in a column.

Dataset fields:
- `field` must match a `text` or `image_url` schema field.
- `metadata` and `task_group_id` fields are rejected.
- The same `field` may not appear more than once on a page.

The API validates at batch create and update, and rejects an invalid layout with a
`422` that names the offending `page`, `row`, `column`, and `item` by zero-based
index. Pre-check these rules before submitting so failures are caught early, then
rely on the CLI or API validation as the backstop.

## 9. Lifecycle and the no-edit-after-setup rule

Order: create the batch (with `task_details` and `batch_items`), then set it up with
grouping, then poll status to `READY`. Datasets and batches move through
`UNINITIALISED`, `PROCESSING`, `READY`, or `ERROR`. Do not attach a batch to a study
until it is `READY`.

Once a batch has been set up you can no longer edit its instructions. Any task change
after setup means a fresh batch (duplicate settings only, then a new dataset if
needed). This is why the preview and feedback loop in Skill 3c has to act before
setup, or accept a rebuild.

## 10. Transport (CLI and API)

Default transport is the Prolific CLI. The exact `batch` subcommands and flags must
be confirmed against `prolific batch --help` before first run, since the published
command list has lagged behind the binary. The CLI wraps these API endpoints, which
are the source of truth for the payload shape:

- Create batch: `POST /api/v1/data-collection/batches` (body: `name`, `workspace_id`,
  `dataset_id`, `task_details`, `batch_items`).
- Set up batch: `POST /api/v1/data-collection/batches/{batch_id}/setup`
  (body: `tasks_per_group`).
- Batch status: `GET /api/v1/data-collection/batches/{batch_id}/status`.

Dataset creation and upload endpoints are Skill 2's responsibility.

## 11. Study link fields

Skill 6 creates and publishes the study. The orchestrator only produces the values it
needs:

- `data_collection_method`: `AI_TASK_BUILDER_BATCH`.
- `data_collection_id`: the batch id.
- `data_collection_metadata.annotators_per_task`: how many participants annotate each
  datapoint. Can be increased after publish but not decreased, and increasing it
  raises total places.

`total_available_places` is calculated from the batch, so the orchestrator does not
set it.
