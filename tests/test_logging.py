import logging
from pathlib import Path

import grep_knowledge.logging_setup as logging_setup
from grep_knowledge.config import Config


def test_rotating_log_configuration(tmp_path: Path) -> None:
    resources = tmp_path / "Resources"
    resources.mkdir()
    log_dir = resources / ".knowledge/logs"
    config = Config(
        resources,
        resources / ".knowledge/searchable",
        resources / "CATALOG.md",
        resources / ".knowledge/state.json",
        4,
        log_dir=log_dir,
        log_max_bytes=100,
        log_backup_count=2,
    )
    logging_setup._configured_for = None

    configure_logger = logging.getLogger("grep_knowledge.test")
    try:
        logging_setup.configure_logging(config)
        configure_logger.info("test message")
        assert (log_dir / "grep-knowledge.log").read_text(encoding="utf-8").endswith("test message\n")
    finally:
        root = logging.getLogger()
        for handler in list(root.handlers):
            if getattr(handler, "baseFilename", None) == str(log_dir / "grep-knowledge.log"):
                root.removeHandler(handler)
                handler.close()
        logging_setup._configured_for = None
