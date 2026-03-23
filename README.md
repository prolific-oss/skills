# Prolific Skills

Official skills from Prolific for AI research workflows. These skills provide API integration patterns and autonomous research tools following the [agentskills.io](https://agentskills.io) specification.

## Installation

```bash
npx skills add prolific/skills
```

Or install individual skills:

```bash
# API integration patterns only
npx skills add prolific/skills --skill prolific-api

# Participant message analysis only
npx skills add prolific/skills --skill examine-participant-messages
```

### Claude Code Plugin

You can also add this as a plugin marketplace in Claude Code:

```bash
/plugin marketplace add prolific/skills
/plugin install prolific-api@prolific
/plugin install examine-participant-messages@prolific
```

## Skills Included

### 1. prolific-api

API integration reference for AI research workflows covering:

- **Authentication** — `PROLIFIC_TOKEN` setup and request header format
- **Why Bulk Endpoints** — rationale for batching as usage scales, rate limit context
- **Bulk Submission Approval** — async approval via `submission_ids` array; idempotent and safe to retry
- **Bonus Payments** — two-step pattern: create batch → trigger payment; amounts in cents
- **Rate Limiting** — exponential backoff patterns for 429 responses
- **Error Handling** — status codes, causes, and recovery actions
- **Code Examples** — Python and curl for all operations

### 2. examine-participant-messages

Autonomous agent skill that:

- **Fetches messages** — live API calls using your `PROLIFIC_TOKEN`, no manual export needed
- **Filters by study** — client-side filtering for the specified study ID
- **Asks for focus** — prompts you for an analysis question with AI-task-specific options
- **Analyses patterns** — groups by message category (technical, payment, feedback, etc.)
- **Reports findings** — formatted markdown with representative quotes, impact ratings, and recommendations

## Quick Reference

### API Endpoints

| Operation | Method | Path |
| --------- | ------ | ---- |
| Bulk approve submissions | POST | `/api/v1/submissions/bulk-approve/` |
| Create bonus batch | POST | `/api/v1/submissions/bonus-payments/` |
| Pay bonus batch | POST | `/api/v1/bulk-bonus-payments/{id}/pay/` |
| Fetch participant messages | GET | `/api/v1/messages/?created_after=<ISO8601>` |

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
