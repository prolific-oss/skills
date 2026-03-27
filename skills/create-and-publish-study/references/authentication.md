---
name: authentication
description: Prolific CLI installation, PROLIFIC_TOKEN setup, and auth verification
---

# Authentication

The `prolific` CLI authenticates using a token from your Prolific account.

## Install the CLI

```bash
go install github.com/prolific-oss/cli/cmd/prolific@latest
```

Requires Go; see the [Prolific CLI documentation](https://github.com/prolific-oss/cli) for the current minimum supported version. Alternatively, download a pre-built binary from the [GitHub releases page](https://github.com/prolific-oss/cli/releases) and add it to your `PATH`.

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
source ~/.zshrc
```

## Verifying authentication

```bash
prolific whoami
```

Returns your account details if the token is valid. A `401 Unauthorized` error means the token is missing, expired, or incorrect — return to **Settings → API** to verify or regenerate it.

## Workspace defaults (optional)

To avoid passing `--workspace` on every command, set a default workspace ID in the CLI config file:

```yaml
# $HOME/.config/prolific-oss/prolific.yaml
workspace: your-workspace-id
```

Run `prolific workspace` to find your workspace ID.
