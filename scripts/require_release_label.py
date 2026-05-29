#!/usr/bin/env python3
"""Require the `release` label on PRs that touch skill folders.

Reads the PR's labels and changed files via `gh pr view`, then:
  - If any changed file lives under skills/<name>/ (any file at any
    depth within a skill folder), the PR MUST carry the `release`
    label.
  - If no skill files changed, the check passes silently.

Args from env (set by the workflow): PR_NUMBER, REPO, GH_TOKEN.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys


def err(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)


def gh_pr_view(pr_number: str, repo: str, fields: str) -> dict:
    result = subprocess.run(
        ["gh", "pr", "view", pr_number, "--repo", repo, "--json", fields],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"error: gh pr view failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def is_skill_file(path: str) -> bool:
    # A "skill change" is any file under a skill folder (skills/<name>/...).
    # The whole folder is the release unit, so a script or reference doc
    # change counts as much as a SKILL.md change.
    parts = path.split("/")
    return len(parts) >= 3 and parts[0] == "skills"


def main() -> int:
    pr_number = os.environ.get("PR_NUMBER", "").strip()
    repo = os.environ.get("REPO", "").strip()
    if not pr_number or not repo:
        sys.exit("error: PR_NUMBER and REPO environment variables are required")

    files_data = gh_pr_view(pr_number, repo, "files")
    changed = [f["path"] for f in files_data.get("files", [])]
    skill_changes = [p for p in changed if is_skill_file(p)]

    if not skill_changes:
        print("OK: no skill files modified; release label not required")
        return 0

    labels_data = gh_pr_view(pr_number, repo, "labels")
    labels = {label["name"] for label in labels_data.get("labels", [])}

    if "release" in labels:
        print(f"OK: skill files modified and 'release' label present ({len(skill_changes)} file(s))")
        return 0

    err(
        "PR modifies skill files but does not carry the 'release' label."
    )
    err("Modified skill files:")
    for path in skill_changes:
        err(f"  - {path}")
    err("Add the 'release' label and bump versions per CONTRIBUTING.md.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
