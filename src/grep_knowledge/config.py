from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Config:
    resources_dir: Path
    searchable_dir: Path
    catalog_path: Path
    state_path: Path
    context_lines: int
    unenrolled_subjects: frozenset[str] = frozenset()

    @classmethod
    def load(cls, path: Path = Path("config.yml")) -> "Config":
        if not path.exists():
            raise ValueError("config.yml is missing; copy config.example.yml")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        root = path.parent.resolve()
        resources = (root / data.get("resources_dir", "../Resources")).resolve()
        if not resources.exists():
            raise ValueError(f"Resources directory does not exist: {resources}")
        raw_unenrolled = data.get("unenrolled_subjects", [])
        if not isinstance(raw_unenrolled, list) or not all(isinstance(subject, str) for subject in raw_unenrolled):
            raise ValueError("unenrolled_subjects must be a list of subject directory names")
        return cls(
            resources_dir=resources,
            searchable_dir=resources / data.get("searchable_dir", ".knowledge/searchable"),
            catalog_path=resources / data.get("catalog_path", "CATALOG.md"),
            state_path=resources / data.get("state_path", ".knowledge/state.json"),
            context_lines=int(data.get("context_lines", 4)),
            unenrolled_subjects=frozenset(subject.casefold() for subject in raw_unenrolled),
        )

    def is_enrolled(self, subject: str) -> bool:
        return subject.casefold() not in self.unenrolled_subjects
