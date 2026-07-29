"""Generic Langfuse media helpers for optional eval file attachments.

Used by the shared eval runner:

  1. sync_dataset  -> build_file_attachments(...)
  2. experiment task -> stage_attachments(...) + prompt_with_attachments(...)

evals.json schema (optional on each case):

    "files": [
      { "path": "fixtures/example.md", "role": "context" },
      { "path": "fixtures/data.csv", "role": "dataset" }
    ]

`role` is optional prompt metadata. Paths are relative to the skill eval folder.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any

from langfuse.media import LangfuseMedia, LangfuseMediaReference

# Prefer explicit MIME types for common eval fixtures; fall back to mimetypes.
MEDIA_TYPES = {
    ".md": "text/markdown",
    ".csv": "text/csv",
    ".json": "application/json",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def content_type_for(path: Path) -> str:
    """Return a Langfuse-compatible MIME type for a fixture path."""
    suffix = path.suffix.lower()
    if suffix in MEDIA_TYPES:
        return MEDIA_TYPES[suffix]
    guessed, _ = mimetypes.guess_type(path.name)
    if guessed:
        return guessed
    raise ValueError(f"Unsupported fixture type for LangfuseMedia: {suffix or path}")


def media_for_path(path: Path) -> LangfuseMedia:
    """Wrap a local fixture file as LangfuseMedia for dataset upload."""
    if not path.exists():
        raise FileNotFoundError(f"Fixture not found: {path}")
    return LangfuseMedia(file_path=str(path), content_type=content_type_for(path))


def file_entries(case: dict[str, Any]) -> list[dict[str, str]]:
    """Return eval case file declarations as a list of {path, role?}."""
    return [
        {"path": entry["path"], **({"role": entry["role"]} if entry.get("role") else {})}
        for entry in case.get("files", [])
    ]


def build_file_attachments(
    case: dict[str, Any],
    fixtures_root: Path,
) -> list[dict[str, Any]]:
    """Build Langfuse-ready attachment objects for a dataset item input."""
    attachments: list[dict[str, Any]] = []
    for entry in file_entries(case):
        path = fixtures_root / entry["path"]
        attachment: dict[str, Any] = {
            "media": media_for_path(path),
            "filename": path.name,
        }
        if role := entry.get("role"):
            attachment["role"] = role
        attachments.append(attachment)
    return attachments


def _staged_filename(
    preferred_name: str | None,
    media: LangfuseMediaReference,
    role: str | None,
) -> str:
    if preferred_name:
        return Path(preferred_name).name
    ext_by_type = {mime: ext for ext, mime in MEDIA_TYPES.items()}
    ext = ext_by_type.get(media.content_type, "")
    return f"{role or 'attachment'}{ext}"


def stage_attachments(
    cwd: Path,
    attachments: list[dict[str, Any]] | None,
) -> list[dict[str, str]]:
    """Write Langfuse media attachments into the agent working directory."""
    staged: list[dict[str, str]] = []
    for attachment in attachments or []:
        media = attachment.get("media")
        if media is None:
            continue
        if not isinstance(media, LangfuseMediaReference):
            raise TypeError(
                f"Expected LangfuseMediaReference for attachment, got {type(media)!r}"
            )
        name = _staged_filename(
            attachment.get("filename"),
            media,
            attachment.get("role"),
        )
        (cwd / name).write_bytes(media.fetch_bytes())
        staged_entry = {"filename": name}
        if role := attachment.get("role"):
            staged_entry["role"] = role
        staged.append(staged_entry)
    return staged


def prompt_with_attachments(prompt: str, staged: list[dict[str, str]]) -> str:
    """Append a short attachment manifest to the user prompt."""
    if not staged:
        return prompt
    lines = []
    for item in staged:
        label = item.get("role") or "file"
        lines.append(f"- {label}: `{item['filename']}`")
    return (
        prompt
        + "\n\nAttached files are available in the working directory under their "
        + "original names:\n"
        + "\n".join(lines)
        + "\nRead these files directly rather than inventing their contents."
    )
