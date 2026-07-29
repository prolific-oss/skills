---
name: side-by-side-image-comparison
description: Build the batch_items layout for a side-by-side, two-image comparison in AI Task Builder, where a participant sees two images and judges them against one or more axes (prompt alignment, image quality, and similar). This is the Skill 3 image pairwise template, called by the task-design-orchestrator when task_type is pairwise_preference and modality is image. Use it whenever the task shows two images and asks the participant to choose between them, including image preference, image-quality A/B, prompt-alignment comparisons, and text-to-image model evaluation.
---

# Side-by-side image comparison (pairwise, image)

Produce the `batch_items` layout for a two-image comparison: show the participant two
images from the dataset and ask which one wins, on each judged axis. The orchestrator
calls this template, wraps the layout with `task_details`, and creates the batch. This
template only produces layout and design.

Read two references first if you have not:
- `../Task-design-orchestrator/references/aitb-task-grammar.md` for how the layout is
  expressed in AI Task Builder.
- `../Task-design-orchestrator/references/eval-methodology.md` for why the design below
  is shaped the way it is. This template is an application of section 2 of that file.

If the skills are moved, update these paths.

## Role and boundaries

Does:
- Return a `batch_items` fragment for the two-image comparison, one forced choice per
  judged axis, with an optional reason.
- State the dataset fields it assumes, so the orchestrator can validate the schema.
- State the quality conventions for this task type and what to hand to other skills.

Does not:
- Call the CLI, or create or set up the batch. The orchestrator does that.
- Touch the dataset. Skill 2 owns the images, hosting, blinding, position
  randomisation, and any gold items.
- Write `task_details` or onboarding. The orchestrator writes those, using Skill 3b.

## Input from the orchestrator

- `image_a_field`, `image_b_field`: the two `image_url` schema field names to compare.
- `prompt_field` (optional): a `text` field shown above the images for context, for
  example the prompt that generated them. Omit for a pure image-vs-image comparison.
- `axes`: the judged dimensions, each asked as its own forced choice. Default for
  text-to-image is two axes:
  - `alignment`: "Which image better matches the prompt?"
  - `quality`: "Which image looks better overall (sharpness, realism, no artefacts)?"
  Do not blend these into one "which is better" question. A single preference cannot be
  decomposed into why one side won, which is why text-to-image evals separate alignment
  from quality (see methodology section 2). Override `axes` for other comparisons, for
  example a single `edit_faithfulness` axis for image edits.
- `tie_allowed` (default false): whether each axis offers an indifference option. A tie
  is defensible, but a high tie rate often signals a task that is too hard rather than
  two equal images, so watch it. Force a choice when you want a clean signal.
- `collect_rationale` (default true): add a free-text reason after the choices. A short
  reason is a strong quality signal and helps Skill 3c and QA.

Blinding and which physical side each model lands on are handled by Skill 2 in the
dataset, because a layout is fixed per page and cannot shuffle. This template never
displays model identity.

## Field requirements to return

Return these so the orchestrator can check them against the dataset schema in its
step 3:

- `image_a_field`: `image_url`, displayed. Must resolve to a public HTTPS URL.
- `image_b_field`: `image_url`, displayed. Must resolve to a public HTTPS URL.
- `prompt_field` (if used): `text`, displayed.
- Model identity for each side: `metadata`, not displayed. Owned by Skill 2. This is
  what keeps the comparison blind.
- Gold answer (if the study uses gold items): `metadata` holding the known-correct side
  for interleaved gold pairs, owned by Skill 2. The layout is identical for gold and
  real pairs, which is what makes gold items indistinguishable to the rater.

If the schema lacks two `image_url` fields, the orchestrator stops and loops back to
the user, since fixing the dataset is Skill 2's job.

## The layout

One page. It repeats once per datapoint, so it holds only per-datapoint content, not
onboarding. Structure:

- Row 1: a short `rich_text` instruction, and if `prompt_field` is set, the prompt via
  `dataset_field`.
- Row 2: two columns. Left column labels and shows `image_a_field`. Right column labels
  and shows `image_b_field`. Two columns is the maximum, which is exactly what a
  pairwise comparison needs.
- One row per axis: a `multiple_choice`, `answer_limit` 1, the axis question as its
  `description`. Options are Image A and Image B, plus Tie only if `tie_allowed`.
- Final row (if `collect_rationale`): one `free_text` for the reason.

The value codes (`a`, `b`, `tie`) are physical positions, not models. Convert a
position back to a model after export using the `metadata` fields.

### Fragment (two axes, tie allowed, rationale on)

