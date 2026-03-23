---
name: error-handling
description: HTTP status codes, causes, and recovery actions
---

# Error Handling

| Status | Cause                        | Action                              |
|--------|------------------------------|-------------------------------------|
| 401    | Invalid/missing token        | Check `PROLIFIC_TOKEN`              |
| 403    | No permission for this study | Verify study ownership              |
| 404    | Study/submission not found   | Check IDs are correct               |
| 429    | Rate limit exceeded          | Retry with exponential backoff      |
| 5xx    | Prolific server error        | Retry after delay                   |

## Notes

- **Bulk approve is idempotent** — already-approved submissions are skipped, so it is safe to retry on network failure or a 5xx response without risk of double-approving.
- **Always check `total_amount`** in the bonus payment batch response (Step 1) before triggering payment (Step 2). Once Step 2 is called, the charge is processed asynchronously and cannot be reversed through the API.

## Related references

- `references/authentication.md` — fixing 401 errors and `PROLIFIC_TOKEN` setup
- `references/rate-limiting.md` — exponential backoff implementation for 429 errors
