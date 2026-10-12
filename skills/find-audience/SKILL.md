---
name: find-audience
description: Navigates the Prolific participant pool to find and size an audience. Use when someone asks who is in the pool, which criteria exist, how many participants match, or wants an audience narrowed, widened, counted, or broken down.
version: 0.1.0
---

## Find an Audience

Navigate the Prolific participant pool on a researcher's behalf: work out which of the live filters
describe the people they mean, find out how many match, and refine until the audience fits. Answer
questions about the pool as readily as you assemble a selection from it.

### Bundled references

- [CLI reference](references/cli.md): which command to reach for, the traps, and payload shape. Read
  it before your first command.
- [Chart guidance](references/charts.md): read when turning a breakdown into a chart.

The reference gives the exact invocation for each command. Use those. Reach for
`prolific <command> --help` only when you need something they don't cover, and never guess a flag.

### Rules that never bend

These hold at every step; the rest of this skill assumes them.

1. **Every number comes from a result in this conversation.** Never state a count you did not
   retrieve — not by adding, scaling, interpolating, estimating, rounding, or recalling a figure
   from earlier in the chat. Changed criteria need a fresh count, however small the change.
2. **Never combine counts; request the one you want.** Separate audiences and breakdown buckets do
   not add up to a union, a total, or a count for different criteria — whether or not the categories
   overlap. So when a broad term maps to several candidate filters, count each one *and* build the
   OR'd group and count that as its own request. The union is a count you make, never a sum you
   compute.
3. **Describe a filter in its own words.** Use the filter's title, description, or option label when
   you say who it selects. Shortening and lower-casing are fine; substituting your own terms is not.
   "Qualified AI taskers" is not "AI experts". The researcher must be agreeing to the same
   population the JSON selects.
4. **Never quietly change the audience.** Flattening an OR into an AND, dropping a criterion to get
   a count, or swapping in a proxy are all things you say out loud.
5. **A count of zero is not "nobody".** The API floors small counts to zero to protect participant
   privacy. Report it as "zero or below the reporting threshold".

### Step 1: Establish intent and workspace

From the request and the conversation, identify the audience, any target sample size, and the
workspace. Ask only for what the next step needs.

Resolve the workspace as the CLI reference describes.

Describe people in everyday language, bringing in filter names, IDs, and JSON when you explain a
choice or hand over the payload. Where a choice key appears in prose, show its label next to it.

### Step 2: Find the filters

Search before you propose a criterion or answer what criteria exist. The CLI reference covers how
the two searches differ and how to phrase a query.

Never guess an ID.

Filters that match the same request can select quite different populations. Read each candidate's
question text, selection type, and choices, then explain the deciding differences in those terms
rather than from titles. Present every materially distinct match you found, without implying a
truncated result list is exhaustive.

When the user's own term is ambiguous, pick the sensible reading, name it and the meaningful
alternative out loud, then build and count the best-fitting one in the same turn.

When a missing fact decides the selection, run the lookups that make the question answerable *before*
asking it, then ask with what they return: a choice between two readings comes with a count for each,
a choice between similar filters with whatever tells them apart. Asking without that is asking someone
to already know the catalogue. If they hand the choice back, recommend a default and move on.

When nothing in the catalogue fits, say what is unsupported. Offer broader or proxy criteria and
explain how they differ.

### Step 3: Build and count

Build the payload from the CLI reference, then count that exact audience against that exact
workspace.

Before the first count or breakdown, fetch the workspace rule tree once and keep it. Validate any
group you build against it rather than sending a request the server will reject.

Do this silently. The tree is plumbing — don't narrate fetching it, and don't report rules the
audience never ran into. Mention it only when it actually blocks what the researcher asked for, and
then say what has to change, not what the tree says.

If a structure is not permitted, restructure only where the audience's meaning is unchanged;
otherwise explain the limitation and ask which requirement can move.

Counts are independent of each other. When you have several candidate audiences to size, send every
count in the same turn rather than one round per variant.

Always try the count before calling an audience unsupported.

### Step 4: Refine

For a small audience, propose relaxing a criterion the user has said can move. For an over-broad
one, propose a relevant narrowing choice. Keep their must-haves intact.

Count every variant before you claim its effect, and do not name the criterion that limits the pool
most without the counts to show it.

### Step 5: Breakdowns

If a breakdown is requested with no dimension, ask which one. If you are offering one, offer it
without holding up the audience result.

Use one breakdown request for the dimension and the current base audience, never a count per
category.

### Output contract

Whenever you present an audience, give both halves:

1. **The filters JSON** — the array you passed to `--filters`, verbatim, in a code block.
2. **The count** that exact array returned.

They travel together. A payload with no count is unverified; a count with no payload cannot be
reproduced or reused. Change the filters and both change: recount, and show the new pair.

Answering a question about the pool needs neither. The contract applies when there is an audience to
hand over, not to every turn.
