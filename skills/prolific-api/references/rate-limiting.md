---
name: rate-limiting
description: Rate limit handling and retry strategies
---

# Rate Limiting

The Prolific API enforces rate limits and returns **HTTP 429 Too Many Requests** when they are exceeded.

## Bulk calls and rate limits

One bulk API call counts as a **single request** regardless of how many submission IDs or bonus rows it contains. Replacing a loop of individual calls with a single bulk call is the most effective way to avoid hitting rate limits entirely.

## Retry strategy: exponential backoff

When a 429 is received, wait before retrying using exponential backoff:

| Attempt | Wait before retry |
|---------|------------------|
| 1       | 1 second          |
| 2       | 2 seconds         |
| 3       | 4 seconds         |
| 4       | 8 seconds         |

After 4 retries, raise an error — continued retrying is unlikely to succeed and may indicate a deeper issue.

## Python retry snippet

```python
import time
import requests


def post_with_retry(url: str, headers: dict, payload: dict, max_retries: int = 4) -> requests.Response:
    delay = 1
    for attempt in range(max_retries + 1):
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 429:
            response.raise_for_status()
            return response
        if attempt == max_retries:
            raise RuntimeError(f"Rate limit exceeded after {max_retries} retries.")
        print(f"Rate limited. Retrying in {delay}s (attempt {attempt + 1}/{max_retries})...")
        time.sleep(delay)
        delay *= 2
```

> See `references/error-handling.md` for the full list of status codes and recovery actions.
