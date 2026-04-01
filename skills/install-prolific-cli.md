---
name: install-prolific-cli
description: Checks for Go, installs it if missing, then installs the Prolific CLI via go install
---

## Install the Prolific CLI

### Step 1: Check for Go

Run the following to check if Go is installed:

```bash
go version
```

- **If Go is installed** (output like `go version go1.22.0 ...`): skip to Step 2.
- **If Go is not installed** (command not found or similar error): follow the instructions below for your platform.

#### Installing Go

Navigate to https://go.dev/doc/install and follow the relevant instructions.

After installing, verify with `go version` before continuing.

### Step 2: Install the Prolific CLI

```bash
go install github.com/prolific-oss/cli/cmd/prolific@latest
```

This installs the `prolific` binary to `$GOPATH/bin` (typically `~/go/bin`). Ensure that directory is on your `PATH`:

```bash
export PATH=$PATH:$(go env GOPATH)/bin
```

Verify the installation:

```bash
prolific --version
```

### Step 3: Configure your Prolific API token

To find or create your token, log in to the Prolific platform and navigate to **API tokens** in the left-hand menu.

Once you have your token, set it in your **current AI-live terminal session**:

```bash
export PROLIFIC_TOKEN="your-token-here"
```

> **Important:** Do this in a separate terminal that is not connected to an AI-driven session.

Verify the token is available:

```bash
echo $PROLIFIC_TOKEN
```

### Step 4: Verify

Run `prolific whoami` in that new terminal to verify you are authenticated with Prolific. You may need to restart your AI session to allow access to the new environment variable and run the Prolific CLI successfully.
