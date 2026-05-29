# Prolific Skills

Official skills from Prolific for AI workflows and research following the [agentskills.io](https://agentskills.io) specification.

Includes `prolific-beta-skills` plugin for skills that are currently being evaluated, but made available for experimentation and feedback.

## Installation

Via [agentskills.io](https://agentskills.io):

```bash
npx skills add prolific/skills
```

Or install individual skills:

```bash
# example prolific skill only
npx skills add prolific/skills --skill recommend-study-filters
```

Or natively from Claude Code:

```
/plugin marketplace add prolific-oss/skills
/plugin install prolific-beta-skills@prolific
```

## Documentation

- [Prolific Documentation](https://docs.prolific.com/documentation/get-started/overview)
- [API Reference](https://docs.prolific.com/api-reference/introduction)
- [Prolific CLI](https://docs.prolific.com/documentation/tooling/prolific-cli)

## Versioning & Releases

Each PR that touches a skill ships as a tagged release — expect
frequent small versions. The CHANGELOG.md is the source of truth for
the current version; `.claude-plugin/marketplace.json` mirrors it
and is what Claude Code reads to deliver updates.

The two install paths above detect updates differently — Claude Code
checks `marketplace.json`'s plugin version, while `npx skills`
checks the GitHub tree SHA of the skill folder. Both are well served
by our release-on-merge model. See
[DEVELOPMENT.md → Update Detection Across Install Paths](./DEVELOPMENT.md#update-detection-across-install-paths)
for the full picture; see [DEVELOPMENT.md](./DEVELOPMENT.md) for the
full versioning model and release mechanics.

## Contributing

- See [CONTRIBUTING.md](./CONTRIBUTING.md) for the PR process and commit format
- See [EVALS.md](./EVALS.md) for working on skills and their evals
- See [DEVELOPMENT.md](./DEVELOPMENT.md) for release mechanics

## License

CC0 1.0 Universal

## Author

[Prolific](https://www.prolific.com/)
