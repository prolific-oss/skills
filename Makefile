.PHONY: help validate release changelog

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

validate: ## Validate skill frontmatter and marketplace.json (structural)
	python3 scripts/validate_skills.py
	python3 scripts/validate_marketplace.py

release: ## Stamp the three versions and stub CHANGELOG (Usage: make release VERSION=X.Y.Z)
	@[ -n "$(VERSION)" ] || { echo "Usage: make release VERSION=X.Y.Z"; exit 1; }
	@git diff --quiet --cached || { echo "Index is dirty; commit or unstage staged changes first."; exit 1; }
	python3 scripts/bump_release.py $(VERSION)
	$(MAKE) validate

changelog: ## Regenerate the CHANGELOG stub via git-cliff (Usage: make changelog VERSION=X.Y.Z)
	@[ -n "$(VERSION)" ] || { echo "Usage: make changelog VERSION=X.Y.Z"; exit 1; }
	@command -v git-cliff >/dev/null || { echo "Install git-cliff: brew install git-cliff"; exit 1; }
	git-cliff $$(git describe --tags --abbrev=0 2>/dev/null)..HEAD --tag v$(VERSION) --strip header
