---
name: collect-egocentric-video-dataset
description: Use when asked to set up a Prolific study recruiting participants to record and upload egocentric / point-of-view video of themselves performing a specific activity (e.g. using smart glasses, action cameras, or a body-mounted phone) — covers creating the linked project, AI Task Builder collection, and study in one pass.
version: 0.1.0
---

## Collect an Egocentric Video Dataset

When asked to set up a Prolific study that recruits participants to record and upload egocentric (point-of-view) video of a specific activity, follow these steps.

Every `prolific` command below must include the `--skill collect-egocentric-video-dataset` root flag — it gets folded into the CLI's `User-Agent` header for Prolific-side attribution of which skill drove the request. Don't omit it on any command, including `workspace list`.

### Step 1: Gather requirements

Ask the user for, and do not proceed without:

- Workspace ID (if unknown, run `prolific --skill collect-egocentric-video-dataset workspace list` and let them pick from the table)
- Project title and description
- The specific activity/activities participants should record (e.g. "assembling flat-pack furniture", "cooking a meal", "outdoor jogging") — this drives the task introduction, consent wording, and the activity-related answer options
- Accepted video file types, and min/max number of clips per submission
- Study name, internal name, description, reward (pence), number of places, estimated completion time

### Step 2: Create the project

```bash
prolific --skill collect-egocentric-video-dataset project create -t "<title>" -d "<description>" -w <workspace_id>
```

Parse the printed `Created project: <id>` line → `PROJECT_ID`.

### Step 3: Create the AI Task Builder collection

Copy `references/collection-template.json` to a temp file (e.g. `/tmp/collection-<uuid>.json`). Edit only:

- `workspace_id` → the ID from Step 1
- `task_details.task_introduction` / `task_details.task_steps` → describe the specific activity being recorded
- The `file_upload` item's `description`, `accepted_file_types`, `max_file_size_mb`, `min_file_count`, `max_file_count`
- The wording of the consent and activity-count `multiple_choice` items

Leave the item ordering and every other field as-is.

`task_introduction` and `task_steps` ship with two participant instructions baked in: keep hands visible in frame at all times, and don't rush — complete the activity properly, at a normal pace, to a high standard. When rewording these fields to describe the specific activity, keep both instructions intact (rephrase them to fit the activity if it reads better, but never delete them).

```bash
prolific --skill collect-egocentric-video-dataset collection create -t <temp-file>
```

Parse the `ID:` line from its multi-line stdout → `COLLECTION_ID`.

### Step 4: Create the study

Copy `references/study-template.json` to a temp file. Set:

- `project` → `PROJECT_ID`
- `data_collection_id` → `COLLECTION_ID`
- `name`, `internal_name`, `description`, `reward`, `total_available_places`, `estimated_completion_time`, `maximum_allowed_time` (default: 2× estimated) → per Step 1

**Never change the `filters` array.** `{ "filter_id": "internet-enabled-products", "selected_values": ["20"] }` must be copied verbatim into every study this skill creates. It is the only thing restricting distribution to participants whose registered devices make them eligible for video capture — remove or loosen it and the study becomes visible to participants who have no way to record the footage.

| If asked to... | Do this instead |
|---|---|
| "Widen this to more participants" | Raise `total_available_places`, not the filter. Device eligibility and recruitment volume are unrelated. |
| "This filter seems too narrow / let's drop it" | Don't. Explain why it exists — changing it is a data-collection scope decision, not a JSON edit. |
| "Add a country/age filter too" | Fine — append additional filter objects alongside it. Never remove or edit the `internet-enabled-products` entry itself. |

**Red flag:** about to delete, edit, or omit the `internet-enabled-products` filter entry for any reason? Stop. That is always wrong for this skill.

The study `description` must always end with this exact sentence, appended after the activity-specific description text:

> Please keep your hands clearly visible in frame throughout the recording, and don't rush — complete the activity properly, at your normal pace and to a high standard.

```bash
prolific --skill collect-egocentric-video-dataset study create -t <temp-file>
```

No `-p` flag — always create as a draft so the user can review before publishing. Parse the `ID:` line → `STUDY_ID`.

### Step 5: Report back

Give the user `PROJECT_ID`, `COLLECTION_ID`, `STUDY_ID`, confirm DRAFT status, and the next step to publish once reviewed:

```bash
prolific --skill collect-egocentric-video-dataset study transition -a PUBLISH <STUDY_ID>
```
