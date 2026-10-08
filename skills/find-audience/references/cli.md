# Prolific CLI

Everything goes through the configured `prolific` CLI.

Read the workspace from `$PROLIFIC_WORKSPACE_ID` and ask only if it is unset. Don't go hunting for
it: `whoami` and `workspace list` are interactive and don't mark which is active.

## Which command

Use these as written. Omitting the output flag opens an interactive browser that hangs until killed.

| to | command |
|---|---|
| find filters by topic | `prolific filters search <query> --csv -w <ws> --skill find-audience` |
| find a choice inside a filter | `prolific filters choices search <filter-id> <query> --csv -w <ws> --skill find-audience` |
| list a filter's choices (fallback) | `prolific filters choices <filter-id> --csv --all -w <ws> --skill find-audience` |
| resolve a named group | `prolific participant-group search <name> --csv -w <ws> --skill find-audience` |
| resolve a prior study | `prolific study search <name> --csv -w <ws> --skill find-audience` |
| learn how this workspace lets filters combine | `prolific filters rule-tree --json -w <ws> --skill find-audience` |
| count an audience | `prolific audience count --filters '<array>' --json -w <ws> --skill find-audience` |
| split a count by one dimension | `prolific audience breakdown --filters '<array>' --breakdown '{"filter_id":"X","selected_values":["0"]}' --json -w <ws> --skill find-audience` |

Read the CSV directly — it carries the columns you need and is several times smaller than the same
data as JSON, so there is no parsing step.

Only if you need something these invocations don't cover, run `prolific <command> --help`. It is
authoritative where this file is not. Never guess a flag.

## Searching

Two different searches, for two different things.

`filters search` finds **filters**. It tells you a filter exists and what it covers. The `choices`
columns on its results are a preview of at most three matches — never the filter's options.

`filters choices search` finds **choices inside one filter**. This is where selection IDs come from,
and it is the first thing to reach for once you know which filter you want.

Try the words you expect to appear in the text, and try the -nyms: synonyms, abbreviations and their
expansions, the broader term and the narrower one. "GP" returns nothing; "general practitioner"
returns 33 filters and "doctor" another 11. One phrase per call, several in the same turn. An empty
result proves nothing on its own.

Listing a filter's choices is the fallback, for when you cannot name what you are after —
assembling every medical specialty, say. Use `--all`.

Write a list you fetch to a temp file and reuse it. A filter's choices don't change mid-task, so
fetch each one at most once and grep the file for later lookups.

## Traps

- **A count of zero may be a privacy floor**, not an empty pool.
- **If a request fails, say so.** Never fill the gap with a guessed ID.

## Reading the rule tree

The response holds a tree of `and` / `or` nodes. Read its shape from the response rather than
assuming a path.

- A sole top-level `and` / `or` group is the root; otherwise the filters array has an implicit AND
  root.
- A node's `children` gives the permitted child type. `leaf: true` permits ordinary filters; an
  absent group type is not permitted there.
- `max_children` caps immediate children. `max_by_type` caps them per type. Zero is a real limit.
  What may nest depends on position.
- Limits differ between workspaces. Read them; don't assume.

The tree governs structure only. IDs and bounds come from the filters themselves.

## Payload shape

A filter payload is a JSON array. Top-level entries combine with **AND** — UK residents aged 25-40:

```json
[
  { "filter_id": "current-country-of-residence", "selected_values": ["0"] },
  { "filter_id": "age", "selected_range": { "lower": 25, "upper": 40 } }
]
```

- `selected_values` takes choice **IDs**, never labels. Several acceptable values of one criterion
  go in one array.
- `selected_range` takes `{"lower": N, "upper": N}`.
- Never both on the same leaf.

A group is `{"filter_id": "and"|"or", "selected_filters": [...]}` and may nest. Use one when a
requirement needs an OR — UK residents who are 18-25 **or** 60+:

```json
[
  { "filter_id": "current-country-of-residence", "selected_values": ["0"] },
  {
    "filter_id": "or",
    "selected_filters": [
      { "filter_id": "age", "selected_range": { "lower": 18, "upper": 25 } },
      { "filter_id": "age", "selected_range": { "lower": 60, "upper": 99 } }
    ]
  }
]
```

Multiple values of a *single* select filter never need a group — they go in one `selected_values`.

`--breakdown` takes one filter object, not an array and never a group: `selected_values` for a
select filter, `selected_range` for a numeric one. Split by a different criterion from the base
audience — the `N/A` bucket is everyone in the audience who falls outside it, including people who
never answered.
