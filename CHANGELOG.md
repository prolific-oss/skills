# Changelog

All notable changes to `prolific/skills` are listed here. Each
release cuts a `vX.Y.Z` git tag and a GitHub Release whose body is
the corresponding section below.

For the versioning model (the release-train number vs. independent
per-plugin versions), see
[DEVELOPMENT.md](./DEVELOPMENT.md#how-the-versions-move).

## 0.4.0

### batch-task-create

- [feat] New skill: creates a Prolific AI Task Builder batch from a researcher-provided dataset by generating the dataset schema, building the `batch_items` layout, and executing the CLI workflow. Added to the `prolific-beta-skills` plugin.

## 0.3.0

### New plugin: adds new prolific skills plugin, aside from the current beta skills plugin, to hold well evaluated skills.

- [feat|fix] <describe the change>

## 0.2.0

### whoami

- [feat] New skill: reports the currently authenticated Prolific account (name, email, researcher ID, and active workspace) by running the Prolific CLI's `prolific whoami` command. If the CLI is unavailable or unauthenticated, it declines to guess rather than fabricating an identity.

## 0.1.1

### recommend-study-filters

- [refactor] Restructure to the agentskills.io folder convention: the skill now lives at `skills/recommend-study-filters/SKILL.md` (was `skills/recommend-study-filters.md`). No behavior change.

## 0.1.0

### recommend-study-filters

- [feat] Initial release: given a description of a target participant population, fetches all available Prolific filters and recommends the best matching combination with filter IDs and values ready to use
