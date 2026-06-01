#!/usr/bin/env python3
"""Validate skill frontmatter.

Each skill lives in skills/<name>/SKILL.md (per the agentskills.io
convention). Every SKILL.md must have top-of-file YAML frontmatter
with name, description, and a valid semver version.

Exits non-zero on any failure with a clear per-file error.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
REQUIRED = ("name", "description", "version")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(-[A-Za-z0-9.-]+)?$")


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return the frontmatter as a dict, or None if absent/malformed."""
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    fields: dict[str, str] = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            return None
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def iter_skill_files() -> list[Path]:
    return sorted(p for p in SKILLS_DIR.glob("*/SKILL.md") if p.is_file())


def validate_one(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is None:
        return [f"{path.relative_to(ROOT)}: missing or malformed YAML frontmatter"]
    errors = []
    for field in REQUIRED:
        if field not in fm or not fm[field]:
            errors.append(f"{path.relative_to(ROOT)}: missing required field '{field}'")
    version = fm.get("version", "")
    if version and not SEMVER.match(version):
        errors.append(
            f"{path.relative_to(ROOT)}: version '{version}' is not valid semver"
        )
    return errors


def main() -> int:
    if not SKILLS_DIR.is_dir():
        print(f"error: {SKILLS_DIR} does not exist", file=sys.stderr)
        return 1

    files = iter_skill_files()
    if not files:
        print(f"warning: no skill files found under {SKILLS_DIR}", file=sys.stderr)
        return 0

    all_errors: list[str] = []
    for path in files:
        all_errors.extend(validate_one(path))

    if all_errors:
        for err in all_errors:
            print(f"::error::{err}", file=sys.stderr)
        return 1

    print(f"OK: {len(files)} skill file(s) validated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
