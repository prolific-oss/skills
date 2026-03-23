---
name: authentication
description: PROLIFIC_TOKEN setup and request header format
---

# Authentication

All Prolific API requests require a bearer token passed as an HTTP header.

## Getting your token

1. Log in to the [Prolific researcher dashboard](https://app.prolific.com).
2. Go to **Settings → API**.
3. Copy your API token.

## Setting the environment variable

```bash
export PROLIFIC_TOKEN="your-token-here"
```

To persist across shell sessions, add the export to your shell profile:

```bash
echo 'export PROLIFIC_TOKEN="your-token-here"' >> ~/.zshrc
```

Then reload the profile:

```bash
source ~/.zshrc
```

## Validating the token is set

```bash
[ -z "$PROLIFIC_TOKEN" ] && echo "not_set" || echo "ok"
```

## Request header format

Every API request must include the following header:

```
Authorization: Token $PROLIFIC_TOKEN
```

### curl example

```bash
curl -s https://api.prolific.com/api/v1/users/me/ \
  -H "Authorization: Token $PROLIFIC_TOKEN"
```

### Python example

```python
import os
import requests

headers = {"Authorization": f"Token {os.environ['PROLIFIC_TOKEN']}"}
response = requests.get("https://api.prolific.com/api/v1/users/me/", headers=headers)
response.raise_for_status()
```

> A `401 Unauthorized` response means the token is missing, expired, or incorrect. Return to **Settings → API** to verify or regenerate it.
