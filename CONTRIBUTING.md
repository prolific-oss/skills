# Contributing to `prolific/skills`

Thank you for contributing. This guide covers what you need to know before opening a pull request. Contributions are restricted to Prolific engineers.

For the deeper "why" — version-resolution rules, bump semantics, release
mechanics — see [DEVELOPMENT.md](DEVELOPMENT.md).

## Pull Request Process

1. **Branch from `main`** — create a working branch for your changes
2. **Make your changes** — follow patterns in existing skills
3. **If you touched a skill, prepare a release** — see [Release-on-merge model](#release-on-merge-model) below
4. **Commit using conventional format** — see [Commit Message Format](#commit-message-format)
5. **Push and open a PR** — include a summary; if it's a release, add the `release` label
6. **Wait for review** — 1 approval from a Prolific maintainer is required
7. **Merging** — only Prolific staff merge PRs

## Release-on-merge Model

This repo ships releases per merge, not in scheduled batches. The rule is simple:

- **If your PR changes any file under `skills/`** (each skill lives in its own folder; the whole folder is the release unit), it **is** a release. Add the `release` label.
- **If your PR is pure docs, CI, scripts, or repo-chore work**, it is not a release. Do not add the label.

When your PR is a release, you must update **three** things in the same PR:

1. **Skill frontmatter `version:`** on every skill you changed, per the [bump rules](DEVELOPMENT.md#bump-rules)
2. **`.claude-plugin/marketplace.json`** — `metadata.version` to the new release-train number (severity = max severity of all skills changed in your PR), and the `version` of **each plugin whose skills you changed** to that plugin's own next version. Unchanged plugins keep their current version.
3. **`CHANGELOG.md`** — add a new `## X.Y.Z` section at the top describing your change, grouped under `### <skill-name>` headings

The fastest way to do steps 1–3 mechanically is:

```bash
make release VERSION=X.Y.Z
```

This runs `scripts/bump_release.py`, which stamps `metadata.version` to
the train number, bumps the `version` of every changed plugin and skill
by its own inferred severity (`feat`→minor, else patch), and stubs a
fresh `## X.Y.Z` section in `CHANGELOG.md` for you to edit. The per-unit
bumps are *suggestions* — review the diff, adjust any version and the
stub, then commit, push, open the PR, add the `release` label. See
[How The Versions Move](DEVELOPMENT.md#how-the-versions-move) for why
each plugin versions independently.

### Version collisions

If your PR sits in review while another release PR merges first,
CI will fail your PR — the version you bumped to is already taken
(either as a git tag or as the top heading in CHANGELOG.md). Rebase
on main and re-run `make release VERSION=<next>`. The collision check
is there to make sure you never silently overwrite someone else's
release.

## Commit Message Format

Commits follow conventional commit format, enforced by CI:

```
type(scope): description
```

**Valid types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `build`, `perf`, `style`, `revert`

The first six (`feat`, `fix`, `docs`, `refactor`, `perf`, `revert`) appear in release notes. The rest are skipped from the changelog.

**Use the skill name as scope** for any commit that touches a skill:

```
feat(recommend-study-filters): add step for handling ambiguous demographic requirements
fix(recommend-study-filters): correct filter_id format in JSON output
feat(workspace-management): add new skill
docs: update install instructions in README
chore: bump eval dependencies
```

**Bad examples:**

```
fixed stuff                                  # no type, vague description
feat: Update recommend-study-filters.        # capitalised, trailing period
FEAT(recommend-study-filters): added step    # uppercase type, past tense
```

## Code Review

Expect a review within approximately one week. Feedback is constructive — we're all here to build something great together.

## License

This project is licensed under [CC0 1.0 Universal](LICENSE.md). By contributing, you agree that your contributions will be licensed under the same terms.
