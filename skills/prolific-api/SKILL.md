---
name: prolific-api
description: Prolific API integration guide for AI research workflows - bulk submission approval and bonus payment patterns with Python and curl examples.
metadata:
  author: Prolific
  version: "1.0.0"
  tags: prolific, api, submissions, bonuses, bulk-operations, ai-research
---

# Prolific API

## When to Use

Use this skill when you need to:

- Approve AI task submissions programmatically at the end of a study run.
- Pay participant bonuses based on performance or completion criteria.
- Build automated pipelines that integrate Prolific into your research infrastructure.

## Why Use Bulk Endpoints

> As your usage scales, we recommend batching requests to Prolific. These endpoints combine several operations into one API call, allowing Prolific to process each change when the wallet is available. It is standard practice for third-party APIs like Prolific's to impose rate limits on customer calls — one bulk request is far less likely to hit those limits than hundreds of individual calls.

Replacing a loop of individual calls with one bulk call is usually a small refactor — swap the loop body for a list comprehension that collects IDs, then make a single request.

## Authentication

All requests require your API token as a header:

```bash
export PROLIFIC_TOKEN="your-token-here"
```

```
Authorization: Token $PROLIFIC_TOKEN
```

See [`references/authentication.md`](references/authentication.md) for full setup, shell profile persistence, and a validation snippet.

## Quick Reference

| Method | Path                                              | Purpose                        |
|--------|---------------------------------------------------|--------------------------------|
| POST   | `/api/v1/submissions/bulk-approve/`               | Approve multiple submissions   |
| POST   | `/api/v1/submissions/bonus-payments/`             | Create a bonus payment batch   |
| POST   | `/api/v1/bulk-bonus-payments/{id}/pay/`           | Trigger a bonus payment batch  |

## Bulk Submission Approval

Send a list of submission IDs to approve them in a single call. The response is the async string `"Bulk approve in progress"` — the operation is idempotent and safe to retry.

```bash
curl -s -X POST https://api.prolific.com/api/v1/submissions/bulk-approve/ \
  -H "Authorization: Token $PROLIFIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"submission_ids": ["id1", "id2"]}'
```

Prefer `submission_ids` over `participant_ids`. See [`references/bulk-approve.md`](references/bulk-approve.md) for a full Python example and response details.

## Bonus Payments

Paying bonuses is a two-step process:

1. **Create batch** — POST participant IDs and amounts (in cents) to get a cost preview including fees and VAT.
2. **Trigger payment** — POST to the returned batch ID's `/pay/` endpoint once `total_amount` looks correct.

```python
import os, requests

headers = {"Authorization": f"Token {os.environ['PROLIFIC_TOKEN']}", "Content-Type": "application/json"}

# Step 1
batch = requests.post(
    "https://api.prolific.com/api/v1/submissions/bonus-payments/",
    headers=headers,
    json={"study_id": "<study-id>", "csv_bonuses": "participant_id,amount\nPID1,100\nPID2,150"},
).json()
print(f"Total charge: {batch['total_amount']} cents")

# Step 2
requests.post(f"https://api.prolific.com/api/v1/bulk-bonus-payments/{batch['id']}/pay/", headers=headers)
```

Always check `total_amount` before triggering Step 2. See [`references/bonus-payments.md`](references/bonus-payments.md) for the full example and field descriptions.

## Rate Limiting

The API returns HTTP 429 when rate limits are exceeded. Use exponential backoff: 1s → 2s → 4s → 8s across 4 retries. Bulk calls count as a single request regardless of batch size, so batching is the most reliable way to stay within limits. See [`references/rate-limiting.md`](references/rate-limiting.md) for a reusable Python retry function.

## Error Handling

Check for `401` (bad token), `403` (study ownership), `404` (wrong IDs), `429` (rate limit), and `5xx` (server errors). See [`references/error-handling.md`](references/error-handling.md) for the full status code table and recovery actions.

## Related

- [`examine-participant-messages`](../examine-participant-messages/SKILL.md) — autonomous skill that fetches and analyses messages from participants in a given study. Useful for quality-checking AI tasks before approving submissions.
