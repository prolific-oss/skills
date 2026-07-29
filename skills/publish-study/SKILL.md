---
name: publish-study
description: Reviews a fully-assembled study spec, checks workspace funds, and publishes it only after explicit researcher confirmation. The one skill in this family that mutates — everything before the confirmation gate is read-only reporting.
version: 0.1.0
---

## Publish Study

When asked to publish a study that's been fully specified in earlier steps, follow these steps. Unlike a purely advisory skill, this one's job is to actually publish — the explicit confirmation gate in Step 3 is what makes that safe, not avoidance of mutation.

### Step 1: Summarise everything decided so far

From the request or spec, assemble a plain-language summary of whatever has already been decided: study overview, target audience (participant group / screeners), estimated completion time, and reward/pay rate. Present this summary to the researcher before doing anything else — this is the review that lets them catch mistakes before money is spent.

If anything material is missing (no reward set, no screeners, no participant count), say so and stop. Don't invent placeholder values just to present a "complete" summary.

### Step 2: Check funds

Mandatory: run the following to see what's actually available to spend.

```bash
prolific workspace balance
```

Omit an explicit workspace ID and let the researcher's configured default apply, unless the spec names a different workspace.

Estimate the study's total cost as `reward × total_available_places` — this is a **floor estimate only**. Prolific's exact total, including its service fee and VAT, is computed via `/api/v1/study-cost-calculator/`, which is not currently exposed by the CLI. State this limitation explicitly rather than presenting your estimate as the final total.

If the estimated cost is close to or exceeds the available balance, flag this clearly and tell the researcher to add funds via the Prolific web app before continuing — there is no CLI command for adding funds.

### Step 3: Get explicit confirmation

Do not publish without an explicit, unambiguous go-ahead. Restate exactly what you're about to do — study name, audience, reward, estimated cost — and ask the researcher to confirm. A vague "ok" or silence is not confirmation; if the response doesn't clearly affirm publishing *this* study with *these* parameters, ask again rather than proceeding.

### Step 4: Optional pre-publish dry run

If a test participant exists in the workspace, offer to validate the configuration first:

```bash
prolific study test <study-id>
```

This creates a test run without publishing to real participants. Recommend it for any study the researcher hasn't tested before, but don't block on it if they decline.

### Step 5: Publish now, or schedule

If the researcher wants to publish immediately:

```bash
prolific study transition -a PUBLISH <study-id>
```

If they want to schedule it for later: the platform does have a `publish_at` field on a study, but this skill hasn't yet confirmed the exact settable path — whether `prolific study create`/`study update` accepts it via template, or whether it needs a different mechanism. Don't guess at a flag that might not exist. Tell the researcher scheduling may need to be set via the Prolific web app until this is verified, rather than silently publishing immediately when they asked to schedule.

### Step 6: Confirm the outcome

After transitioning, run `prolific study view <study-id>` and report back the study's live status, ID, and URL as the final output. If the transition failed, report the exact error — never imply success that didn't happen.
