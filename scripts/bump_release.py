#!/usr/bin/env python3
"""Stamp a new release across the marketplace, plugins, and skills.

Usage:
  bump_release.py X.Y.Z   # X.Y.Z is the release-train number

Edits (in-place, leaves them uncommitted for the contributor to review):
  - .claude-plugin/marketplace.json:
      - metadata.version → X.Y.Z (the release-train number; always)
      - plugins[*].version → bumped by that plugin's OWN severity, only for
        plugins whose skills changed since the last tag (independent
        per-plugin semver; unchanged plugins are left alone)
  - skills/<changed>/SKILL.md frontmatter: version → bumped by that skill's
    OWN severity (every existing skill folder touched since the last tag;
    brand-new skills keep their author-set version)
  - CHANGELOG.md: prepends a new `## X.Y.Z` section (with a per-plugin
    version summary) stubbed from git-cliff output (falls back to a
    manual-fill stub if git-cliff is unavailable or no tag exists yet)

Severity per unit is inferred from conventional-commit types since the
last tag (any `feat` → MINOR, otherwise PATCH; pre-1.0). The suggestion is
printed for review — adjust the numbers before committing if a change
warrants a different bump.

The contributor reviews the diff, edits the CHANGELOG stub if needed,
commits, pushes, and opens a PR with the `release` label.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import validate_marketplace as vm

ROOT = Path(__file__).resolve().parent.parent
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CHANGELOG = ROOT / "CHANGELOG.md"
SKILLS_DIR = ROOT / "skills"
# Plain X.Y.Z only — prerelease suffixes are disallowed (see validate_marketplace).
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
FRONTMATTER_VERSION = re.compile(
    r'(^---\n.*?^version:\s*)(["\']?)([^\n"\']+)(\2)(\s*$)',
    re.MULTILINE | re.DOTALL,
)


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def last_tag() -> str | None:
    result = subprocess.run(
        ["git", "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"],
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


def existed_at(since: str | None, relpath: str) -> bool:
    """Whether `relpath` existed in the tree at `since`."""
    if since is None:
        return False
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{since}:{relpath}"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    return result.returncode == 0


def folder_severity(folder: str, since: str | None) -> str:
    """'minor' if any feat commit touched the folder since `since`, else 'patch'."""
    if since is None:
        return "patch"
    result = subprocess.run(
        ["git", "log", f"{since}..HEAD", "--format=%s", "--", f"skills/{folder}/"],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    subjects = result.stdout.splitlines() if result.returncode == 0 else []
    return "minor" if any(re.match(r"^feat", s) for s in subjects) else "patch"


def bump_version(version: str, severity: str) -> str:
    """Increment X.Y.Z by `severity` (pre-1.0: feat→minor, else patch)."""
    major, minor, patch = (int(x) for x in version.split("."))
    if severity == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def read_skill_version(path: Path) -> str | None:
    match = FRONTMATTER_VERSION.search(path.read_text(encoding="utf-8"))
    return match.group(3) if match else None


def bump_marketplace(
    train: str,
    changed_folders: set[str],
    prev_plugins: dict[str, dict],
    severities: dict[str, str],
) -> list[tuple[str, str, str]]:
    """Set metadata.version to the train; bump each changed plugin by its own
    severity. Returns (name, old, new) for every plugin that moved."""
    data = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    data["metadata"]["version"] = train
    if not data.get("plugins"):
        die("marketplace.json has no plugins to bump")
    deltas: list[tuple[str, str, str]] = []
    for plugin in data["plugins"]:
        name = plugin.get("name", "<unnamed>")
        prev = prev_plugins.get(name)
        # Brand-new plugins keep their author-set version; unchanged plugins
        # (no skill-file change and no skill-set change) are left alone so
        # users aren't re-delivered no-ops.
        if prev is None or not vm.plugin_changed(plugin, prev, changed_folders):
            continue
        owned = vm.plugin_skill_folders(plugin) & changed_folders
        severity = "minor" if any(severities.get(f) == "minor" for f in owned) else "patch"
        prev_version = prev.get("version", "")
        computed = bump_version(prev_version, severity)
        # Never downgrade: if the contributor already bumped past the
        # suggestion (or re-ran make release), keep the higher version.
        current = plugin.get("version", prev_version)
        new = computed if vm.parse_semver(computed) >= vm.parse_semver(current) else current
        plugin["version"] = new
        deltas.append((name, prev_version, new))
    MARKETPLACE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return deltas


def bump_skill(path: Path, version: str) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text, n = FRONTMATTER_VERSION.subn(rf"\g<1>\g<2>{version}\g<4>\g<5>", text, count=1)
    if n == 0:
        return False
    path.write_text(new_text, encoding="utf-8")
    return True


def stub_changelog(
    version: str, since: str | None, plugin_deltas: list[tuple[str, str, str]]
) -> str:
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
    summary = ""
    if plugin_deltas:
        parts = ", ".join(f"{name} {old}→{new}" for name, old, new in plugin_deltas)
        summary = f"_Plugins: {parts}_\n\n"
    return f"## {version}\n\n{summary}{body}\n\n"


def prepend_changelog(
    version: str, since: str | None, plugin_deltas: list[tuple[str, str, str]]
) -> None:
    section = stub_changelog(version, since, plugin_deltas)
    existing = CHANGELOG.read_text(encoding="utf-8") if CHANGELOG.exists() else "# Changelog\n\n"
    header_end = existing.find("\n## ")
    if header_end == -1:
        new_text = existing.rstrip() + "\n\n" + section
    else:
        new_text = existing[: header_end + 1] + section + existing[header_end + 1 :]
    CHANGELOG.write_text(new_text, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        die("usage: bump_release.py X.Y.Z  (X.Y.Z = release-train number)")
    train = sys.argv[1].lstrip("v")
    if not SEMVER.match(train):
        die(f"version '{train}' is not valid semver")

    since = last_tag()
    changed_files = changed_skill_files(since)
    changed_folders = {p.parent.name for p in changed_files}
    severities = {f: folder_severity(f, since) for f in changed_folders}
    prev_plugins = vm.plugins_at(since)
    if prev_plugins is None:
        die(f"could not load marketplace.json at {since}; refusing to bump")

    # Bump each existing skill's frontmatter by its own severity. Brand-new
    # skills keep the version their author set in this PR.
    skill_deltas: list[tuple[Path, str, str]] = []
    for path in changed_files:
        folder = path.parent.name
        if not existed_at(since, f"skills/{folder}/SKILL.md"):
            continue
        current = read_skill_version(path)
        if current is None:
            continue
        new = bump_version(current, severities[folder])
        if bump_skill(path, new):
            skill_deltas.append((path, current, new))

    plugin_deltas = bump_marketplace(train, changed_folders, prev_plugins, severities)
    prepend_changelog(train, since, plugin_deltas)

    print(f"Bumped marketplace.json metadata.version → {train} (release train)")
    if plugin_deltas:
        print(f"Bumped {len(plugin_deltas)} plugin(s) by their own severity:")
        for name, old, new in plugin_deltas:
            print(f"  - {name}: {old} → {new}")
    else:
        print("No plugin versions bumped (no plugin's skills changed since last tag)")
    if skill_deltas:
        print(f"Bumped frontmatter on {len(skill_deltas)} skill(s):")
        for path, old, new in skill_deltas:
            print(f"  - {path.relative_to(ROOT)}: {old} → {new}")
    else:
        print("No skill frontmatter bumped (none changed, or all brand-new)")
    print(f"Prepended ## {train} section to CHANGELOG.md")
    print("")
    print("Next steps:")
    print("  1. Review the diff; adjust any suggested per-plugin/skill bump and the CHANGELOG stub")
    print(f"  2. Commit: git checkout -b release/v{train} && git add -A && git commit -m 'chore: release v{train}'")
    print("  3. Push and open a PR with the 'release' label")


if __name__ == "__main__":
    main()
