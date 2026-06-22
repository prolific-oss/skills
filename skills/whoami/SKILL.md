---
name: whoami
description: Shows details about the current Prolific account — who you are signed in as, your researcher identity, email, and workspace. Use when asked "who am I on Prolific", "what account am I using", or to confirm the active Prolific credentials.
version: 0.2.0
---

## Who Am I

When asked who the current Prolific user is (or to confirm which account/credentials are active), follow these steps.

### Step 1: Fetch the account details

Mandatory: run the following Prolific CLI command to retrieve details about the authenticated account.

```bash
prolific whoami
```

If the command fails because the CLI is not installed or no credentials are configured, do **not** guess or fabricate an identity. Instead, tell the user the CLI could not authenticate and point them to set up the Prolific CLI (`prolific --help` and the config file at `$HOME/.config/prolific-oss/prolific.yaml`).

### Step 2: Present the identity

Report the account details returned by the command in a clear, readable form. Typically this includes:

- **Name** — the researcher's name on the account
- **Email** — the email the account is registered under
- **ID** — the researcher / account identifier
- **Workspace** — the active workspace, if shown

Summarise plainly, e.g. "You are signed in as <name> (<email>), researcher ID <id>." Only report fields that the command actually returned — never invent missing values.
