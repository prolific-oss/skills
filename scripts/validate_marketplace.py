#!/usr/bin/env python3
"""Validate .claude-plugin/marketplace.json.

Always checks:
  - metadata.version is valid semver
  - every plugins[*].version is valid semver
  - every skill listed under plugins[*].skills resolves to an existing file

With --strict (used on release-labelled PRs), additionally checks:
  - metadata.version == plugins[0].version == top CHANGELOG version
  - v<version> does not already exist as a git tag

Exits non-zero on any failure with a clear per-issue error.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")


def err(msg: str) -> None:
    print(f"::error::{msg}", file=sys.stderr)


def validate_semver(value: str, where: str, errors: list[str]) -> None:
    if not value or not SEMVER.match(value):
        errors.append(f"{where}: value '{value}' is not valid semver")


def validate_always(data: dict) -> list[str]:
    errors: list[str] = []

    metadata = data.get("metadata", {})
    validate_semver(metadata.get("version", ""), "metadata.version", errors)

    for i, plugin in enumerate(data.get("plugins", [])):
        validate_semver(
            plugin.get("version", ""), f"plugins[{i}].version", errors
        )
        for skill_path in plugin.get("skills", []):
            resolved = (ROOT / skill_path.lstrip("./")).resolve()
            skill_md = resolved / "SKILL.md"
            if not skill_md.exists():
                errors.append(
                    f"plugins[{i}].skills: '{skill_path}' does not resolve to {skill_md.relative_to(ROOT)}"
                )

    return errors


def read_top_changelog_version() -> str:
    changelog_script = ROOT / "scripts" / "changelog.py"
    result = subprocess.run(
        [sys.executable, str(changelog_script), "extract-version"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"error: could not read CHANGELOG version: {result.stderr.strip()}")
    return result.stdout.strip()


def tag_exists(version: str) -> bool:
    result = subprocess.run(
        ["git", "tag", "--list", f"v{version}"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    return bool(result.stdout.strip())


def validate_strict(data: dict) -> list[str]:
    errors: list[str] = []
    metadata_version = data.get("metadata", {}).get("version", "")
    plugins = data.get("plugins", [])
    plugin_version = plugins[0].get("version", "") if plugins else ""
    changelog_version = read_top_changelog_version()

    if metadata_version != changelog_version:
        errors.append(
            f"metadata.version ({metadata_version}) != top CHANGELOG version ({changelog_version})"
        )
    if plugin_version != changelog_version:
        errors.append(
            f"plugins[0].version ({plugin_version}) != top CHANGELOG version ({changelog_version})"
        )

    if tag_exists(changelog_version):
        errors.append(
            f"tag v{changelog_version} already exists; rebase on main and bump to the next version"
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Also enforce release-PR invariants (version sync + tag collision)",
    )
    args = parser.parse_args()

    if not MARKETPLACE.exists():
        err(f"{MARKETPLACE.relative_to(ROOT)} does not exist")
        return 1

    try:
        data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"{MARKETPLACE.relative_to(ROOT)} is not valid JSON: {e}")
        return 1

    errors = validate_always(data)
    if args.strict:
        errors.extend(validate_strict(data))

    if errors:
        for e in errors:
            err(e)
        return 1

    mode = "strict" if args.strict else "structural"
    print(f"OK: marketplace.json passed {mode} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
