# Prolific Skills

Official skills from Prolific for AI research workflows. These skills provide API integration patterns and autonomous research tools following the [agentskills.io](https://agentskills.io) specification.

## Installation

```bash
npx skills add prolific/skills
```

Or install individual skills:

```bash
# Study creation and publishing only
npx skills add prolific/skills --skill create-and-publish-study

# Participant message analysis only
npx skills add prolific/skills --skill examine-participant-messages
```

### Claude Code Plugin

You can also add this as a plugin marketplace in Claude Code:

```bash
/plugin marketplace add prolific/skills
/plugin install create-and-publish-study@prolific
/plugin install examine-participant-messages@prolific
```

## Skills Included

### 1. create-and-publish-study

CLI skill for creating and publishing Prolific studies covering:

- **CLI Setup** — install the `prolific` CLI and authenticate with `PROLIFIC_TOKEN`
- **Study Config** — YAML-driven study definition with annotated schema
- **Study Creation** — `prolific study create -t config.yaml`; returns a draft study ID
- **Study Publishing** — `--publish` flag or separate `prolific study publish <id>`; funds check before publishing
- **Error Handling** — CLI error scenarios: auth failures, YAML parse errors, insufficient funds

### 2. examine-participant-messages

Autonomous agent skill that:

- **Fetches messages** — retrieves all participant messages across your recent studies using the `prolific` CLI, no manual export needed
- **Asks for focus** — prompts you for an analysis question with AI-task-specific options
- **Analyses patterns** — groups by message category (technical, payment, feedback, etc.) across all studies
- **Reports findings** — formatted markdown with representative quotes, study attribution, impact ratings, and recommendations

## Quick Reference

### CLI Commands

| Command | Purpose |
| ------- | ------- |
| `prolific study create -t config.yaml` | Create a study in draft state |
| `prolific study create -t config.yaml --publish` | Create and immediately publish |
| `prolific study publish <study-id>` | Publish an existing draft |
| `prolific studies` | List all studies |

### Message Categories

| Category | Meaning |
| -------- | ------- |
| `technical-issues` | Bugs, loading errors, browser problems |
| `payment-timing` | Questions about when payment arrives |
| `payment-issues` | Payment disputes or missing payments |
| `feedback` | General task experience feedback |
| `rejections` | Concerns about submission rejections |
| `other` | Uncategorised messages |

## Prerequisites

**`PROLIFIC_TOKEN`** — required for all API operations and the `examine-participant-messages` skill.

```bash
export PROLIFIC_TOKEN='your-token-here'
```

To persist across sessions, add to your shell profile (`~/.zshrc` or `~/.bashrc`):

```bash
echo 'export PROLIFIC_TOKEN="your-token-here"' >> ~/.zshrc
```

Get your token: Prolific researcher dashboard → **Settings** → **API**.

## Documentation

- [Prolific Documentation](https://docs.prolific.com)
- [API Reference](https://docs.prolific.com/api-reference/introduction)

## Author

[Prolific](https://prolific.com)