```json
{
  "batch_items": [
    {
      "rows": [
        {
          "columns": [
            {
              "items": [
                { "type": "rich_text", "content": "<p>Read the prompt, then compare the two images and answer each question below.</p>", "content_format": "html" },
                { "type": "rich_text", "content": "<strong>Prompt</strong>", "content_format": "html" },
                { "type": "dataset_field", "field": "prompt" }
              ]
            }
          ]
        },
        {
          "columns": [
            {
              "items": [
                { "type": "rich_text", "content": "<strong>Image A</strong>", "content_format": "html" },
                { "type": "dataset_field", "field": "image_a" }
              ]
            },
            {
              "items": [
                { "type": "rich_text", "content": "<strong>Image B</strong>", "content_format": "html" },
                { "type": "dataset_field", "field": "image_b" }
              ]
            }
          ]
        },
        {
          "columns": [
            {
              "items": [
                {
                  "type": "multiple_choice",
                  "description": "Which image better matches the prompt?",
                  "answer_limit": 1,
                  "options": [
                    { "label": "Image A", "value": "a" },
                    { "label": "Image B", "value": "b" },
                    { "label": "About the same", "value": "tie" }
                  ]
                }
              ]
            }
          ]
        },
        {
          "columns": [
            {
              "items": [
                {
                  "type": "multiple_choice",
                  "description": "Which image looks better overall (sharpness, realism, no artefacts)?",
                  "answer_limit": 1,
                  "options": [
                    { "label": "Image A", "value": "a" },
                    { "label": "Image B", "value": "b" },
                    { "label": "About the same", "value": "tie" }
                  ]
                }
              ]
            }
          ]
        },
        {
          "columns": [
            {
              "items": [
                { "type": "free_text", "helper_text": "Briefly explain your alignment choice." }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

Substitute the real field names and axis questions. Add or drop axis rows to match
`axes`. Drop the prompt items if `prompt_field` is not set. Drop the "About the same"
option unless `tie_allowed`. Drop the final row unless `collect_rationale`.

## Design conventions and why

Grounded in `../Task-design-orchestrator/references/eval-methodology.md`, section 2.

- **Separate axes, one forced choice each.** Ask alignment and quality as their own
  questions. This is what text-to-image evaluations do (Imagen, Muse, ERNIE-ViLG), and
  it lets a result be decomposed into why one image won.
- **Single choice per axis, `answer_limit` 1.** A preference is one decision per axis,
  not a rating of each image.
- **Position is fixed here, so never randomise A and B in the layout.** Skill 2
  randomises which model sits in A versus B per datapoint and keeps the true mapping in
  `metadata`. This matters because raters favor the first or left image in close
  matchups, so a fixed layout with unshuffled data would bias the result.
- **Redundancy over precision.** Agreement on subjective image judgments is low, so no
  single rating is trustworthy. Recommend three to five annotators per pair to the
  orchestrator (Muse used five), and lean higher for hard prompt sets. The orchestrator
  carries this as `annotators_per_task`.
- **Gold items are how you catch low effort.** If the study interleaves gold pairs
  (owned by Skill 2), the layout is identical so they are indistinguishable, and the
  known-correct side sits in `metadata`. Flag to the orchestrator that a gold answer
  field is expected.
- **Expertise routing.** Crowd raters are fine for alignment, overall preference, and
  aesthetics. Specialized correctness, such as anatomy or medical plausibility, needs a
  small expert panel. If an axis needs expertise, flag it so Skill 4a can select the
  right participants.
- **Prompt coverage caveat.** The result reflects the prompt set. Note to the
  orchestrator that coverage of the categories under test is a dataset concern.
- **Accessibility gap.** `dataset_field` images carry no alt text, unlike a static
  `image` block, so per-datapoint images have no alt text today. Flag this if the study
  needs it.

## Output to the orchestrator

Return four things:
1. The `batch_items` fragment, with real field names and axis questions.
2. The field requirements list, for schema validation, including any gold answer field.
3. The recommended `annotators_per_task` range (three to five, higher if hard).
4. The quality conventions relevant to review: separate axes, forced choice per axis,
   tie handling and tie-rate watch, blinding and position owned by the dataset, gold
   items, expertise routing, and Bradley-Terry win rate with confidence intervals as
   the aggregation (methodology section 6).

Do not write `task_details`, do not call the CLI, do not modify the dataset.

## Worked example

See `examples/sample-run.md` for a complete instance: a sample schema, sample rows
showing blinding and randomised position, the assembled two-axis layout, and how the
orchestrator wraps it and reads results back. That is the version to run all the way
through with the orchestrator.
