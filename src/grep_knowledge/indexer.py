from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import UTC, datetime
from pathlib import Path

from .config import Config
from .extractors import extract

SUPPORTED = {".pdf", ".docx", ".pptx", ".ipynb", ".txt", ".md", ".csv", ".tsv", ".py", ".r"}
LOGGER = logging.getLogger(__name__)


def _hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def build_index(config: Config) -> dict[str, object]:
    previous = {}
    if config.state_path.exists():
        previous = json.loads(config.state_path.read_text(encoding="utf-8")).get("files", {})
    current: dict[str, dict[str, str]] = {}
    catalog: dict[str, list[tuple[str, str]]] = {}
    errors: list[str] = []
    indexed = skipped = 0
    added: list[str] = []
    updated: list[str] = []

    for subject_dir in sorted(
        path
        for path in config.resources_dir.iterdir()
        if path.is_dir() and path.name != ".knowledge" and config.is_enrolled(path.name)
    ):
        subject = subject_dir.name
        for kind in ("Transcripts", "Notes"):
            source_root = subject_dir / kind
            if not source_root.exists():
                continue
            for source in sorted(path for path in source_root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED):
                relative = source.relative_to(config.resources_dir).as_posix()
                digest = _hash(source)
                target_relative = Path(subject) / kind / source.relative_to(source_root)
                target = (config.searchable_dir / target_relative).with_suffix(source.suffix + ".txt")
                current[relative] = {"sha256": digest, "target": target.relative_to(config.resources_dir).as_posix()}
                catalog.setdefault(subject, []).append((kind, relative))
                if previous.get(relative, {}).get("sha256") == digest and target.exists():
                    skipped += 1
                    continue
                try:
                    body = extract(source)
                    header = f"[[SUBJECT: {subject}]]\n[[SOURCE: {relative}]]\n[[TYPE: {kind}]]\n\n"
                    _write(target, header + body)
                    indexed += 1
                    if relative in previous:
                        updated.append(relative)
                    else:
                        added.append(relative)
                except Exception as exc:
                    error = f"{relative}: {type(exc).__name__}: {exc}"
                    errors.append(error)
                    LOGGER.warning("Document extraction failed: %s", error, exc_info=True)

    removed = sorted(set(previous) - set(current))
    searchable_root = config.searchable_dir.resolve()
    for relative in removed:
        old_target = previous.get(relative, {}).get("target")
        if not old_target:
            continue
        target = (config.resources_dir / old_target).resolve()
        try:
            target.relative_to(searchable_root)
        except ValueError:
            continue
        if target.is_file():
            target.unlink()

    lines = ["# Knowledge catalog", "", f"Updated: {datetime.now(UTC).isoformat()}", ""]
    for subject, items in sorted(catalog.items()):
        lines += [f"## {subject}", ""]
        for kind, relative in sorted(items):
            lines.append(f"- **{kind}** — `{relative}`")
        lines.append("")
    if errors:
        lines += ["## Extraction errors", ""] + [f"- {error}" for error in errors] + [""]
    _write(config.catalog_path, "\n".join(lines))
    _write(config.state_path, json.dumps({"updated_at": datetime.now(UTC).isoformat(), "files": current}, indent=2))
    return {
        "indexed": indexed,
        "unchanged": skipped,
        "errors": errors,
        "files": len(current),
        "added": sorted(added),
        "updated": sorted(updated),
        "removed": removed,
    }
