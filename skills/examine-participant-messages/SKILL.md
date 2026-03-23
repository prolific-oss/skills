---
name: examine-participant-messages
description: Autonomous skill that fetches messages from Prolific study participants and analyses them for patterns in feedback, technical issues, or questions. Requires PROLIFIC_TOKEN env var.
allowed-tools: Bash, AskUserQuestion
argument-hint: <study-id> [analysis-question]
metadata:
  author: Prolific
  version: "1.0.0"
  tags: prolific, messages, participants, analysis, ai-research
---

# Examine Participant Messages

Fetch all messages from participants in a Prolific study over the last 30 days and analyse them for patterns.

## Step 1 — Validate study ID

Check that a study ID was provided as the first argument. If missing, print usage and exit:

```
Usage: examine-participant-messages <study-id> [analysis-question]

Example:
  examine-participant-messages 63f1a2b3c4d5e6f7a8b9c0d1
  examine-participant-messages 63f1a2b3c4d5e6f7a8b9c0d1 "What technical issues are participants experiencing?"
```

## Step 2 — Check PROLIFIC_TOKEN

```bash
[ -z "$PROLIFIC_TOKEN" ] && echo "not_set" || echo "ok"
```

If the output is `not_set`, explain that the token is required and exit:

> `PROLIFIC_TOKEN` is not set. Get your API token from the Prolific researcher dashboard under **Settings → API**, then run:
>
> ```bash
> export PROLIFIC_TOKEN="your-token-here"
> ```
>
> To persist it across sessions, add the export to `~/.zshrc` and run `source ~/.zshrc`.

## Step 3 — Get analysis question

If an analysis question was not provided as the second argument, use `AskUserQuestion` to prompt the user with these options:

- "What technical or task issues are participants experiencing?"
- "What questions are participants asking about the task instructions?"
- "What feedback are participants giving about the task?"
- "What problems are participants having with payment or submission?"

## Step 4 — Fetch messages (last 30 days)

```bash
CREATED_AFTER=$(python3 -c "from datetime import datetime,timedelta,timezone; print((datetime.now(timezone.utc)-timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
curl -s -G "https://api.prolific.com/api/v1/messages/" \
  --data-urlencode "created_after=$CREATED_AFTER" \
  -H "Authorization: Token $PROLIFIC_TOKEN"
```

If the curl exits with a non-zero status, or the response contains a top-level `"detail"` key, display the raw response and the troubleshooting table from the Error Handling section below.

## Step 5 — Filter messages

From the `results` array, keep only entries where `data.study_id` matches the provided study ID.

If zero messages remain after filtering, explain the 30-day window and suggest:

> No messages found for this study in the last 30 days. Check that:
> - The study ID is correct (24-character hex string).
> - The study was active within the last 30 days.
> - Participants have sent messages (not all studies receive messages).

## Step 6 — Analyse patterns

Process the filtered messages:

1. **Group by `data.category`** — `technical-issues`, `payment-timing`, `payment-issues`, `feedback`, `rejections`, `other`.
2. **Count occurrences** and compute each category's percentage of total messages.
3. **Extract representative quotes** from the `body` field; cite the message `id` for traceability.
4. **Assess severity** for each pattern: Critical / High / Medium / Low.
5. **Generate specific, actionable recommendations** for each pattern identified.

## Step 7 — Present results

Output the analysis in this format:

````markdown
## Analysis Summary

[Paragraph directly answering the analysis question]

## Key Patterns Identified

### 1. [Pattern Name] (X messages - Y%)

**Impact:** [Critical/High/Medium/Low]
[Description]
**Examples:** "[Quote]" (Message ID: xxx)
**Recommendation:** [Action]

## Recommendations

1. **[Immediate]** - [Now]
2. **[Short-term]** - [Next iteration]
3. **[Long-term]** - [Structural improvement]

## Supporting Data

- Total messages analysed: X
- Date range: [earliest] to [latest sent_at]
- Study ID: [id]
- Analysis focus: "[question]"
````

## Error Handling

| Error                      | Cause                  | Resolution                          |
|----------------------------|------------------------|-------------------------------------|
| Missing study ID           | No argument            | Show usage                          |
| `PROLIFIC_TOKEN` not set   | Missing env var        | `export PROLIFIC_TOKEN='...'`       |
| 401 Unauthorized           | Invalid token          | Check token in dashboard            |
| 403 Forbidden              | No access              | Verify study ownership              |
| Empty results after filter | No messages in 30 days | Check study age / ID                |
| `"detail": "Not found"`    | Invalid study ID       | Verify 24-char hex format           |

---

_Modelled on: internal admin `examine-study-feedback` command and `analyse-study-feedback` skill._
