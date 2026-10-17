from __future__ import annotations

import subprocess
from pathlib import Path

from .config import Config


def search(config: Config, query: str, subject: str | None, kind: str | None, context: int | None) -> int:
    root = config.searchable_dir
    if subject:
        candidates = [
            path
            for path in root.iterdir()
            if path.is_dir()
            and config.is_enrolled(path.name)
            and subject.casefold() in path.name.casefold()
        ]
        if not candidates:
            raise ValueError(f"No subject matches: {subject}")
        root = candidates[0]
    if kind:
        root = root / kind
    search_roots = [str(root)]
    if not subject and not kind:
        search_roots = [str(path) for path in root.iterdir() if path.is_dir() and config.is_enrolled(path.name)]
    command = ["rg", "-n", "-i", "-C", str(context if context is not None else config.context_lines), query, *search_roots]
    completed = subprocess.run(command, check=False)
    return completed.returncode
