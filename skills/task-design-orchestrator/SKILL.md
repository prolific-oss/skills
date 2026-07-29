---
name: task-design-orchestrator
description: Turn a study's goal and dataset into a runnable AI Task Builder task on Prolific, then create the batch via the Prolific CLI. This is the Skill 3 orchestrator. Use it whenever the workflow needs to build the task for an evaluation or annotation study, route to a task-type sub-skill (side-by-side preference, rubric, classification, free-text response), assemble a batch_items layout and task_details, or produce annotators_per_task for the study step. Use it even when the request only says "build the task", "set up the eval", "design the annotation", or names a task type, as long as the target is an AI Task Builder batch.
---

# Task Design Orchestrator (Skill 3)

Turn a study's context into a runnable AI Task Builder batch. This skill does not
design any single task type itself. It reads the context, routes to the right
task-type sub-skill, assembles the batch from the shared grammar, creates it via the
Prolific CLI, and hands it to Skill 3c for preview and feedback.

Every eval task type is the same object: a dataset schema, `task_details`, and a
`batch_items` layout. Two shared references are the single home for the detail, so the
sub-skills do not restate it. Read both before building:
- `references/aitb-task-grammar.md`: how a task is expressed in AI Task Builder.
- `references/eval-methodology.md`: how to run an eval soundly (rater count, order and
  position bias, ties, gold items, aggregation, agreement). Grounded in how text-to-
  image and LLM evals are actually run. Pass the relevant defaults to sub-skills and
  downstream skills.

## What this skill does and does not do

