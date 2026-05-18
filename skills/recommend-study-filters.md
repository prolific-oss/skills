---
name: recommend-study-filters
description: Given a description of your target participant population, fetches all available Prolific filters and recommends the best matching combination with filter IDs and values ready to use.
version: 0.1.0
---

## Recommend Study Filters

When asked to recommend filters for a Prolific study, follow these steps.

### Step 1: Fetch all available filters

Mandatory: run the following Prolific CLI command to understand the filters CLI command.

```bash
prolific filters --help
```

Mandatory: run the following Prolific CLI command to retrieve the full filter catalogue and renders it straight to the terminal for analysis

```bash
prolific filters -n
```

Each filter in the output includes:

- **Filter ID** — the identifier used when configuring a study (e.g. `current-country-of-residence`, `age`)
- **Type** — either `select` (choose from a list of options) or `range` (set lower/upper bounds)
- **Choices** — for `select` filters, a map of choice keys to human-readable labels
- **Min / Max** — for `range` filters, the allowed bounds

### Step 2: Analyse the researcher's requirements

Read the researcher's description carefully and identify every distinct requirement. Group them by category, for example:

- **Geographic** — country of residence, nationality
- **Demographic** — age, gender, ethnicity
- **Educational** — highest qualification, student status
- **Employment** — employment status, occupation, industry
- **Behavioural / experiential** — prior Prolific participation, device ownership, health conditions, parental status, language fluency

Flag any requirements that are ambiguous or may not map to a single filter.

### Step 3: Match requirements to filters

For each identified requirement, find the best matching filter from the Step 1 output:

- Compare the researcher's language to filter titles, descriptions, and questions
- **For `select` type filters**: identify the specific choice key(s) that match (e.g. for a "UK residents" requirement, find the key for "United Kingdom" in the country filter's choices)
- **For `range` type filters**: determine appropriate `lower` and `upper` bounds based on the researcher's stated criteria (e.g. age 25–45 → `lower: 25, upper: 45`)
- Note the exact `filter_id` for every recommended filter

If multiple filters could satisfy the same requirement (e.g. nationality vs. country of residence), explain the difference and recommend the more appropriate one.

### Step 4: Present recommendations

For each recommended filter, provide:

1. **Filter title** and **filter_id**
2. **Selected values** (for `select` type) or **range** (for `range` type), ready to copy into a study configuration
3. A plain-language explanation of why this filter matches the researcher's requirement

Format the selected values in the JSON structure used by the Prolific API so they can be used directly:

- Select filter: `{ "filter_id": "...", "selected_values": ["key1", "key2"] }`
- Range filter: `{ "filter_id": "...", "selected_range": { "lower": X, "upper": Y } }`

If any stated requirement could not be matched to an available filter, say so explicitly and suggest the closest alternative or a workaround.
