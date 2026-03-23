---
name: bulk-approve
description: Bulk submission approval endpoint reference
---

# Bulk Submission Approval

> As your usage scales, we recommend batching requests to Prolific. These endpoints combine several operations into one API call, allowing Prolific to process each change when the wallet is available. It is standard practice for third-party APIs like Prolific's to impose rate limits on customer calls — one bulk request is far less likely to hit those limits than hundreds of individual calls.

## Endpoint

```
POST https://api.prolific.com/api/v1/submissions/bulk-approve/
```

## Request body

```json
{
  "submission_ids": ["id1", "id2"]
}
```

Prefer `submission_ids` over `participant_ids` — submission IDs are stable and unambiguous when a participant has multiple submissions in the same study.

## Response

Returns the async string `"Bulk approve in progress"`. The operation is idempotent — already-approved submissions are skipped, so it is safe to retry on failure.

## Examples

### curl

```bash
curl -s -X POST https://api.prolific.com/api/v1/submissions/bulk-approve/ \
  -H "Authorization: Token $PROLIFIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"submission_ids": ["63f1a2b3c4d5e6f7a8b9c0d1", "63f1a2b3c4d5e6f7a8b9c0d2"]}'
```

### Python

```python
import os
import requests

headers = {
    "Authorization": f"Token {os.environ['PROLIFIC_TOKEN']}",
    "Content-Type": "application/json",
}

submission_ids = ["63f1a2b3c4d5e6f7a8b9c0d1", "63f1a2b3c4d5e6f7a8b9c0d2"]

response = requests.post(
    "https://api.prolific.com/api/v1/submissions/bulk-approve/",
    headers=headers,
    json={"submission_ids": submission_ids},
)
response.raise_for_status()
print(response.json())  # "Bulk approve in progress"
```

> The response is async — approval completes in the background. Poll submission status or wait before checking final state.
