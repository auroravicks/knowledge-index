from __future__ import annotations

import logging

import click

from .config import Config
from .indexer import build_index
from .logging_setup import configure_logging
from .notifications import send_index_summary
from .search import search as run_search

LOGGER = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """Build and search a local grep-first study knowledge layer."""


@cli.command()
def index() -> None:
    """Extract changed source files and refresh CATALOG.md."""
    try:
        config = Config.load()
        configure_logging(config)
        LOGGER.info("Starting knowledge index")
        result = build_index(config)
        send_index_summary(config, result)
        LOGGER.info(
            "Knowledge index complete: files=%s indexed=%s unchanged=%s errors=%s",
            result["files"], result["indexed"], result["unchanged"], len(result["errors"]),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        LOGGER.exception("Knowledge index failed")
        raise click.ClickException(str(exc)) from exc
    click.echo(
        f"Knowledge index: files={result['files']} indexed={result['indexed']} "
        f"unchanged={result['unchanged']} errors={len(result['errors'])}."
    )


@cli.command()
@click.argument("query")
@click.option("--subject")
@click.option("--kind", type=click.Choice(["Transcripts", "Notes"], case_sensitive=False))
@click.option("--context", type=click.IntRange(0, 50))
def search(query: str, subject: str | None, kind: str | None, context: int | None) -> None:
    """Search extracted text with ripgrep."""
    try:
        config = Config.load()
        configure_logging(config)
        LOGGER.info("Starting knowledge search subject=%s kind=%s", subject or "all", kind or "all")
        code = run_search(config, query, subject, kind, context)
    except (OSError, ValueError) as exc:
        LOGGER.exception("Knowledge search failed")
        raise click.ClickException(str(exc)) from exc
    if code not in (0, 1):
        LOGGER.error("ripgrep failed with exit code %s", code)
        raise click.ClickException(f"ripgrep failed with exit code {code}")


if __name__ == "__main__":
    cli()
