# Changelog

All notable changes to `prolific/skills` are listed here. Each
release cuts a `vX.Y.Z` git tag and a GitHub Release whose body is
the corresponding section below.

For the versioning model (the release-train number vs. independent
per-plugin versions), see
[DEVELOPMENT.md](./DEVELOPMENT.md#how-the-versions-move).

## 0.5.2

_Plugins: prolific-beta-skills 0.4.1 to 0.4.2_

### find-audience

- [fix] Match specialist audience recommendations to the strongest relevant qualification evidence, with concise, source-backed guidance across Domain Expert pools. Preserve explicit self-report and occupational requests. Add regression and generalisation scenarios for coding, language, healthcare and STEM tasks, including unavailable qualification details. Retry blocked read-only lookups through the environment's network-permission flow without inventing fallback audiences.

## 0.5.1

_Plugins: prolific-beta-skills 0.4.0→0.4.1_

### batch-task-create

- [fix] Stops before creating a study, checks the dataset import result before creating the batch, and documents layout behaviour that was wrong or unclear: free-text boxes are required unless `optional` is set, `disable_dropdown` for radio buttons, shared column heights, one use per dataset field per page, `batch update` after setup, and failure modes for schema-less datasets, partial imports and rejected `style` attributes.

## 0.5.0

### find-audience

- [feat] New skill: navigates the Prolific participant pool to find and size an audience, using the CLI's catalogue, search, count, and breakdown commands. Covers named group/study lookup, nested AND/OR criteria, and breakdown charts. Added to `prolific-beta-skills` (0.4.0), with an eval dataset under `evals/find-audience/`.

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
