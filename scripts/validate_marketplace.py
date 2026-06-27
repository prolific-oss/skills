#!/usr/bin/env python3
"""Validate .claude-plugin/marketplace.json.

Always checks:
  - metadata.version is valid semver
  - every plugins[*].version is valid semver
  - every skill listed under plugins[*].skills resolves to an existing file

With --strict (used on release-labelled PRs), additionally checks:
  - metadata.version == top CHANGELOG version
  - v<version> does not already exist as a git tag
  - every plugin whose skills changed since the last tag has a version
    strictly greater than its version at that tag; every plugin whose
    skills did not change keeps its previous version (no phantom bumps)

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


def skill_folder_name(skill_path: str) -> str:
    """'./skills/whoami' -> 'whoami'."""
    return skill_path.rstrip("/").split("/")[-1]


def plugin_skill_folders(plugin: dict) -> set[str]:
    """Folder names a plugin owns, from its `skills` list."""
    return {skill_folder_name(s) for s in plugin.get("skills", [])}


def parse_semver(value: str) -> tuple[int, int, int]:
    """Numeric (major, minor, patch) core for ordering; (-1,-1,-1) if unparsable."""
    if not value or not SEMVER.match(value):
        return (-1, -1, -1)
    core = value.split("-", 1)[0]
    major, minor, patch = (int(part) for part in core.split("."))
    return (major, minor, patch)


def plugin_bump_errors(
    data: dict,
    prev_versions: dict[str, str],
    changed_folders: set[str],
) -> list[str]:
    """Each plugin's own semver moves only with its own skills (Model B).

    - A plugin whose skills changed must be strictly greater than its
      version at the last tag.
    - A plugin whose skills did not change must keep that previous version,
      so Claude Code does not re-deliver an unchanged plugin.
    - A plugin with no previous version (newly added this release) is only
      required to be valid semver, which `validate_always` already checks.
    """
    errors: list[str] = []
    for i, plugin in enumerate(data.get("plugins", [])):
        name = plugin.get("name", f"plugins[{i}]")
        version = plugin.get("version", "")
        prev = prev_versions.get(name)
        if prev is None:
            continue
        changed = bool(plugin_skill_folders(plugin) & changed_folders)
        if changed:
            if parse_semver(version) <= parse_semver(prev):
                errors.append(
                    f"plugin '{name}' has changed skills since the last release "
                    f"but its version ('{version}') is not greater than its "
                    f"previous version ('{prev}'); bump it (run `make release "
                    f"VERSION=<train>` and adjust the suggested per-plugin bump)"
                )
        elif version != prev:
            errors.append(
                f"plugin '{name}' has no skill changes since the last release "
                f"but its version moved ('{prev}' -> '{version}'); revert it so "
                f"unchanged plugins are not re-delivered to users"
            )
    return errors


def strict_errors(
    data: dict,
    changelog_version: str,
    prev_versions: dict[str, str],
    changed_folders: set[str],
    tag_already_exists: bool,
) -> list[str]:
    """Pure core of the strict checks — no git, no filesystem."""
    errors: list[str] = []
    metadata_version = data.get("metadata", {}).get("version", "")
    if metadata_version != changelog_version:
        errors.append(
            f"metadata.version ({metadata_version}) != top CHANGELOG version ({changelog_version})"
        )
    if tag_already_exists:
        errors.append(
            f"tag v{changelog_version} already exists; rebase on main and bump to the next version"
        )
    errors.extend(plugin_bump_errors(data, prev_versions, changed_folders))
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


def last_tag() -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def changed_skill_folders(since: str | None) -> set[str]:
    """Skill folder names touched since `since` (all of them if no tag yet)."""
    if since is None:
        return {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
    result = subprocess.run(
        ["git", "diff", "--name-only", since, "--", "skills/"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    if result.returncode != 0:
        sys.exit(f"error: git diff failed: {result.stderr.strip()}")
    folders: set[str] = set()
    for line in result.stdout.splitlines():
        parts = line.split("/")
        if len(parts) >= 2 and parts[0] == "skills":
            folders.add(parts[1])
    return folders


def plugin_versions_at(tag: str | None) -> dict[str, str]:
    """Map plugin name -> version in marketplace.json at `tag` (empty if none)."""
    if tag is None:
        return {}
    result = subprocess.run(
        ["git", "show", f"{tag}:.claude-plugin/marketplace.json"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    if result.returncode != 0:
        return {}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}
    return {
        p.get("name", ""): p.get("version", "")
        for p in data.get("plugins", [])
        if p.get("name")
    }


def validate_strict(data: dict) -> list[str]:
    since = last_tag()
    changelog_version = read_top_changelog_version()
    return strict_errors(
        data,
        changelog_version,
        plugin_versions_at(since),
        changed_skill_folders(since),
        tag_already_exists=tag_exists(changelog_version),
    )


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
