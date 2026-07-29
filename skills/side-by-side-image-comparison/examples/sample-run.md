# Worked example: side-by-side image comparison

A complete instance to run through the chain. Skill 2 would produce the dataset; the
schema and rows here are a fixture so the layout can be built and a batch created
without waiting on Skill 2.

Scenario: two text-to-image models each generated an image for the same prompt. Judge
prompt alignment and image quality as separate axes. Blind, tie allowed, rationale on,
with a small set of interleaved gold pairs to catch low-effort raters.

## 1. Dataset schema (owned by Skill 2, shown here as a fixture)

```json
{
  "strict": false,
  "fields": {
    "prompt":      { "type": "text" },
    "image_a":     { "type": "image_url" },
    "image_b":     { "type": "image_url" },
    "model_a":     { "type": "metadata" },
    "model_b":     { "type": "metadata" },
    "is_gold":     { "type": "metadata" },
    "gold_answer": { "type": "metadata" }
  }
}
```

`model_a` and `model_b` never appear on screen, so the pair is blind. `is_gold` marks
an interleaved control pair, and `gold_answer` holds the known-correct side for it.
Both are metadata, so a gold pair looks identical to a real one.

## 2. Sample data (JSONL)

```
{"prompt": "A red fox sitting in fresh snow at sunrise", "image_a": "https://example.com/img/001_a.png", "image_b": "https://example.com/img/001_b.png", "model_a": "model_x", "model_b": "model_y", "is_gold": "false", "gold_answer": ""}
{"prompt": "A watercolor lighthouse on a rocky cliff", "image_a": "https://example.com/img/002_a.png", "image_b": "https://example.com/img/002_b.png", "model_a": "model_y", "model_b": "model_x", "is_gold": "false", "gold_answer": ""}
{"prompt": "A sharp studio photo of a red apple versus a heavily blurred one", "image_a": "https://example.com/gold/003_a.png", "image_b": "https://example.com/gold/003_b.png", "model_a": "gold", "model_b": "gold", "is_gold": "true", "gold_answer": "a"}
```

Row 2 flips model_x and model_y between positions A and B. Position is randomised per
row by Skill 2, so no rater can infer the model from where it sits. Row 3 is a gold
pair where image A is unambiguously sharper, so any rater who does not pick A on the
quality axis is not looking. Image URLs must be public HTTPS.

## 3. Sub-skill input from the orchestrator

```json
{
  "image_a_field": "image_a",
  "image_b_field": "image_b",
  "prompt_field": "prompt",
  "axes": [
    { "name": "alignment", "question": "Which image better matches the prompt?" },
    { "name": "quality",   "question": "Which image looks better overall (sharpness, realism, no artefacts)?" }
  ],
  "tie_allowed": true,
  "collect_rationale": true
}
```

## 4. Field requirements the sub-skill returns

- `image_a`: image_url, displayed
- `image_b`: image_url, displayed
- `prompt`: text, displayed
- `model_a`, `model_b`: metadata, hidden
- `gold_answer`, `is_gold`: metadata, hidden (gold items)

Recommended `annotators_per_task`: 5 (subjective image judgment, redundancy over
precision).

The orchestrator checks these against the schema in section 1. They match, so it
proceeds.

## 5. Assembled batch_items

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

## 6. What the orchestrator does with this

1. Wraps it with `task_details` from Skill 3b, for example:
   `task_name`: "Image eval: alignment and quality",
   `task_introduction` and `task_steps` with the onboarding, shown once.
2. Creates the batch against the `dataset_id`, with `batch_items` and `task_details`.
3. Sets up the batch with `tasks_per_group` (say 10 pairs per submission), polls to
   `READY`.
4. Outputs `annotators_per_task` (5 here) for Skill 6, and hands the batch and preview
   link to Skill 3c.

## 7. Reading the results

Each response records a chosen `value` (`a`, `b`, or `tie`) per axis, which is a
position. First filter raters using the gold pairs: anyone who misses the obvious gold
answers is dropped before aggregation. Then join the surviving votes back to `model_a`
and `model_b` from metadata to convert positions into models. Aggregate per axis:
majority per pair for a per-item view, and a Bradley-Terry win rate with confidence
intervals across the model, reported separately for alignment and quality. Count a tie
as half a win to each side. Because position was randomised, the aggregate is not
biased by side. Expect modest inter-rater agreement on these axes, which is why the
five-rater redundancy and the confidence intervals matter.
