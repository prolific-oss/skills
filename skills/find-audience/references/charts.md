# Charts from breakdown JSON

A chart here is a bar chart of one audience, split by one dimension.

Every bar comes from the breakdown response. Never invent, extend, or adjust one.

## IDs and labels

- The **ID** is identity, straight from the response. It is what you match on.
- The **label** is display. Map IDs to labels using that filter's choices.

Keep IDs exactly as returned, `N/A` and numeric bucket boundaries included. Where two IDs would
show the same label, print the ID beside it. Mark one you could not map rather than guessing.

## Plot

Bar chart, zero-based count axis, readable labels. Name the audience and the dimension in the title
or caption, and explain `N/A` as outside the dimension's values, or unanswered.

Plot zeros as reported — the API floors small counts for privacy, so a zero is not proof that nobody
qualifies. Do not sum buckets, turn them into shares of people, or use a pie chart.

If the host cannot plot, give a labelled table and say that no chart was generated.
