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