Does:
- Resolve the task type and route to the matching sub-skill.
- Validate the dataset schema against what the task type needs.
- Get onboarding content and task length from Skill 3b, and write `task_details`.
- Assemble the full batch (`task_details` plus the sub-skill's `batch_items`).
- Pre-validate the layout, then create and set up the batch via the CLI.
- Output `annotators_per_task` and the batch reference, and hand to Skill 3c.

Does not:
- Create or edit the dataset. Skill 2 owns the dataset, its schema, blinding via
  metadata, position randomisation, and image hosting. Consume a ready `dataset_id`.
- Design the layout for a specific task type. The sub-skill does that.
- Create or publish the study. Skill 6 does that, using `annotators_per_task`.
- Author onboarding content from scratch. Skill 3b supplies it.

## Input contract

Skill 1 does not exist yet, so this skill declares its own input. Treat this as the
interim contract that Skill 1 will fill later. Required unless marked optional.

- `task_type`: one of `pairwise_preference`, `rubric`, `classification`,
  `free_text_response`. Fixed set. Routes to a sub-skill.
- `modality`: `text` or `image`. A parameter to the sub-skill, not a separate skill.
- `objective`: plain-language goal of the evaluation.
- `dataset_id`: from Skill 2, must be `READY`.
- `dataset_schema`: the field names and types, so fields can be validated and
  referenced by name.
- `criteria` (rubric): each with a name, a scale, and anchors. Optional for other
  types.
- `dimensions` (optional): evaluation dimensions such as factuality. Passed to the
  sub-skill as config. A dimension is what is judged, not a layout, so it does not
  change the routing.
- `answer_options` and `tie_allowed` (pairwise, classification): the choice set.
- `blinding` (optional, default true for pairwise): model identity hidden. Enforced
  by Skill 2 through metadata fields, checked here.
- `tasks_per_group`: datapoints per submission. Default 1.
- `annotators_per_task`: participants per datapoint. Default 1.
- `gold_subset` (optional): reference items for quality checks.

If a required field is missing or `dataset_id` is not `READY`, stop and loop back to
the user rather than guessing a value.

## Workflow

1. **Resolve the fork.** Confirm the target is an `AI_TASK_BUILDER_BATCH`. If the
   context resolves to a collection, stop and route to the collection path.

2. **Route.** Map `task_type` to its sub-skill (see Routing). Load that sub-skill.

3. **Validate the dataset schema against the task type.** Confirm the fields the task
   type needs exist with the right types (for example a pairwise text eval needs two
   `text` fields for the two responses, an image eval needs `image_url` fields). For
   image modality, confirm the `image_url` fields resolve to public HTTPS URLs. If the
   schema does not match, stop and loop back to the user, naming the missing or
   wrong-typed fields, since Skill 2 owns the fix.

4. **Get onboarding and task length from Skill 3b.** Pass the task type, criteria, and
   modality. Skill 3b returns onboarding content and an estimated task length. Keep
   onboarding in `task_details`, not in `batch_items`, because a `batch_items` page
   repeats per datapoint.

5. **Get the layout from the sub-skill.** Pass the resolved input (fields, criteria,
   dimensions, options, blinding, modality). The sub-skill returns a `batch_items`
   fragment plus any layout-level notes. The orchestrator owns the final assembly.

6. **Assemble the batch.** Combine `task_details` (from step 4) and `batch_items`
   (from step 5), referencing `dataset_id`. Do not reference `metadata` or
   `task_group_id` fields on screen.

7. **Pre-validate.** Check the grammar rules before submitting: two columns per row
   maximum, every `dataset_field` matches a `text` or `image_url` schema field, no
   field repeated on a page, every level non-empty. Catching these here makes the
   `422` a backstop rather than the first line of defence.

8. **Create and set up the batch via the CLI.** Create the batch with `task_details`
   and `batch_items` against `dataset_id`, then set it up with `tasks_per_group`, then
   poll status until `READY`. Confirm the exact `batch` subcommands and flags against
   `prolific batch --help` first. See Transport.

9. **On failure, loop back to the user.** If the CLI rejects the layout or a
   precondition fails, surface the specific issue and stop. Do not silently retry with
   altered content.

10. **Output and hand off.** Emit `annotators_per_task` for Skill 6, and the batch
    reference and preview link for Skill 3c. Do not create the study and do not add a
    human approval gate before creation. The batch is created and handed straight to
    Skill 3c.

## Routing

| `task_type`          | Sub-skill                        | Shape |
| -------------------- | -------------------------------- | ----- |
| `pairwise_preference`| `side-by-side-image-comparison`  | Two stimuli in two columns, forced choice with optional tie, blinding, randomised position. v1 is image only (the built sub-skill). |
| `rubric`             | `rubric-eval`                    | Built. One stimulus, a stack of anchored scored inputs, one per criterion, binary preferred over Likert. Pointwise rating is the single-criterion case and folds in here. |
| `classification`     | `single-label-classification`    | To build. One stimulus, one choice. `multiple_choice` for single label, checkbox behaviour via `answer_limit` for multi label. |
| `free_text_response` | `free-text-response`             | To build. One stimulus plus `free_text`. Covers rewrite, critique, and open response. |

Modality is passed into the chosen sub-skill. v1 ships `side-by-side-image-comparison`
for the image case, since that is the first path being run end to end. A text pairwise
version is the same layout with the stimulus fields typed `text` instead of
`image_url`. The planned consolidation is a single pairwise sub-skill with modality as
a parameter, so audio and video do not each spawn a new skill. Until then, route
`pairwise_preference` to the image sub-skill.

Dimensions (factuality and similar) are passed to the sub-skill as config. If a
dimension needs heavy extra logic, such as source material on screen or per-claim
decomposition, it may later become a thin wrapper sub-skill over `rubric-eval` or
`single-label-classification`. Route on `task_type` regardless.

## Sub-skill contract

The orchestrator gives the sub-skill:
- Resolved input fields (schema field names, criteria, dimensions, options, blinding,
  modality).

The sub-skill returns:
- A `batch_items` fragment expressed in the grammar.
- Any field requirements it assumes (so the orchestrator can confirm them against the
  schema in step 3).
- Its quality notes for the task type (for example forced choice, tie handling, one
  anchored scale reused across criteria).

The sub-skill does not call the CLI, does not touch the dataset, and does not write
`task_details`. It only produces layout and design.

## Transport

Default transport is the Prolific CLI. The AITB `batch` commands exist in the current
binary but the published command list has lagged, so confirm the exact subcommands and
flags against `prolific batch --help` before first run.

The CLI wraps these endpoints, which define the payload the orchestrator assembles:
- Create batch: `POST /api/v1/data-collection/batches`
- Set up batch: `POST /api/v1/data-collection/batches/{batch_id}/setup`
- Batch status: `GET  /api/v1/data-collection/batches/{batch_id}/status`

See `references/aitb-task-grammar.md` section 10 for payload detail.

## Constraints to respect

- Onboarding goes in `task_details` and, if larger, in the study description handed to
  Skill 6. Not in `batch_items`, which repeats per datapoint.
- Blinding and position randomisation are dataset properties owned by Skill 2, carried
  in `metadata`. Never place `metadata` or `task_group_id` fields on screen.
- Instructions cannot be edited after setup. A task change after setup needs a fresh
  batch (duplicate settings). Skill 3c's feedback loop should act before setup.

## Definition of done

- The batch is created and validated (CLI or API).
- `annotators_per_task` is output for Skill 6.
- The batch reference and preview link are handed to Skill 3c.
