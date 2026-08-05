# Annotated exemplars

Three real `#prolific-tech-announcements` posts, chosen for the highest engagement (reactions + thread replies) and for showing the arc from SKILL.md in different situations: a revenue/integration milestone, a competitive B2B product release, and a UI-capability release with a demo. Study the *moves*, not the exact wording — reuse the structure and the framing instincts, not the phrasing.

Slack syntax is preserved verbatim: `*bold*`, `_italic_`, `:emoji:`, `<url|text>`, and team handles like `<!subteam^ID>`.

---

## Example 1 — Revenue/integration milestone (top all-time, 114 reactions / 16 replies)

```
:google-gemini: *Google Nexus* *API integration live, unlocking $100m+ potential*
The Gemini Human Data API integration is live and the first tasks have successfully landed. This is the first end-to-end exchange of this type and such an exciting milestone. We know from <@Bryce Sheppard> that Scale were running >$100m worth of business for Johannes Mauerer's team at Google by integrating with this API and demonstrating high data quality. This integration is the first step, we are now eligible to compete for this same huge slice of the :google-redesign: pie. :muscle:

*What we built*
Google sends a notification via their API when a new batch of tasks is ready. We fetch the task data and stand up the annotation project in HumanSignal automatically. From there we fire a Slack notification and <!subteam^services> reviews the request, runs the study and manages delivery. Once complete, we extract the results and submit them back to Google via the same API.

*What comes next*
• ~Test run complete, first data returned to Google~ :status-done:
• ~200-task pilot batch follows
• Then the large volume projects this integration was built for :prolific-rocket:
```

**Why it works**
- **Headline is pure outcome + number.** The mechanism ("Gemini Human Data API") is present but the *stakes* ("unlocking $100m+ potential") lead.
- **Hook is all customer/competitive/revenue framing** — names Google, the competitor (Scale), the buyer (Johannes' team), and the size of the prize — before any implementation.
- **"What we built" is quarantined** into one block and stays plain-language.
- **"What comes next" as a checklist** with shipped items struck through and `:status-done:` — shows momentum.
- No Loom, no metric-heavy proof section — and it didn't need them, because the revenue framing carried it.

---

## Example 2 — Competitive B2B product release (78 reactions / 22 replies)

```
:briefcase: B2B Expert Network — MVP is live

hey all, really excited to share that the B2B Expert Network MVP is now live for select partners, following the collaboration between <!subteam^expert-network> and <!subteam^integrity>

• you can now combine the professional filters with the wide range of existing filters researchers already use, in a single query
• a new job-title filter with a verification level selector, so researchers can require 'Additional Verification' backed by corroborated participant attributes
• custom reward-rate constraints enforced per question per verification level, configurable by admins without a deploy and snapshotted at publish

*why it matters*
• gives partners the credible, verifiable B2B panel they need as our competitor (user interviews) sunset their partner API contracts
• leans into our biggest differentiator of integrity & trust
• lays the foundation for the wider Expert Network and AI domain experts to build on the same attribute + verification layer

Today we already have ~70k verified B2B expert participants available for researchers — <https://eu.hex.tech/...|up-to-date counts in this hex dashboard>.

The plan is to soft launch to select partners, then open to GA later. We can enable it workspace-by-workspace if you want to experiment — reach out to me with a workspace ID.
```

**Why it works**
- **Separates "what" from "why it matters"** into two labelled blocks — the why is explicitly about a competitor sunsetting contracts and about Prolific's differentiator.
- **Hard number as proof** (`~70k verified` participants) with a **live dashboard link** for anyone who wants to verify.
- **Clear, low-friction CTA** ("reach out with a workspace ID") and named owning teams as a credit line.
- **Strategy tie without OKR jargon** — "our biggest differentiator of integrity & trust", "foundation for the wider Expert Network".

---

## Example 3 — UI capability release with a demo (65 reactions / 30 replies)

```
:aitb: _*Configurable task layouts in AITB | Side by side comparison and more!*_

One of the reasons our internal teams have chosen other tools over AITB has been task layout flexibility — other tools let you decide exactly where the stimulus sits and how the screen is split. AITB had a fixed layout. Our internal <!subteam^services> team are our most accessible customers and the strongest proof point for whether AITB can compete: if we win them, we validate that self-serve customers will make the same choice.

*What <!subteam^aitb> built*
Researchers can now define their task layout. Each page is rows; each row has one or two columns; each column holds:
• A dataset field — the datapoint to annotate (image, text, audio…)
• An instruction — a question or input (radio, text, rating scale…)
• A content block — supporting text, headers, context

Check it out in action <https://www.loom.com/share/...|on Loom> :loom:

*What's next*
This was the foundation for multi-modal evals — before the end of June we'll release image, video and audio in the task UI! :exciting:

:we-win-together-emoji: *How we win together*
<!subteam^services> keen to work with you on where this fits current/upcoming projects — reach out if you have an opportunity that might now suit AITB.
```

**Why it works**
- **Leads with a hypothesis/why** ("if we win our internal teams, we validate self-serve customers will choose us too") rather than the feature — reframes an internal tool change as a strategic bet.
- **Frames internal teams *as customers*** — a very Prolific move that ties any internal tooling release back to customer value.
- **Loom link near the top** to demo the UI, exactly where a capability post should put it.
- **Explicit, well-labelled ask** at the end aimed at the specific team that can act on it.
- Light on hard numbers, but the strategic framing + demo carried it — proof that when you don't have a metric, strong framing plus a visual can still land.

---

## What the low-engagement posts got wrong (avoid these)

- **Engineering-first framing** — opening on the implementation ("we added participant-projects endpoints…") with the customer value buried or absent.
- **Recurring status updates** ("biweekly payments update", "weekly pulse") with no single point and no number — these consistently underperformed.
- **No ask, no tag, no link** — nothing for the reader to do or verify.
- **Dense paragraphs** with no bullets or bold, so nothing survives a glance.
