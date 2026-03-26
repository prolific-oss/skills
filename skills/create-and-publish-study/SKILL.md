---
name: create-and-publish-study
description: Prolific CLI guide for creating and publishing research studies — YAML-driven study setup with the prolific CLI tool.
metadata:
  author: Prolific
  version: "1.1.0"
  tags: prolific, cli, study, create, publish, ai-research
---

# Prolific CLI

## When to Use

Use this skill when you need to:

- Create a new Prolific study for AI data collection or annotation.
- Publish a study to open it to participant recruitment.
- Script or automate study launches across multiple configs.

## Prerequisites

The `prolific` CLI must be installed and authenticated before running any commands:

```bash
go install github.com/prolific-oss/cli/cmd/prolific@latest
```

See [`references/authentication.md`](references/authentication.md) for full installation options, token setup, and workspace defaults.

For the full list of CLI flags run:

```bash
prolific study create --help
```

CLI reference: [docs.prolific.com/documentation/tooling/prolific-cli.md](https://docs.prolific.com/documentation/tooling/prolific-cli.md)

## Authentication

Set your API token as an environment variable:

```bash
export PROLIFIC_TOKEN="your-token-here"
```

Verify it works:

```bash
prolific whoami
```

See [`references/authentication.md`](references/authentication.md) for shell profile persistence and optional workspace config.

## Quick Reference

| Command | Purpose |
|---------|---------|
| `prolific study create -t config.yaml` | Create a study in draft state |
| `prolific study create -t config.yaml --publish` | Create and immediately publish |
| `prolific study publish <study-id>` | Publish an existing draft |
| `prolific studies` | List all studies |
| `prolific study pause <study-id>` | Pause recruitment after publishing |

## Study Config File

Studies are defined in YAML. Minimal example:

```yaml
name: My AI annotation task
internal_name: annotation-batch-01
description: Review short texts and answer questions about their tone.
external_study_url: "https://your-tool.com/task?pid={{%PROLIFIC_PID%}}"
prolific_id_option: url_parameters
completion_code: ABC123
total_available_places: 50
estimated_completion_time: 10
maximum_allowed_time: 20
reward: 400
device_compatibility:
  - desktop
peripheral_requirements: []
submissions_config:
  max_submissions_per_participant: 1
```

`reward` is in pence — `400` = £4.00. `{{%PROLIFIC_PID%}}` is required in the URL so Prolific can match submissions to participants. See [`references/study-create.md`](references/study-create.md) for the full annotated schema.

## Build a Study Config

**Before asking any questions**, check whether a study config already exists:

- If the user has provided a path to a `.yaml`, `.yml`, or `.json` file — read it, validate it against the required fields in [`references/study-create.md`](references/study-create.md#required-fields), flag any missing or invalid values, and proceed directly to [Creating a Study](#creating-a-study).
- If the user says they already have a config — ask them to share or point to it, then validate.
- Only proceed to the elicitation questions below if no config exists yet.

If a study YAML does not already exist, work through the groups below in order. Skip optional groups if the user has no requirements for them.

### Group 1 — Core (required)

1. **Study name** — What is the public title participants will see?
2. **Description** — Describe the task participants will do. (Paste or write the participant-facing text; HTML is supported.)
3. **External URL** — What is the URL of your survey or experiment tool? (The `{{%PROLIFIC_PID%}}` parameter will be appended automatically if missing.)
4. **Reward** — How much will you pay per participant, in pence? (e.g. `400` = £4.00. Aim for at least minimum wage for your target country based on the estimated time.)
5. **Estimated time** — How many minutes should the task take?
6. **Participant slots** — How many participants do you need?
7. **Completion code** — What code will participants enter at the end of your task to confirm completion? (If your tool generates the code, provide it now. If unsure, use a random 6-character alphanumeric string.)

### Group 2 — Device & environment (optional, defaults shown)

8. **Device compatibility** — Which devices should participants be allowed to use? (Default: `desktop` only. Options: `desktop`, `tablet`, `mobile`.)
9. **Peripheral requirements** — Does the task require any hardware beyond a keyboard? (Default: none. Options: `audio`, `camera`, `microphone`, `download`.)
10. **Maximum allowed time** — What hard timeout (minutes) should Prolific set before auto-returning an incomplete submission? (Default: `estimated_completion_time × 2`.)

### Group 3 — Participant targeting (optional)

11. **Filters** — Do you need to restrict to specific demographics (age, fluency, country, etc.)? If yes, list the criteria. See [`references/study-create.md`](references/study-create.md#participant-filters) for the filter YAML format.

### Group 4 — Advanced (optional)

12. **Study labels** — Should this study be tagged? Options: `survey`, `annotation`, `decision_making_task`, `interview`.
13. **Content warnings** — Does the study contain any sensitive content participants should be warned about?
14. **Internal name** — Do you want a private label for your own tracking (e.g. `annotation-batch-03`)?
15. **Multi-submission** — Should a single participant be able to take this study more than once? (Default: `1`. Use `-1` for unlimited.)

### Produce the YAML

Once you have answers, output a complete YAML config. Use this template as your base and populate with the collected values:

```yaml
name: "<study name>"
internal_name: "<internal name or omit>"
description: >
  <participant-facing description>
external_study_url: "<url>?pid={{%PROLIFIC_PID%}}"
prolific_id_option: url_parameters
completion_codes:
  - code: "<completion code>"
    code_type: COMPLETED
    actions:
      - action: AUTOMATICALLY_APPROVE
total_available_places: <number>
estimated_completion_time: <minutes>
maximum_allowed_time: <estimated_completion_time × 2>
reward: <pence>
device_compatibility:
  - desktop
peripheral_requirements: []
submissions_config:
  max_submissions_per_participant: 1
```

Add `filters:`, `study_labels:`, `content_warnings:`, and `naivety_distribution_rate:` if provided (see [`references/study-create.md`](references/study-create.md) for their formats). Save the file as `study.yaml` (or a descriptive name) and confirm with the user before proceeding.

## Creating a Study

```bash
prolific study create -t study.yaml
```

Returns the new study ID. The study is in **draft** state and not yet visible to participants.

To capture the ID for scripted pipelines:

```bash
STUDY_ID=$(prolific study create -t study.yaml | awk '{print $NF}')
```

See [`references/study-create.md`](references/study-create.md) for batch creation patterns and all config fields.

## Publishing a Study

Check your wallet balance first (`prolific whoami`), then publish:

```bash
# Option A — publish at creation time
prolific study create -t study.yaml --publish

# Option B — publish an existing draft
prolific study publish <study-id>
```

Publishing charges your wallet immediately and opens recruitment. See [`references/study-publish.md`](references/study-publish.md) for funds requirements and scripted publish patterns.

## Error Handling

Common errors: `401` (bad token), `403` (wrong workspace), YAML parse failures, and insufficient funds at publish time. See [`references/error-handling.md`](references/error-handling.md) for the full table and recovery steps.

## Related

- [`examine-participant-messages`](../examine-participant-messages/SKILL.md) — fetches and analyses messages from participants in a given study. Useful for monitoring task quality after a study goes live.
