from pathlib import Path

from grep_knowledge.extractors import extract


def test_extracts_text(tmp_path: Path) -> None:
    source = tmp_path / "lecture.txt"
    source.write_text("gradient descent", encoding="utf-8")
    assert extract(source) == "gradient descent"

