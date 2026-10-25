from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from .config import Config

_configured_for: str | None = None


def configure_logging(config: Config) -> None:
    global _configured_for
    log_dir = config.log_dir or config.resources_dir / ".knowledge/logs"
    target = log_dir / "grep-knowledge.log"
    if _configured_for == str(target):
        return
    log_dir.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        target,
        maxBytes=config.log_max_bytes,
        backupCount=config.log_backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.setLevel(getattr(logging, config.log_level, logging.INFO))
    root.addHandler(handler)
    _configured_for = str(target)
