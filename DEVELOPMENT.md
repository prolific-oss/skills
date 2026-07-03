# Development & Release Mechanics — `prolific/skills`

This document explains how versioning and releases work in this repo,
and what CI enforces. For day-to-day contribution rules (commit format,
when to add the `release` label), see [CONTRIBUTING.md](CONTRIBUTING.md).

## Anthropic Version Resolution

Per the [plugin marketplace docs](https://code.claude.com/docs/en/plugin-marketplaces#version-resolution-and-release-channels),
Claude Code resolves a plugin's version from the first of these that
is set:

1. `version` in the plugin's `plugin.json`
2. `version` in the plugin's marketplace entry (our case — set in
   `.claude-plugin/marketplace.json` under the `prolific-beta-skills`
   plugin)
3. The git commit SHA of the plugin's source

Two consequences shape the whole release process:

- **Setting `version` pins the plugin.** Pushing new commits without
  bumping `version` does nothing for existing users — Claude Code
  sees the same version and keeps its cached copy. Every release MUST
  bump the plugin's `version` in `marketplace.json`, otherwise users
  get no update.
- **`plugin.json` always wins silently** if both it and the marketplace
  entry declare a version. To keep one source of truth, we set
  `version` only in the marketplace entry and ship no `plugin.json`
  for `prolific-beta-skills`.

The marketplace itself also has its own `metadata.version` in
`.claude-plugin/marketplace.json`. This is separate from any plugin
version and is what `/plugin marketplace update` uses to decide
whether to re-pull the catalog.

**Skill-level `version:` in skill frontmatter is NOT part of Claude
Code's resolution chain.** It is metadata for contributors, reviewers,
and changelog tooling only. Bumping a skill's frontmatter version
without bumping the plugin's version in the marketplace entry will
**not** deliver the change to users.

## How The Versions Move

The marketplace can host **multiple plugins** (e.g. `prolific-beta-skills`
plus a future `prolific-stable-skills`). A release bumps a single
release-train number, but each plugin carries its **own** semver and moves
only when its own skills change — so users of an untouched plugin are never
re-delivered a no-op "update".

| Field                       | File                                                     | Bumped when                                                                                       |
| --------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `metadata.version`          | `.claude-plugin/marketplace.json` (root)                 | **Every release.** It is the release-train number — drives `/plugin marketplace update` re-pulls, the git tag, and the GitHub Release. Equals the top CHANGELOG heading. |
| Plugin entry `version`      | `.claude-plugin/marketplace.json` (`plugins[*].version`) | **Only when one of that plugin's own skills changed**, by that plugin's own severity. Drives `/plugin update` for that plugin's users. |
| Skill frontmatter `version` | `skills/<name>/SKILL.md` (top-level YAML)                | When that skill changes, by its own severity. Contributor signal + changelog grouping. **Claude Code ignores this.** |

A plugin's `version` therefore reads as "the version of this plugin",
advancing independently of the train. An untouched plugin keeps its
number across releases — that is intentional, so Claude Code does not
re-deliver an identical plugin as a phantom update.

There is still exactly **one** git tag (`v<metadata.version>`) and **one**
GitHub Release per release. `metadata.version` is the release-train number;
plugin versions are passengers stamped only when they actually changed.

