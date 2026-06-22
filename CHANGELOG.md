# Changelog

All notable changes to `prolific/skills` are listed here. Each
release cuts a `vX.Y.Z` git tag and a GitHub Release whose body is
the corresponding section below.

For the versioning model (why three places move together, what each
controls), see [DEVELOPMENT.md](./DEVELOPMENT.md#the-three-versions-that-move-together).

## 0.2.0

### whoami

- [feat] New skill: reports the currently authenticated Prolific account (name, email, researcher ID, and active workspace) by running the Prolific CLI's `prolific whoami` command. If the CLI is unavailable or unauthenticated, it declines to guess rather than fabricating an identity.

## 0.1.1

### recommend-study-filters

- [refactor] Restructure to the agentskills.io folder convention: the skill now lives at `skills/recommend-study-filters/SKILL.md` (was `skills/recommend-study-filters.md`). No behavior change.

## 0.1.0

### recommend-study-filters

- [feat] Initial release: given a description of a target participant population, fetches all available Prolific filters and recommends the best matching combination with filter IDs and values ready to use
