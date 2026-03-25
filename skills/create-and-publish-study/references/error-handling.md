---
name: error-handling
description: CLI error scenarios, causes, and recovery actions
---

# Error Handling

| Error | Cause | Resolution |
|-------|-------|-----------|
| `401 Unauthorized` | Invalid or missing `PROLIFIC_TOKEN` | Re-export the token, then run `prolific whoami` to confirm it works |
| `403 Forbidden` | No permission for this workspace or study | Check the `workspace` setting in `~/.config/prolific-oss/prolific.yaml` and verify study ownership |
| YAML parse error | Malformed config file | Validate YAML syntax; check all required fields (`name`, `external_study_url`, `reward`, `total_available_places`) are present |
| Insufficient funds | Publishing with a low wallet balance | Top up your wallet in the [Prolific dashboard](https://app.prolific.com) before retrying |
| `404 Not Found` | Invalid study ID passed to publish or pause | Run `prolific studies` to list studies and confirm the ID |
| `5xx` server error | Prolific service issue | Retry after a short delay; check [Prolific status](https://status.prolific.com) |

## Related references

- `references/authentication.md` — CLI installation, token setup, and `prolific whoami` verification
- `references/study-create.md` — required YAML fields and config schema
- `references/study-publish.md` — funds check and publish steps
