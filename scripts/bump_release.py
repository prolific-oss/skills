#!/usr/bin/env python3
"""Stamp a new release version across the three sync points.

Usage:
  bump_release.py X.Y.Z

Edits (in-place, leaves them uncommitted for the contributor to review):
  - .claude-plugin/marketplace.json: metadata.version + plugins[0].version → X.Y.Z
  - skills/<changed>/SKILL.md frontmatter: version: → X.Y.Z (every skill
    whose folder was touched since the last release tag, or every skill
    if no tag exists yet)
  - CHANGELOG.md: prepends a new `## X.Y.Z` section stubbed from git-cliff
    output (falls back to a manual-fill stub if git-cliff is not installed
    or no tag exists yet)

The contributor reviews the diff, edits the CHANGELOG stub if needed,
commits, pushes, and opens a PR with the `release` label.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SKILLS_DIR = ROOT / "skills"
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")
FRONTMATTER_VERSION = re.compile(
    r'(^---\n.*?^version:\s*)(["\']?)([^\n"\']+)(\2)(\s*$)',
    re.MULTILINE | re.DOTALL,
)


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def last_tag() -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def changed_skill_files(since: str | None) -> list[Path]:
    """Return SKILL.md paths for skill folders touched since `since`.

    A "touched skill" is any skill folder containing at least one file
    in the diff against `since`. Multiple files in the same folder
    collapse to a single SKILL.md to bump.
    """
    if since:
        result = subprocess.run(
            ["git", "diff", "--name-only", since, "--", "skills/"],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT,
        )
        if result.returncode != 0:
            die(f"git diff failed: {result.stderr.strip()}")
        skill_mds: set[Path] = set()
        for line in result.stdout.splitlines():
            parts = line.split("/")
            if len(parts) < 2 or parts[0] != "skills":
                continue
            skill_md = SKILLS_DIR / parts[1] / "SKILL.md"
            if skill_md.exists():
                skill_mds.add(skill_md)
        return sorted(skill_mds)
    return sorted(p for p in SKILLS_DIR.glob("*/SKILL.md") if p.is_file())


def bump_marketplace(version: str) -> None:
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    data["metadata"]["version"] = version
    if not data.get("plugins"):
        die("marketplace.json has no plugins to bump")
    data["plugins"][0]["version"] = version
    MARKETPLACE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def bump_skill(path: Path, version: str) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text, n = FRONTMATTER_VERSION.subn(rf"\g<1>\g<2>{version}\g<4>\g<5>", text, count=1)
    if n == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def stub_changelog(version: str, since: str | None) -> str:
    cmd = (
        ["git-cliff", f"{since}..HEAD", "--tag", f"v{version}", "--strip", "header"]
        if since
        else ["git-cliff", "--tag", f"v{version}", "--strip", "header"]
    )
    try:
        cliff = subprocess.run(
            cmd, capture_output=True, text=True, check=False, cwd=ROOT
        )
    except FileNotFoundError:
        cliff = None
    if cliff is not None and cliff.returncode == 0 and cliff.stdout.strip():
        body = cliff.stdout.strip()
    else:
        body = "### <skill-name>\n\n- [feat|fix] <describe the change>"
    return f"## {version}\n\n{body}\n\n"


def prepend_changelog(version: str, since: str | None) -> None:
    section = stub_changelog(version, since)
    existing = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else "# Changelog\n\n"
    header_end = existing.find("\n## ")
    if header_end == -1:
        new_text = existing.rstrip() + "\n\n" + section
    else:
        new_text = existing[: header_end + 1] + section + existing[header_end + 1 :]
    CHANGELOG.write_text(new_text, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        die("usage: bump_release.py X.Y.Z")
    version = sys.argv[1].lstrip("v")
    if not SEMVER.match(version):
        die(f"version '{version}' is not valid semver")

    since = last_tag()
    skills = changed_skill_files(since)
    bumped_skills = [p for p in skills if bump_skill(p, version)]
    bump_marketplace(version)
    prepend_changelog(version, since)

    print(f"Bumped marketplace.json metadata.version + plugins[0].version → {version}")
    if bumped_skills:
        print(f"Bumped frontmatter version on {len(bumped_skills)} skill(s):")
        for p in bumped_skills:
            print(f"  - {p.relative_to(ROOT)}")
    else:
        print("No skill frontmatter to bump (no skill changes since last tag)")
    print(f"Prepended ## {version} section to CHANGELOG.md")
    print("")
    print("Next steps:")
    print("  1. Review the diff and edit the CHANGELOG stub")
    print(f"  2. Commit: git checkout -b release/v{version} && git add -A && git commit -m 'chore: release v{version}'")
    print("  3. Push and open a PR with the 'release' label")


if __name__ == "__main__":
    main()
