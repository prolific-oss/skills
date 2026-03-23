---
name: bonus-payments
description: Two-step bulk bonus payment reference
---

# Bonus Payments

> As your usage scales, we recommend batching bonus payments to Prolific. These endpoints combine several operations into one API call, allowing Prolific to process each payment when the wallet is available. It is standard practice for third-party APIs like Prolific's to impose rate limits on customer calls — one bulk request is far less likely to hit those limits than hundreds of individual calls.

Paying bonuses is a two-step process: first create a payment batch to preview costs, then trigger the payment once the total looks correct.

## Step 1 — Create batch

```
POST https://api.prolific.com/api/v1/submissions/bonus-payments/
```

### Request body

```json
{
  "study_id": "63f1a2b3c4d5e6f7a8b9c0d1",
  "csv_bonuses": "participant_id,amount\nPID1,100\nPID2,150"
}
```

- `csv_bonuses` is a CSV string with a `participant_id,amount` header row.
- Amounts are in **cents** (integers). `100` = £1.00 / $1.00.

### Response

```json
{
  "id": "bonus-batch-id",
  "study": "63f1a2b3c4d5e6f7a8b9c0d1",
  "amount": 250,
  "fees": 25,
  "vat": 5,
  "total_amount": 280
}
```

**Check `total_amount` before proceeding.** This is the amount that will be debited from your wallet in Step 2.

## Step 2 — Trigger payment

```
POST https://api.prolific.com/api/v1/bulk-bonus-payments/{id}/pay/
```

- Use the `id` from the Step 1 response.
- No request body required.
- Returns **HTTP 202 Accepted** — payment processes asynchronously.

## Examples

### curl (both steps)

```bash
# Step 1 — create batch
BATCH=$(curl -s -X POST https://api.prolific.com/api/v1/submissions/bonus-payments/ \
  -H "Authorization: Token $PROLIFIC_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "study_id": "63f1a2b3c4d5e6f7a8b9c0d1",
    "csv_bonuses": "participant_id,amount\nPID1,100\nPID2,150"
  }')

echo "$BATCH"  # review total_amount before continuing

BATCH_ID=$(echo "$BATCH" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# Step 2 — trigger payment
curl -s -X POST "https://api.prolific.com/api/v1/bulk-bonus-payments/${BATCH_ID}/pay/" \
  -H "Authorization: Token $PROLIFIC_TOKEN"
```

### Python (both steps)

```python
import os
import requests

headers = {
    "Authorization": f"Token {os.environ['PROLIFIC_TOKEN']}",
    "Content-Type": "application/json",
}

# Step 1 — create batch
bonuses = [("PID1", 100), ("PID2", 150)]
csv_bonuses = "participant_id,amount\n" + "\n".join(f"{pid},{amount}" for pid, amount in bonuses)

response = requests.post(
    "https://api.prolific.com/api/v1/submissions/bonus-payments/",
    headers=headers,
    json={
        "study_id": "63f1a2b3c4d5e6f7a8b9c0d1",
        "csv_bonuses": csv_bonuses,
    },
)
response.raise_for_status()
batch = response.json()

print(f"Total to be charged: {batch['total_amount']} cents")
# Inspect total_amount before continuing

# Step 2 — trigger payment
pay_response = requests.post(
    f"https://api.prolific.com/api/v1/bulk-bonus-payments/{batch['id']}/pay/",
    headers=headers,
)
pay_response.raise_for_status()  # 202 Accepted
print("Payment triggered successfully.")
```
