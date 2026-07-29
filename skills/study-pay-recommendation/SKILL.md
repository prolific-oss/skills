---
name: study-pay-recommendation
description: Given a study's audience (screeners/participant group) and estimated completion time, produces an opinionated single pay-rate recommendation rather than a range. Currently blocked on a CLI gap for live rate data — flags this rather than guessing (see Step 2).
version: 0.1.0
---

## Study Pay Recommendation

When asked to recommend a reward/pay rate for a study, follow these steps.

### Step 1: Gather the inputs

From the request or spec, extract:

- The **audience** already decided for this study — recommended screener `filter_id`s and/or a participant group, if any were already worked out
- The **estimated completion time**, in minutes
- The **currency** — Prolific's reward recommendations only support `USD` and `GBP`; ask if neither can be inferred from the workspace or researcher

If any of these are missing, ask for them rather than guessing. A pay recommendation without a real estimated time or a real audience is just a guess dressed up as an opinion.

### Step 2: Known gap — no CLI support for reward recommendations

Prolific's `/api/v1/reward-recommendations/` endpoint returns `min_reward_per_hour` and `recommended_reward_per_hour` for a given workspace, currency, and set of screener filter IDs — exactly what this skill needs to be "opinionated." **It is not currently exposed by the Prolific CLI** — the CLI's own contract tests mark it explicitly out of scope.

Until that gap is closed:

- Do not fabricate a reward-per-hour figure, and do not call the raw HTTP API directly to work around the missing CLI command.
- Tell the researcher plainly that a live rate recommendation isn't available through this skill yet, and that the same recommendation is shown in the Prolific web app when creating or editing a study.
- If a draft study already exists for this recruit, there's an indirect signal available: viewing it returns `average_reward_per_hour` / `estimated_reward_per_hour` and an `is_underpaying` flag, computed by the platform from whatever reward is currently set. This can confirm a *chosen* reward isn't underpaying — it does not tell you what to choose, so don't present it as a recommendation.

### Step 3: Present what you can

Even without a live recommendation, produce a structured output the researcher can act on:

1. **Inputs used** — audience summary, estimated completion time, currency
2. **What's missing** — state clearly that `min_reward_per_hour` / `recommended_reward_per_hour` require the Prolific web app (or a future CLI update) until this gap is closed
3. **If a draft study already exists**, check it isn't underpaying once a reward is chosen: `prolific study view <study-id>` and read back `average_reward_per_hour` and `is_underpaying`

Never publish a study, and never create one just to run this check unless one already exists for this recruit — this skill is advisory, not a study-creation step.
