from __future__ import annotations

import click

from .config import Config
from .indexer import build_index
from .search import search as run_search


@click.group()
def cli() -> None:
    """Build and search a local grep-first study knowledge layer."""


@cli.command()
def index() -> None:
    """Extract changed source files and refresh CATALOG.md."""
    try:
        result = build_index(Config.load())
    except (OSError, ValueError) as exc:
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
        code = run_search(Config.load(), query, subject, kind, context)
    except (OSError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc
    if code not in (0, 1):
        raise click.ClickException(f"ripgrep failed with exit code {code}")


if __name__ == "__main__":
    cli()

