---
name: release-tech-announce
description: Drafts a punchy, company-wide internal Slack announcement for a Prolific product or feature release, pulling the real facts from a Linear ticket, GitHub PR, or Notion/Slack doc so nothing is hand-copied. This is for internal release comms (telling the company what shipped), not external go-to-market. Use this whenever someone wants to announce, post, or write up a release, ship, feature, integration, or milestone internally — even if they just say "help me write the comms for X", "draft a Slack post for this release", "roast/polish my announcement", or paste a ticket/PR link and ask for an announcement. Reverse-engineered from Prolific's highest-engagement announcements and PM "roast my comms" feedback.
version: 0.1.0
---

## Release tech announcement

Help the user write an internal release announcement for `#prolific-tech-announcements` (or a team channel) that reads like the posts that actually land at Prolific: impact-first, framed in customer value, backed by a real number, and easy to skim in 15 seconds. This is internal comms — telling the company what just shipped and why it matters — not an external marketing launch.

The goal is not to fill in a template. It's to make one point land: **what did we just make possible, for which customer, and why does it matter to the business.** Everything below serves that.

### The shape of a great post (learned from what works)

The highest-engagement release posts follow this arc. Not every post needs all eight parts, but the top posts nail 1 → 3 → 4 → 5/6, and the biggest differentiator is the strength of the customer/strategy framing plus a concrete number.

1. **Headline** — emoji + bold, `feature | benefit`, with a metric or customer baked in. Lead with the logo/product emoji.
2. **Hook / why it matters** (1–3 sentences) — the customer need, named customer, competitive threat, or revenue/strategic stakes. This is where you win or lose the reader.
3. **What we built / what's now live** — plain-language, bulleted capabilities. Credit the owning team here.
4. **Why it matters** — tie to a customer outcome, an OKR/KR, or an explicit hypothesis.
5. **Proof** — a hard number, a baseline→now, or a verbatim customer quote.
6. **Visual** — a Loom, screen recording, or screenshots (see below).
7. **What's next / coming soon** — short roadmap bullets.
8. **Links + tag + ask** — docs/dashboard links, the owning team as a credit/shoutout, and one clear call to action (or an explicit "no ask").

See `references/examples.md` for three annotated real posts (including the all-time top performer) showing this arc in the wild. Read it before drafting your first announcement so the voice is calibrated.

### Step 1 — Get the real facts from the source

The user will usually point you at where the facts live rather than retype them. Pull from whatever they give you:

- **Linear ticket / project** — use the Linear tools to read the issue, its description, and status. Grab what shipped, the customer/team it's for, any metrics or links.
- **GitHub PR** — use `gh pr view <url> --json title,body,files` (or the GitHub tools) to see what actually changed and read the description.
- **Notion / Slack doc** — fetch and read it for context, metrics, and customer references.
- **Rough notes / a rough draft** — work from what they pasted; polish rather than replace their voice.

Extract and hold onto: what shipped (in plain language), who it's for (named customer or internal team), the metric/proof, any demo link, and the relevant links (docs, dashboard, project). If a source link is given, read it — don't guess at what a ticket says.

### Step 2 — Find the gaps, then ask (don't fabricate)

The elements that separate a great post from a forgettable one — a hard number, a customer quote, a Loom, a strategy tie — are often *not* in the ticket. Once you've drafted from the source, tell the user what's missing and ask for it. Never invent a metric, a customer quote, or a Loom link. A specific, honest number beats an impressive fake one, and a fabricated quote is a real risk.

Ask specifically, e.g.: "Do you have a number for impact (revenue, volume, time saved, adoption)?" · "Is there a customer or internal team we can name, or a quote?" · "Is there a Loom or screenshot?" · "Which H2 priority does this ladder up to?" If they don't have one, that's fine — lean harder on the framing you *do* have (see `references/strategy.md` for how to tie to strategy, and the "don't block on the demo" note below).

### Step 3 — Draft it, punchy and scannable

Write for how people read Slack: assume ~80% will glance and ~20% will deep-dive. Design for the glance.

- **Headline does the heavy lifting.** Put the *outcome* in the title, not the mechanism. "Google API integration live, unlocking $100m+ opportunity" beats "Google sent us tasks via the Gemini Human Data API." If there's a number, put it in the headline.
- **Lead with the why.** Get the strategic/customer context above the operational detail so an exec or a distant reader gets the point first. Don't make them read "what we built" to find out why they should care.
- **Frame everything in customer value.** Translate features into what they let a customer *do* or what risk they remove. Keep implementation in its own "what we built" block — and keep it non-technical. If you're writing about queues, retries, or endpoints, find the plain-language version.
- **Bring a number.** If you genuinely can't, lean on impact framing and a verbatim qualitative quote instead — and it's fine to say quantitative confirmation is still pending.
- **Bullets over paragraphs.** Every strong post uses short bulleted lists. Bold the section labels.
- **Length: aim for ~150–350 words.** If it's running long, push the deep detail into a thread reply and keep the top-level post skimmable.
- **One clear ask.** If you want feedback or action, put the ask near the top and tag the specific people who need to see it — tagging is what gets the right eyes on it. If it's purely an FYI, say so ("no ask, just sharing").
- **Show, don't just tell** — but ship now. A Loom or screenshot brings it to life; put the link near the top ("above the fold"). If the demo isn't ready, post anyway and say it's coming — a smaller update now beats a perfect one later.
- **Tie to strategy** where it's genuine. See `references/strategy.md` for the current priorities and the "right to win" framing to connect to. Don't force it.

Match Slack's formatting syntax (this is what renders correctly and matches the house style):

- `*bold*` for the headline and section labels, `_italic_` for asides.
- `:emoji:` — lead with a product/customer logo emoji; celebratory custom emoji (`:heart-prolific:`, `:prolific-rocket:`, `:tada:`) are part of the culture. Use them to punctuate, not to decorate every line — heavy emoji walls hurt readability for part of the audience.
- Links as `<https://url|readable text>`, not bare URLs.
- Tag teams with their Slack group handle and people with `@name`. Place team credit in the "what we built" line or as an end shoutout.

### Step 4 — Self-check before handing it back

Read the draft once as a busy exec who will only see the first two lines, then run this check:

- Does the **headline** state an outcome, ideally with a number or a customer?
- In the **first 2 lines**, is it clear what this makes possible and why it matters?
- Is there a **concrete number** or, failing that, a customer quote/named need?
- Is the technical detail **quarantined** and non-technical elsewhere?
- Is there a **visual** (or an honest "demo coming")?
- Is the **ask explicit** (or explicitly "no ask"), and are the **right people/teams tagged**?
- Is it **≤ ~350 words** and scannable in a glance?
- Does it **ladder up to a strategic priority** where genuine?

Present the draft in a copy-pasteable Slack code block, then note any gaps you flagged in Step 2 that the user still needs to fill (e.g. "add the Loom link here", "confirm the $ figure"). Offer to tighten tone, cut length, or produce a threaded version if the post is long.

### Reference files

- `references/examples.md` — three annotated, real high-engagement posts. Read before your first draft to calibrate voice and structure.
- `references/strategy.md` — Prolific's current strategic priorities and "right to win" framing, for the strategy tie in Step 3. Check it's current before leaning on specifics.
