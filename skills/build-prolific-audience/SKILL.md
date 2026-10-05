---
name: build-prolific-audience
description: Builds, previews, refines, and exports Prolific recruitment audiences from plain-language criteria. Use when a researcher wants participant counts, audience refinement, reusable audience JSON, or breakdown charts.
version: 0.1.0
---

## Build a Prolific Audience

Build and preview a reusable audience using the Prolific CLI's shared search, count, and breakdown services. For filter
recommendations alone, use `recommend-study-filters`; use this workflow when the researcher wants a previewed audience,
counts, refinement, or breakdowns.

### Bundled references

- [CLI reference](references/cli.md): read before constructing payloads or calling search, rule-tree, count, or breakdown.
- [Chart guidance](references/charts.md): read when converting breakdown JSON into a chart.

### Step 1: Establish intent and capabilities

Use the request and conversation to identify the audience, any target sample size, and the workspace. Ask only for
missing information needed for the next step. Keep replies short and describe people in everyday language; use filter
names, IDs, and JSON when explaining technical choices or delivering the payload. Show a readable label alongside any
choice key in prose or tables; keep payload JSON in the API format.

Use the user's configured credentials and selected workspace. Ask for a workspace when unresolved; do not choose an
unrelated workspace or ask the user to paste credentials into chat.

Before constructing or previewing an audience, retrieve the live workspace rule tree following the CLI reference.
Usable rules are required; stop if they cannot be retrieved. The reference defines interpretation, reuse, and refresh
rules. Do not recreate local search/count algorithms or save temporary filter sets to obtain counts.

### Step 2: Discover and propose

Search the live catalogue before proposing a new criterion or answering what criteria are available. Use one phrase
per search call. Batch a small set of relevant phrasings in parallel in the same turn: synonyms, abbreviations and their
expansions, and a broader or narrower term where useful. A failed abbreviation search alone does not establish absence.

Filters matching the same request can select different populations. Read each candidate's question text, selection
type, and choices; explain the deciding differences in those terms rather than relying on titles. Present all materially
distinct relevant matches found, without implying that truncated search results are exhaustive. Use live API choice keys in payloads. Search previews may omit choices; resolve required choices from current catalogue
data before using them.

For an ambiguous term the user supplied, propose a sensible interpretation and explicitly name it and the meaningful
alternative, then build and count the best-fitting interpretation in the same turn. For missing facts that determine
the selection, such as income country/currency, ask rather than inventing a value. If the user delegates the choice,
recommend a default and continue without reopening it.

When no exact criterion is available, say what is unsupported. Offer broader or proxy criteria as alternatives,
explaining how they differ; do not silently replace the requested audience. For prior-study or participant-group
criteria, use the participant-group or study search commands in the CLI reference to resolve accessible items and
selection keys. Do not invent IDs or claim access the tools have not established.

### Step 3: Preview and refine

Build the supported payload using the reference, then obtain a count for that exact audience and workspace. Every stated
participant count must come from an actual result in this conversation. Recount after any criteria change. Never add
counts from separate audiences or breakdown buckets to derive eligibility totals, unions, or counts for changed
criteria. Request a count for those exact criteria instead, regardless of whether categories overlap.

Preserve nested AND/OR intent using `selected_filters` and validate its structure against the retrieved rule tree.
The API remains authoritative; follow the CLI reference's refresh procedure on a group-limit rejection. Restructure
only when the audience's meaning is unchanged; otherwise explain the limitation and ask which requirement can change.
Never flatten an OR into AND or remove criteria just to obtain a count.

An audience that has not been counted has unknown feasibility. Once its choices are resolved and its structure follows
the retrieved rules, try the count before declaring it unsupported. Report the API response; distinguish an absent
catalogue criterion, an explicit rule restriction, and a failed count request.

On an actionable count validation failure, correct the input and retry once; otherwise report what could not be checked.
Preserve privacy suppression and unavailable-count states; neither proves that no participants exist.

For a small audience, propose relaxing a criterion the user can change. For an overly broad audience, propose a relevant
narrowing choice. Preserve their must-have criteria and count each variant before claiming its effect. Do not claim
which criterion limits the pool most without supporting counts.

### Step 4: Show breakdowns when requested or useful

Skip this step unless a breakdown is requested or would materially help a recruitment decision, such as comparing
country groups against sample targets or spotting an uneven distribution. A single total or simple comparison usually
needs no breakdown. For a requested breakdown with no dimension supplied or implied, ask which dimension to use; for
an optional breakdown, offer a useful dimension without holding up the audience result.

Use one breakdown request for the selected dimension and current base audience, rather than a count request per category.
Follow the CLI reference's error handling; a failed breakdown does not invalidate a successful audience count.

Draw a chart when requested or useful, following the chart guidance. Respect text-only requests. Keep the chart tied
to the current audience and chart only successful, unambiguous results.

### Step 5: Deliver

When delivering a proposed or refined audience, include:

- A short description of the people selected and any material assumptions or proxy criteria.
- The count for that exact audience and workspace, with any suppression or failure status. Compare it to the user's
  target when supplied; distinguish current eligibility from guaranteed recruitment.
- Usable JSON shaped as `{"filters": [...]}`, in a JSON code block or a linked saved `.json` file. Deliver the actual
  filters, matching the audience counted. Clearly distinguish counted alternatives from the current selection.
- Any requested or useful breakdown chart, linked or displayed, with the audience and dimension identified. If a chart
  was warranted but could not be generated, state the limitation and provide returned data when available.

Keep the summary, assumptions, workspace, count, preview status, and unsupported requirements outside the filters JSON.
If no successful preview exists, label the payload unpreviewed; if criteria remain unresolved, identify it as an
incomplete draft. A successful count for the supported criteria does not establish that unsupported requirements are
satisfied. Clarification-only turns need not produce a payload; do not invent selections to fill one.

The JSON is a reusable audience component for a filter-set or study payload, not a complete study-create request.
Building and previewing does not itself save a remote filter set, modify a study, or publish a study. If the user asks
for a subsequent mutation, use the relevant supported workflow and the authorization already given for that action.
