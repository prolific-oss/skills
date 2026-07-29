---
name: study-recruitment-proposal
description: Given a target demographic/persona and a participant group from a study spec, reviews existing Prolific screeners for fit and produces a recruit proposal — a match/gap analysis plus ready-to-use filter and participant-group eligibility requirements. Does not create or modify anything in the workspace.
version: 0.1.0
---

## Study Recruitment Proposal

When asked to propose how to recruit a specific type of participant (e.g. "Domain Experts") for a study, using a named or existing participant group, follow these steps.

This skill is advisory only. It reviews and recommends — it never runs a mutating command (`filter-sets create`, `study create`, `participant create`/`remove`, etc.) on the researcher's behalf.

### Step 1: Identify the target audience and participant group

The request may come as a study specification object rather than free text:

```json
{
  "overview": "string",
  "task_method": "AI Task Builder | External Link",
  "task_format": "Batch | Collection"
}
```

That shape has no dedicated demographics or participant-group fields — treat `overview` as background context and look inside its free text for the persona description. `task_method`/`task_format` describe the study's data-collection mechanics rather than who to recruit; only note them if they constrain who can realistically take part (e.g. an AI Task Builder batch task may assume tooling familiarity an external-link survey wouldn't).

From the request or spec (structured or free text), extract:

- The **target demographic / persona** description (e.g. "Domain Experts", "UK nurses with 5+ years experience")
- The **participant group** — an ID, or a name that needs resolving
- The **workspace** the participant group and study belong to

If the workspace ID is missing, ask for it rather than guessing — participant group and filter set commands are scoped to a workspace.

If only a participant group **name** is given (not an ID), resolve it first:

```bash
prolific participant --help
prolific participant list -w <workspace-id>
```

Match the name against the `Name` column. If nothing matches, say so explicitly — do not invent an ID.

### Step 2: Inspect the participant group

Mandatory: run the following to see who is actually in the group.

```bash
prolific participant view <participant-group-id>
```

This returns participant IDs and the date each was added. Note the group size. A group whose *name* matches the persona but is empty, tiny, or stale (no recent additions) is a real proposal risk — flag it even if nothing else is wrong.

### Step 3: Fetch the filter catalogue and any existing screeners

Mandatory: run the following to understand the current screener/filter landscape.

```bash
prolific filters --help
prolific filters -n
```

Participant groups can themselves appear in this catalogue as a filter — look for an entry with filter_id `participant_group_allowlist` (or `participant_group_blocklist`); its selected values are participant group IDs. Confirm this from the live output rather than assuming it's present.

If the spec references an existing study or filter set to review (rather than starting from a blank slate), fetch it too:

```bash
prolific filter-sets list -w <workspace-id>
prolific filter-sets view <filter-set-id>
```

`filter-sets view` shows the filters currently applied, their selected values/ranges, and the current eligible-participant count — use this as the baseline for the gap analysis in Step 4. If no existing filter set or study is referenced, treat Step 4 as a fresh recommendation instead of a gap analysis against a baseline.

### Step 4: Review screeners for match against the persona

Break the persona description into its distinct requirements. Group them by category, for example:

- **Geographic** — country of residence, nationality
- **Demographic** — age, gender, ethnicity
- **Educational** — highest qualification, student status
- **Employment** — employment status, occupation, industry
- **Behavioural / experiential** — prior Prolific participation, device ownership, health conditions, parental status, language fluency
- **Skill / domain expertise** — professional or subject-matter knowledge (e.g. "Domain Experts"). Prolific's built-in filters are demographic/behavioural, not skill-based, so requirements in this category will usually have no filter equivalent — expect them to end up as GAPs resolved by the participant group, not a filter

Flag any requirement that's ambiguous or doesn't cleanly map to a single filter before proceeding.

For each requirement, compare it against the filter titles, descriptions, questions, and choices from Step 3. If multiple filters could satisfy the same requirement (e.g. nationality vs. country of residence), explain the difference and pick the more appropriate one — don't recommend both without justification.

Classify each requirement against the *existing* screeners fetched in Step 3 (or against "nothing yet" if there's no baseline):

- **MATCH** — an existing filter and selected value(s) already cover this requirement
- **PARTIAL MATCH** — a related filter exists but its selected values/range don't fully cover the requirement (e.g. right filter, wrong choices)
- **GAP** — no existing filter/screener addresses this requirement; recommend the closest matching filter from the catalogue, with its exact `filter_id` and selected values/range

Never fabricate a `filter_id` — every one used in the proposal must come from the Step 3 output. If a requirement has no matching filter at all, say so explicitly and note that the participant group (Step 2) may be the *only* mechanism available to target it, rather than forcing a weak filter match.

### Step 5: Present the recruit proposal

Structure the output as:

1. **Participant group fit** — name, ID, size, and whether it plausibly matches the persona (from Step 2)
2. **Screener match/gap table** — one row per requirement, with its classification, the `filter_id` involved (or "none" for an unmatched GAP), and a one-line rationale explaining why it matches, partially matches, or doesn't
3. **Recommended eligibility requirements**, ready to paste into a filter set template, combining the participant group and any recommended filters in the same `filter_id`/`selected_values`/`selected_range` shape `filter-sets create` expects:

```json
{
  "name": "<persona> recruit proposal",
  "filters": [
    { "filter_id": "participant_group_allowlist", "selected_values": ["<participant-group-id>"] },
    { "filter_id": "<filter-id-from-catalogue>", "selected_values": ["<choice-key>"] }
  ]
}
```

4. **Suggested next step**, not an action taken: tell the researcher they can validate the real eligible-participant count by saving the block above as a template and running it themselves:

```bash
prolific filter-sets create -t <template>.json -w <workspace-id>
```

Never run this (or any other create/update/delete) command as part of producing the proposal — the proposal is a recommendation for the researcher to review, edit, and apply.
