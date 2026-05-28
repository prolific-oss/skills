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

## The Three Versions That Move Together

Every release bumps the same SemVer in three places:

| Field                       | File                                                  | What it controls                                                          |
| --------------------------- | ----------------------------------------------------- | ------------------------------------------------------------------------- |
| `metadata.version`          | `.claude-plugin/marketplace.json` (root)              | Whether `/plugin marketplace update` re-pulls the catalog                 |
| Plugin entry `version`      | `.claude-plugin/marketplace.json` (`plugins[*].version`) | Whether `/plugin update` refreshes the installed plugin for users          |
| Skill frontmatter `version` | `skills/<name>.md` (top-level YAML)                   | Contributor signal + changelog grouping. **Claude Code ignores this.**    |

Why all three move together:

- Bumping only the skill frontmatter changes nothing for users —
  Claude Code does not read that field for update detection.
- Bumping only the marketplace `metadata.version` re-pulls the catalog
  but the plugin entry's pin means `/plugin update` still no-ops.
- Bumping only the plugin entry `version` works for `/plugin update`
  directly, but users who haven't re-pulled the catalog won't see it.

The `make release VERSION=X.Y.Z` target (see [Tooling](#tooling))
edits all three at once so they cannot drift.

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

| Change to a skill                                            | Per-skill bump                |
| ------------------------------------------------------------ | ----------------------------- |
| Trigger criteria narrowed/widened; output schema changed     | MINOR (pre-1.0) / MAJOR (post-1.0) |
| New capability or expanded scope (additive)                  | MINOR                              |
| Prompt wording fix, typo, no behavioural change              | PATCH                              |
| Eval-only or doc-only change                                 | No bump                            |

## Release Workflow

The whole flow is "release on merge" — every skill-touching PR ships
as a tagged release at merge time. There is no separate
maintainer-cuts-release ritual.

1. Contributor edits a skill on a feature branch
2. Contributor runs `make release VERSION=X.Y.Z` to stamp the three
   versions and stub a `## X.Y.Z` section in `CHANGELOG.md`
3. Contributor edits the CHANGELOG stub, commits, pushes, opens PR,
   adds the `release` label
4. CI runs (see [What CI Enforces](#what-ci-enforces))
5. PR is reviewed and merged
6. `.github/workflows/create-release.yml` fires on push to main,
   detects the `release` label, creates the `vX.Y.Z` git tag, and
   publishes a GitHub Release with the CHANGELOG section as the body

## What CI Enforces

| Workflow              | What it catches                                                                          |
| --------------------- | ---------------------------------------------------------------------------------------- |
| `validate.yml`        | Bad commit message; missing/invalid skill frontmatter; missing release label on a skill-touching PR; tag collision; version mismatch across the three sync points |
| `changelog-gate.yml`  | `release`-labelled PR that doesn't modify both `CHANGELOG.md` AND `.claude-plugin/marketplace.json` |
| `create-release.yml`  | Re-checks version match after merge before tagging; fails the release rather than tag inconsistently |

The single most important failure mode these gates prevent is:
"CHANGELOG bumped but `plugins[0].version` forgotten" — users would
get no update and we'd ship a silent no-op release.

## Tooling

| File                                | Purpose                                                                                              |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `cliff.toml`                        | git-cliff config; groups conventional commits by scope (skill name) for CHANGELOG generation         |
| `CHANGELOG.md`                      | Source of truth for the release version; top semver heading drives the tag                           |
| `scripts/changelog.py`              | `extract-version` and `extract-section X.Y.Z` — used by CI to read CHANGELOG                         |
| `scripts/validate_skills.py`        | Asserts every skill has `name`, `description`, valid-semver `version` in frontmatter                 |
| `scripts/validate_marketplace.py`   | Asserts marketplace.json is structurally valid; on release PRs also asserts version sync + no tag collision |
| `scripts/require_release_label.py`  | Asserts that skill-touching PRs carry the `release` label                                            |
| `scripts/bump_release.py`           | Called by `make release`; stamps the three versions and stubs the CHANGELOG section                  |
| `Makefile`                          | `validate`, `release`, `changelog` targets                                                            |

## Prerequisites for the Release Pipeline

These are configured once on the GitHub repo (not via code):

- A `release` label exists on the repo (used to gate `create-release.yml`)
- A `main` GitHub Environment exists with a `REPO_CONTENTS_WRITE`
  secret (a PAT with `contents: write` scope), used by
  `create-release.yml` to push the tag and create the GitHub Release

## Release Channels (Future)

Per [Anthropic's release channels guidance](https://code.claude.com/docs/en/plugin-marketplaces#set-up-release-channels),
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

**Deferred until v1.0.** Trigger to revisit: first skill graduates
from beta, or first external Prolific team adopts the marketplace at
scale.
