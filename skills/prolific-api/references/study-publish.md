---
name: study-publish
description: Publishing a Prolific study using the prolific CLI — at creation time or as a separate step
---

# Study Publishing

Publishing opens a study to participant recruitment. Prolific charges your wallet immediately on publish — confirm your balance before proceeding.

## Check wallet balance first

```bash
prolific whoami
```

Your current balance is shown in the account output. Required funds = `reward × total_available_places` plus Prolific's service fee (shown at publish time).

## Option A — Publish at creation time

Pass `--publish` to create and open recruitment in one step:

```bash
prolific study create -t study.yaml --publish
```

Requires sufficient wallet funds. If the balance is too low the command fails and the study is left in draft state — no charge is made.

## Option B — Publish after creation

Publish a draft study by ID:

```bash
prolific study publish <study-id>
```

Retrieve the study ID from the creation output or by listing drafts:

```bash
prolific studies
```

## Scripted publish

Capture the study ID at creation and publish immediately in a pipeline:

```bash
STUDY_ID=$(prolific study create -t study.yaml | awk '{print $NF}')
prolific study publish "$STUDY_ID"
```

## What happens on publish

- The study becomes visible to eligible participants on the Prolific platform.
- Your wallet is charged for the full `reward × places` plus fees upfront.
- Recruitment begins immediately — you cannot unpublish once participants have started.

> To pause recruitment after publishing, use `prolific study pause <study-id>`.
