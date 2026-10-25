from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv
import yaml


@dataclass(frozen=True)
class Config:
    resources_dir: Path
    searchable_dir: Path
    catalog_path: Path
    state_path: Path
    context_lines: int
    unenrolled_subjects: frozenset[str] = frozenset()
    google_chat_webhook_url: str | None = None
    google_chat_enabled: bool = False
    summary_max_items: int = 20
    log_level: str = "INFO"
    log_dir: Path | None = None
    log_max_bytes: int = 2_097_152
    log_backup_count: int = 5

    @classmethod
    def load(cls, path: Path = Path("config.yml")) -> "Config":
        if not path.exists():
            raise ValueError("config.yml is missing; copy config.example.yml")
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        root = path.parent.resolve()
        load_dotenv(root / ".env", override=False)
        resources = (root / data.get("resources_dir", "../Resources")).resolve()
        if not resources.exists():
            raise ValueError(f"Resources directory does not exist: {resources}")
        raw_unenrolled = data.get("unenrolled_subjects", [])
        if not isinstance(raw_unenrolled, list) or not all(isinstance(subject, str) for subject in raw_unenrolled):
            raise ValueError("unenrolled_subjects must be a list of subject directory names")
        notifications = data.get("notifications", {})
        if not isinstance(notifications, dict):
            raise ValueError("notifications must be a mapping")
        google_chat = notifications.get("google_chat", {})
        if not isinstance(google_chat, dict):
            raise ValueError("notifications.google_chat must be a mapping")
        logging_config = data.get("logging", {})
        if not isinstance(logging_config, dict):
            raise ValueError("logging must be a mapping")
        return cls(
            resources_dir=resources,
            searchable_dir=resources / data.get("searchable_dir", ".knowledge/searchable"),
            catalog_path=resources / data.get("catalog_path", "CATALOG.md"),
            state_path=resources / data.get("state_path", ".knowledge/state.json"),
            context_lines=int(data.get("context_lines", 4)),
            unenrolled_subjects=frozenset(subject.casefold() for subject in raw_unenrolled),
            google_chat_webhook_url=os.getenv("GOOGLE_CHAT_WEBHOOK_URL") or None,
            google_chat_enabled=bool(google_chat.get("enabled", False)),
            summary_max_items=int(google_chat.get("summary_max_items", 20)),
            log_level=str(logging_config.get("level", "INFO")).upper(),
            log_dir=resources / str(logging_config.get("directory", ".knowledge/logs")),
            log_max_bytes=int(logging_config.get("max_bytes", 2_097_152)),
            log_backup_count=int(logging_config.get("backup_count", 5)),
        )

    def is_enrolled(self, subject: str) -> bool:
        return subject.casefold() not in self.unenrolled_subjects
