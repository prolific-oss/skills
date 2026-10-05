# CLI contract

Use the configured `prolific` CLI. Pass the resolved workspace explicitly to rule-tree, search, count, and breakdown.
Authentication uses the normal Prolific CLI configuration; do not dump configuration files or tokens into the
conversation.

## Retrieve workspace rules

Before constructing or previewing an audience, use the thin CLI command with the current user's credentials:

```bash
prolific filters rule-tree --workspace WORKSPACE_ID --json
```

This calls `GET /api/v1/filters/rule-tree/?workspace_id=WORKSPACE_ID` and returns `{"rule_tree": {...}}`. Require a
successful response containing a nonempty, interpretable `rule_tree` object. If access is denied, the request fails, or
the response is unusable, stop before constructing new selections or making count/breakdown requests. Explain the
blocker and preserve any existing draft without claiming a new preview. Do not substitute fixed or inferred rules,
reuse rules from another context, or omit the workspace to obtain default rules.

Reuse the tree only in the same session and user/credentials, workspace, and API environment. Retrieve it again when
that context changes or a group-limit rejection requires a refresh. A failed refresh also stops the workflow.

Interpret the returned tree relative to the payload's canonical root:

- A sole top-level `and` or `or` group is the root. Otherwise the `filters` array has an implicit AND root.
- Follow each node's `children` entry for the child's type. An absent group type is not permitted there; `leaf: true`
  permits ordinary catalogue filters.
- `max_children` limits immediate children; missing or null means unlimited. `max_by_type` limits immediate children of
  the named types. Zero is a real limit. Nesting permissions depend on position.
- Leaf IDs, choice keys, and numeric bounds come from the live catalogue; the tree governs group structure.

## Search

Run independent phrasings in parallel through the host's tool batching, one phrase per command. For example, submit
these three calls together rather than stopping after an empty abbreviation result:

```bash
prolific filters search 'GP' --workspace WORKSPACE_ID --limit 50 --json
prolific filters search 'general practitioner' --workspace WORKSPACE_ID --limit 50 --json
prolific filters search 'doctor' --workspace WORKSPACE_ID --limit 50 --json
```

Search calls the API-backed catalogue search and preserves server ranking. Results may contain only matching choice
previews. Do not interpret omitted choices as nonexistent. Inspect `prolific filters list --help` and use its supported
non-interactive catalogue output if full choice data is needed. Do not assume a choice-search CLI command exists.
Use additional targeted searches or the supported `--all` option if a result limit hides relevant alternatives.

### Named participant groups and prior studies

Catalogue search does not resolve named participant groups or studies. Use server-side resource search:

```bash
prolific participant search 'pilot cohort' --workspace WORKSPACE_ID --json
prolific study search 'memory task' --workspace WORKSPACE_ID --json
```

These commands send the `search` query parameter to `/api/v1/participant-groups/` and `/api/v1/studies/`, respectively,
alongside `workspace_id`. Do not substitute `name` or `title` parameters or list an entire workspace to search locally.
Inspect returned pagination metadata and use the command's supported pagination options to retrieve additional
matches when needed before claiming an item is absent or unique.

Resolve a returned item's ID and readable name; studies also expose `internal_name`. If several items still fit, show
the distinguishing names/IDs and ask which one the user means. Use the resolved IDs as strings in `selected_values` for
the appropriate live filter: `participant_group_allowlist` / `participant_group_blocklist` or
`previous_studies_allowlist` / `previous_studies_blocklist`. Confirm inclusion versus exclusion from the user's intent
and verify the filter's current semantics. A search result establishes item access, not successful audience eligibility;
preview the resulting payload with count.

## Count an unsaved audience

Write `audience.json` with a `filters` array. For example, this range-only payload requires no categorical choice keys:

```json
{
  "filters": [{ "filter_id": "age", "selected_range": { "lower": 25, "upper": 40 } }]
}
```

```bash
prolific audience count --template-path audience.json --workspace WORKSPACE_ID --json
```

Replace `WORKSPACE_ID` with the user's resolved workspace. The template contains `filters`; the command adds
`workspace_id` when calling `POST /api/v1/eligibility-count/`.

Categorical selections use `{"filter_id": "catalogue-id", "selected_values": ["choice-key"]}` with real IDs and keys
resolved from the current catalogue. Put multiple acceptable values of one criterion in one `selected_values` array. Use
`selected_range` for numeric criteria, respecting the catalogue's type and limits. Do not use both selection forms on
one leaf.

Top-level filters are combined with AND unless a sole group specifies the root relation. Groups use `filter_id: "and"`
or `"or"` and a `selected_filters` array of leaves or nested groups. Both `--filters` JSON and JSON/YAML templates
preserve this structure. For example, the following expresses two alternative age ranges; check the retrieved rule tree
before submitting it for server validation:

```json
{
  "filters": [
    {
      "filter_id": "or",
      "selected_filters": [
        { "filter_id": "age", "selected_range": { "lower": 18, "upper": 30 } },
        { "filter_id": "age", "selected_range": { "lower": 50, "upper": 65 } }
      ]
    }
  ]
}
```

The JSON result contains `count` and `below_privacy_threshold`. The command marks returned zero as potentially
privacy-suppressed. Report “zero or below the reporting threshold,” not “no participants.” Do not infer an exact privacy
threshold from the count response.

The current count command takes either `--template-path` or `--filters`, not both. It does not support `--filter-set`.
If starting from a saved definition, resolve its actual filters using an available supported read operation before
counting; do not pass the saved-set ID as an audience filter.

## Breakdown

Write `breakdown.json` with the same base `filters` and one `breakdown_filter`. For example:

```json
{
  "filters": [{ "filter_id": "age", "selected_range": { "lower": 25, "upper": 40 } }],
  "breakdown_filter": {
    "filter_id": "age",
    "selected_range": { "lower": 25, "upper": 40 }
  }
}
```

```bash
prolific audience breakdown --template-path breakdown.json --workspace WORKSPACE_ID --json
```

This calls `POST /api/v1/eligibility-count/filter-breakdown/`. Base `filters` may include the same nested groups as
count; `breakdown_filter` remains one distributable leaf. JSON output is shaped as
`{"breakdown": {"choice-key": 4, "N/A": 2}}` (illustrative counts). Read the `breakdown` object using
[the chart guidance](charts.md). Numeric bucket boundaries come from the server.

Choose a supported distributable filter with nonempty `selected_values` or a valid `selected_range`. A bare filter ID is
insufficient. On an actionable input validation error, correct the input and retry once. Otherwise report the actual
failure; call a dimension unsupported only when the API response establishes that limitation. Do not replace a failed
breakdown with per-bucket counting. Keep the base audience unchanged while changing the breakdown dimension. Breakdown
selection does not become a recruitment criterion unless the user requests it.
