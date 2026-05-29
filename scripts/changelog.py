#!/usr/bin/env python3
"""Helpers for reading CHANGELOG.md.

Commands:
  extract-version              Print the top semver heading (the current release version)
  extract-section X.Y.Z        Print the body of the X.Y.Z section
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
SEMVER = re.compile(r"^## (\d+\.\d+\.\d+)\s*$", re.MULTILINE)


def extract_version() -> str:
    text = CHANGELOG.read_text(encoding="utf-8")
    match = SEMVER.search(text)
    if not match:
        sys.exit(f"error: no semver heading (## X.Y.Z) found in {CHANGELOG}")
    return match.group(1)


def extract_section(version: str) -> str:
    text = CHANGELOG.read_text(encoding="utf-8")
    heading = f"## {version}"
    start = text.find(f"\n{heading}\n")
    if start == -1 and text.startswith(f"{heading}\n"):
        start = 0
    else:
        start += 1 if start != -1 else 0
    if start == -1 or start < 0:
        sys.exit(f"error: version {version} not found in {CHANGELOG}")
    body_start = text.find("\n", start) + 1
    next_heading = re.search(r"^## ", text[body_start:], re.MULTILINE)
    body_end = body_start + next_heading.start() if next_heading else len(text)
    return text[body_start:body_end].strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("extract-version", help="Print the top semver heading")
    section = sub.add_parser("extract-section", help="Print one version's body")
    section.add_argument("version", help="Semver to extract (e.g. 0.1.0)")
    args = parser.parse_args()

    if args.cmd == "extract-version":
        print(extract_version())
    elif args.cmd == "extract-section":
        sys.stdout.write(extract_section(args.version))


if __name__ == "__main__":
    main()
