---
name: study-create
description: Creating a Prolific study from a YAML config file using the prolific CLI
---

# Study Creation

Create a study by pointing the CLI at a YAML or JSON config file. The CLI validates the config and returns a study ID on success.

## Required fields

| Field | Type | Notes |
|-------|------|-------|
| `name` | string | Shown to participants on the listing page |
| `description` | string | Participant-facing task description; supports HTML |
| `reward` | integer | Payment **in pence** — `400` = £4.00 |
| `estimated_completion_time` | integer | Minutes shown to participants |
| `total_available_places` | integer | Number of participant slots |
| `external_study_url` | string | Must contain `{{%PROLIFIC_PID%}}` |
| `completion_codes` | array | See [Completion codes](#completion-codes) section below |

## Command

```bash
prolific study create -t path/to/study.yaml
```

The study is created in **draft** state — it is not visible to participants until published. See `study-publish.md` to publish immediately or as a separate step.

## Config file schema

All fields shown below. Annotated with types and constraints.

```yaml
# Human-readable title shown to participants on the study listing page
name: My AI annotation task

# Internal label visible only to you — useful for tracking across studies
internal_name: annotation-batch-01

# Participant-facing description of the task (supports plain text)
description: >
  You will review a set of short texts and answer questions about their tone.
  The task takes approximately 10 minutes.

# URL participants are redirected to — must include the PROLIFIC_PID template
# variable so Prolific can match submissions back to participants
external_study_url: "https://your-tool.com/task?pid={{%PROLIFIC_PID%}}"

# How Prolific passes the participant ID to your study URL
# url_parameters: appended as a query param (most common)
prolific_id_option: url_parameters

# Completion codes — each code participants enter at the end of your task
completion_codes:
  - code: "ABC123"
    code_type: COMPLETED          # COMPLETED | FAILED_ATTENTION_CHECK | NO_CONSENT | OTHER
    actions:
      - action: AUTOMATICALLY_APPROVE

# Number of participant slots to open
total_available_places: 50

# Expected task duration shown to participants, in minutes
estimated_completion_time: 10

# Hard timeout before a submission is auto-returned, in minutes
# Should be longer than estimated_completion_time to allow for slower participants
maximum_allowed_time: 20

# Payment per participant in pence/cents — 400 = £4.00 / $4.00
# Prolific recommends at least minimum wage for your target country
reward: 400

# Devices participants may use — limit to control task environment
# Options: desktop, tablet, mobile
device_compatibility:
  - desktop

# Hardware required — only list what your task genuinely needs
# Options: audio, camera, download, microphone
peripheral_requirements: []

# Controls how many times a single participant can take this study
# -1 = unlimited (useful for multi-session AI tasks)
# 1  = one submission per participant (default for most studies)
submissions_config:
  max_submissions_per_participant: 1
```

## Completion codes

`completion_codes` is a list. Each entry has:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `code` | string | yes | The string participants enter; use `null` for no-code flows |
| `code_type` | enum | yes | `COMPLETED`, `FAILED_ATTENTION_CHECK`, `NO_CONSENT`, `FOLLOW_UP_STUDY`, `GIVE_BONUS`, `INCOMPATIBLE_DEVICE`, `OTHER`, `FIXED_SCREENOUT` |
| `actions` | array | yes | What Prolific does when this code is submitted |
| `actor` | enum | no | `"participant"` (default) or `"researcher"` |

### Actions

| Action | Effect |
|--------|--------|
| `AUTOMATICALLY_APPROVE` | Auto-approve the submission |
| `MANUALLY_REVIEW` | Submission goes to researcher review queue |
| `REQUEST_RETURN` | Ask participant to return the submission |
| `ADD_TO_PARTICIPANT_GROUP` | Add participant to a group |
| `REMOVE_FROM_PARTICIPANT_GROUP` | Remove participant from a group |

**Most studies use one code** with `code_type: COMPLETED` and `action: AUTOMATICALLY_APPROVE`. Add additional codes for attention-check failures or screen-outs.

### Example: two codes

```yaml
completion_codes:
  - code: "COMPLETE99"
    code_type: COMPLETED
    actions:
      - action: AUTOMATICALLY_APPROVE
  - code: "SCREENOUT1"
    code_type: FAILED_ATTENTION_CHECK
    actions:
      - action: REQUEST_RETURN
```

## Scripted / batch creation

For launching multiple studies without interactive prompts, the CLI runs silently when all required fields are present in the config:

```bash
for config in studies/*.yaml; do
  prolific study create -t "$config"
done
```

## Output

On success the CLI prints the new study ID:

```
Study created: 66a1b2c3d4e5f6a7b8c9d0e1
```

Capture it for use in subsequent publish or monitor commands:

```bash
STUDY_ID=$(prolific study create -t study.yaml | awk '{print $NF}')
```

Run `prolific studies` to list all studies and confirm the new draft appears.