`make release VERSION=X.Y.Z` (see [Tooling](#tooling)) stamps
`metadata.version` to the train number, bumps the `version` of every plugin
whose skills changed (and every changed skill's frontmatter) by its own
inferred severity, and stubs a `## X.Y.Z` CHANGELOG section with a
per-plugin version summary. The severities are *suggestions* — review and
adjust the numbers before committing. CI enforces the invariant on
release-labelled PRs: `metadata.version` == top CHANGELOG version, the tag
is not already taken, every plugin with changed skills is bumped above its
previous version, and every plugin without changes keeps its version.

## Update Detection Across Install Paths

This repo is installable two ways. They detect updates via completely
different mechanisms, and both are supported by our release model
without any extra work.

| Install path                                                                                   | What it reads to detect updates         | When users see an update                                |
| ---------------------------------------------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------- |
| `/plugin install ...@prolific` (Claude Code)                                                   | the installed plugin's `version` in `marketplace.json` | When that plugin's `version` is bumped (our release model) |
| `npx skills add prolific/skills` ([vercel-labs/skills](https://github.com/vercel-labs/skills)) | GitHub Trees API → skill folder SHA     | When any file in the skill folder changes               |

### Claude Code marketplace path

Uses [Anthropic's version-resolution chain](#anthropic-version-resolution).
Updates are deliberate: a user only sees a new version when we bump that
plugin's `version` in `marketplace.json`. Push commits without a
version bump and existing installs stay frozen on the cached copy.
This is what most of this document is about.

### npx skills path

The `vercel-labs/skills` CLI tracks installed skills in a
`.skill-lock.json` file (see
[`src/skill-lock.ts`](https://github.com/vercel-labs/skills/blob/main/src/skill-lock.ts)).
Each entry stores a `skillFolderHash` — the GitHub tree SHA of the
skill's folder. The source comment is explicit:

> This hash changes when ANY file in the skill folder changes.

So `npx skills update` sees an update available whenever a skill
file changes on `main`, regardless of any version field. The
frontmatter `version:` and a hypothetical `plugin.json` are
informational metadata for this path — not the trigger for update
detection.

### Consequences for our release model

- **Both audiences are well served by release-on-merge.** Every
  skill-touching PR cuts a tag (good for Claude Code users) AND
  changes the file (good for npx users). The two paths stay in sync.
- **npx users may see the update slightly sooner** — they see it as
  soon as `main` advances, while Claude Code users see it after
  `create-release.yml` tags + publishes the GitHub Release (seconds
  to a minute later in practice).
- **The `release` label gate is doubly important.** If a PR slipped
  in skill changes without the label, Claude Code users would not get
  an update (no version bump) but npx users would (tree SHA changed
  anyway). `scripts/require_release_label.py` prevents that
  divergence at PR time.

## Bump Rules

The release-level bump severity for a PR is the **max** severity across
all skills the PR touches. New skills always trigger MINOR.

### Release-level bump

| Change                                                                    | Bump                               |
| ------------------------------------------------------------------------- | ---------------------------------- |
| Incompatible change to skill API (removes steps, renames required fields) | MINOR (pre-1.0) / MAJOR (post-1.0) |
| New skill added                                                           | MINOR                              |
| Skill improvement, clarification, bug fix                                 | PATCH                              |
| Docs, eval changes, CI, chore                                             | No bump (no release PR opened)     |

Pre-1.0 (current state): MAJOR stays `0`; MINOR signals breaking
changes.

### Per-skill bump (contributor-facing)

A contributor touching a skill bumps **only that skill's frontmatter
`version`** in their PR, plus marketplace.json + CHANGELOG.

| Change to a skill                                        | Per-skill bump                     |
| -------------------------------------------------------- | ---------------------------------- |
| Trigger criteria narrowed/widened; output schema changed | MINOR (pre-1.0) / MAJOR (post-1.0) |
| New capability or expanded scope (additive)              | MINOR                              |
| Prompt wording fix, typo, no behavioural change          | PATCH                              |
| Eval-only or doc-only change                             | No bump                            |

## Release Workflow

The whole flow is "release on merge" — every skill-touching PR ships
as a tagged release at merge time. There is no separate
maintainer-cuts-release ritual.

1. Contributor edits a skill on a feature branch
2. Contributor runs `make release VERSION=X.Y.Z` (the release-train
   number) to stamp `metadata.version`, bump each changed plugin and
   skill by its own severity, and stub a `## X.Y.Z` section in
   `CHANGELOG.md`
3. Contributor edits the CHANGELOG stub, commits, pushes, opens PR,
   adds the `release` label
4. CI runs (see [What CI Enforces](#what-ci-enforces))
5. PR is reviewed and merged
6. `.github/workflows/create-release.yml` fires on push to main,
   detects the `release` label, creates the `vX.Y.Z` git tag, and
   publishes a GitHub Release with the CHANGELOG section as the body

## What CI Enforces

| Workflow             | What it catches                                                                                                                                                   |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `validate.yml`       | Bad commit message; failing script unit tests; missing/invalid skill frontmatter; missing release label on a skill-touching PR; tag collision; `metadata.version` ≠ CHANGELOG; a changed plugin not bumped or an unchanged plugin bumped |
| `changelog-gate.yml` | `release`-labelled PR that doesn't modify both `CHANGELOG.md` AND `.claude-plugin/marketplace.json`                                                               |
| `create-release.yml` | Re-runs the strict marketplace check after merge before tagging; fails the release rather than tag inconsistently                                                              |

The single most important failure mode these gates prevent is:
"a plugin's skills changed but its `version` was forgotten" — that
plugin's users would get no update and we'd ship a silent no-op release.
The mirror image is also caught: bumping a plugin whose skills did not
change, which would push a phantom update to its users.

## Tooling

| File                               | Purpose                                                                                                     |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `cliff.toml`                       | git-cliff config; groups conventional commits by scope (skill name) for CHANGELOG generation                |
| `CHANGELOG.md`                     | Source of truth for the release version; top semver heading drives the tag                                  |
| `scripts/changelog.py`             | `extract-version` and `extract-section X.Y.Z` — used by CI to read CHANGELOG                                |
| `scripts/validate_skills.py`       | Asserts every skill has `name`, `description`, valid-semver `version` in frontmatter                        |
| `scripts/validate_marketplace.py`  | Asserts marketplace.json is structurally valid; on release PRs also asserts the per-plugin bump invariant + no tag collision |
| `scripts/tests/`                   | `unittest` coverage for the pure validator helpers (run by the `unit-tests` CI job)                         |
| `scripts/require_release_label.py` | Asserts that skill-touching PRs carry the `release` label                                                   |
| `scripts/bump_release.py`          | Called by `make release`; stamps the train, bumps changed plugins/skills by their own severity, stubs the CHANGELOG section |
| `Makefile`                         | `validate`, `release`, `changelog` targets                                                                  |

## Prerequisites for the Release Pipeline

A one-time setup on the GitHub repo (not via code):

- A `release` label exists on the repo (used to gate `create-release.yml`)

The release workflow uses the default `GITHUB_TOKEN` with an explicit
`contents: write` permission on the release job — no PAT or GitHub
Environment setup is required.

## Adding a New Plugin

The marketplace holds an array of plugins, so adding a second one (e.g.
`prolific-stable-skills`) is a manifest edit — the validator and stamper
already iterate every plugin.

1. Add an entry to `plugins[]` in `.claude-plugin/marketplace.json`:

   ```json
   {
     "name": "prolific-stable-skills",
     "description": "…",
     "source": "./",
     "strict": false,
     "version": "0.1.0",
     "skills": ["./skills/<name>"],
     "author": { "name": "Prolific" }
   }
   ```

   Pick a sensible **starting** `version` — a brand-new plugin has no
   previous tag, so the per-plugin bump guard leaves it alone on the
   release that introduces it.
2. Do **not** add a `plugin.json` — `version` lives only in the
   marketplace entry (see [Anthropic Version Resolution](#anthropic-version-resolution)).
3. A skill may be listed under more than one plugin. Changing that skill
   marks **every** owning plugin as changed, so each is bumped (by its own
   severity) on the next release.
4. After the introducing release, the plugin's `version` advances on its
   own — only when one of its skills changes — independently of the train
   and of the other plugins.

## Release Channels (Future)

As per [Anthropic's release channels guidance](https://code.claude.com/docs/en/plugin-marketplaces#set-up-release-channels),
`stable`/`latest` channels are implemented as **two marketplace JSONs
pointing at different git refs of the same repo**, not as branches
inside a single marketplace JSON:

- `marketplace.json` on a `stable` branch — pinned to released
  versions, advanced manually by maintainers cherry-picking from `main`
- `marketplace.json` on `main` — every release lands here first

Each channel must resolve to a **different `version` string** at any
given time, or Claude Code dedupes them and skips the update. Because
we set `version` explicitly (not commit SHA), this constraint is
naturally satisfied as long as `stable` lags `main`.

**Deferred until v1.0.** Trigger to revisit: skills graduate
from beta
