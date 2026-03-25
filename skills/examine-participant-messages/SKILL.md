---
name: examine-participant-messages
description: Autonomous skill that fetches recent messages from participants across all your Prolific studies and analyses them for patterns in feedback, technical issues, or questions.
allowed-tools: Bash, AskUserQuestion
argument-hint: [analysis-question]
metadata:
  author: Prolific
  version: "1.1.0"
  tags: prolific, messages, participants, analysis, ai-research
---

# Examine Participant Messages

Fetch all messages from participants across your recent Prolific studies (last 29 days) and analyse them for patterns.

## Step 1 — Verify CLI auth

```bash
prolific whoami
```

If this errors, the `prolific` CLI is not installed or `PROLIFIC_TOKEN` is not set. Explain both and exit:

> The `prolific` CLI is required. Install it with:
>
> ```bash
> go install github.com/prolific-oss/cli/cmd/prolific@latest
> ```
>
> Then set your API token:
>
> ```bash
> export PROLIFIC_TOKEN="your-token-here"
> ```
>
> Get your token from the Prolific researcher dashboard under **Settings → API**. To persist it, add the export to `~/.zshrc` and run `source ~/.zshrc`.

## Step 2 — Get analysis question

If an analysis question was not provided as an argument, use `AskUserQuestion` to prompt the user with these options:

- "What technical or task issues are participants experiencing?"
- "What questions are participants asking about the task instructions?"
- "What feedback are participants giving about the task?"
- "What problems are participants having with payment or submission?"

## Step 3 — Fetch messages (last 29 days)

```bash
CREATED_AFTER=$(python3 -c "from datetime import datetime,timedelta,timezone; print((datetime.now(timezone.utc)-timedelta(days=29)).strftime('%Y-%m-%d'))")
prolific message list -c "$CREATED_AFTER" | grep -v '^&{'
```

The `grep -v '^&{'` strips the CLI debug line from stdout. The remaining output contains the JSON response followed by a human-readable table — parse the line beginning with `{"results"` for message data.

If the command exits with a non-zero status, or the JSON contains a top-level `"detail"` key, display the raw output and the troubleshooting table from the Error Handling section below.

## Step 4 — Analyse patterns

Process all messages from the `results` array:

1. **Group by `data.category`** — `technical-issues`, `payment-timing`, `payment-issues`, `feedback`, `rejections`, `other`.
2. **Count occurrences** and compute each category's percentage of total messages.
3. **Extract representative quotes** from the `body` field; cite the message `id` and `data.study_id` for traceability.
4. **Assess severity** for each pattern: Critical / High / Medium / Low.
5. **Generate specific, actionable recommendations** for each pattern identified.

## Step 5 — Present results

Output the analysis in this format:

````markdown
## Analysis Summary

[Paragraph directly answering the analysis question]

## Key Patterns Identified

### 1. [Pattern Name] (X messages - Y%)

**Impact:** [Critical/High/Medium/Low]
[Description]
**Examples:** "[Quote]" (Message ID: xxx, Study: yyy)
**Recommendation:** [Action]

## Recommendations

1. **[Immediate]** - [Now]
2. **[Short-term]** - [Next iteration]
3. **[Long-term]** - [Structural improvement]

## Supporting Data

- Total messages analysed: X
- Date range: [earliest] to [latest sent_at]
- Studies with messages: [count, list of study IDs]
- Analysis focus: "[question]"
````

## Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| `prolific whoami` fails | CLI not installed or `PROLIFIC_TOKEN` not set | Install CLI; `export PROLIFIC_TOKEN='...'` |
| `401 Unauthorized` | Invalid token | Check token in Prolific dashboard under Settings → API |
| `403 Forbidden` | No access | Verify account permissions |
| Empty results | No messages in the 29-day window | Check that studies were active recently and participants have sent messages |

---

_Modelled on: internal admin `examine-study-feedback` command and `analyse-study-feedback` skill._
