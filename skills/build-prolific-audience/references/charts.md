# Charts from breakdown JSON

Use the host's charting tools or a standard plotting library. This is presentation over the shared breakdown result,
not a local implementation of eligibility.

## Read the response

Run `audience breakdown` with `--json`, check that it succeeded, and read the complete JSON response. Keep the response
and input audience/dimension together so the chart can be checked against its source. The response has this shape
(illustrative counts only):

```json
{"breakdown": {"0": 4, "1": 3, "N/A": 5}}
```

Read category keys and nonnegative integer counts from `breakdown`. Preserve keys as strings, every returned bucket,
zero counts, and N/A. An empty object does not justify inventing zero-valued categories. If the response is missing,
malformed, truncated, or has invalid counts, explain the issue rather than guessing chart data.

Map keys to readable labels using the current breakdown filter's catalogue choices. Retain keys alongside labels when
needed to distinguish collisions; mark unmapped keys explicitly. Keep numeric bucket boundaries exactly as returned.
The current response has no separate suppression metadata. Plot zeros as reported values, not proof that nobody
qualifies. Preserve any suppression annotations if the API later supplies them.

## Plot

Generate a bar chart with a zero-based count axis and readable category labels. Include the audience and breakdown
dimension in the title or caption, and explain N/A as outside the selected values/range or unanswered. Compare plotted
labels and counts with the JSON before presenting the chart. Save and link PNG or SVG when using file-based plotting.
Show a target line or markers when comparing groups against supplied sample targets.

Never sum breakdown buckets or separate audience counts to derive eligibility totals, unions, or counts for different
criteria. Use a count request for the exact criteria instead. Do not normalize bucket sums into shares of people or use
a pie chart. Re-run breakdown if the base audience changes. If the host cannot plot, provide a labelled table and state
that no chart was generated.
