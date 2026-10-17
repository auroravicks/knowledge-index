from pathlib import Path

from grep_knowledge.config import Config
from grep_knowledge.indexer import build_index


def test_indexes_transcript_and_writes_catalog(tmp_path: Path) -> None:
    resources = tmp_path / "Resources"
    transcript = resources / "Course A" / "Transcripts" / "Lecture 1.txt"
    transcript.parent.mkdir(parents=True)
    transcript.write_text("A useful theorem", encoding="utf-8")
    config = Config(resources, resources / ".knowledge/searchable", resources / "CATALOG.md", resources / ".knowledge/state.json", 4)
    result = build_index(config)
    assert result["indexed"] == 1
    assert "Course A" in config.catalog_path.read_text(encoding="utf-8")
    assert "useful theorem" in next(config.searchable_dir.rglob("*.txt")).read_text(encoding="utf-8")


def test_skips_unenrolled_subjects(tmp_path: Path) -> None:
    resources = tmp_path / "Resources"
    for subject in ("Course A", "Course B"):
        transcript = resources / subject / "Transcripts" / "Lecture 1.txt"
        transcript.parent.mkdir(parents=True)
        transcript.write_text(f"Material for {subject}", encoding="utf-8")
    config = Config(
        resources,
        resources / ".knowledge/searchable",
        resources / "CATALOG.md",
        resources / ".knowledge/state.json",
        4,
        frozenset({"course b"}),
    )

    result = build_index(config)

    catalog = config.catalog_path.read_text(encoding="utf-8")
    assert result["files"] == 1
    assert "Course A" in catalog
    assert "Course B" not in catalog
