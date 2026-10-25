from grep_knowledge.notifications import build_index_summary


def test_index_summary_reports_changes() -> None:
    result = {
        "files": 12,
        "added": ["Course A/Notes/new.pdf"],
        "updated": ["Course A/Transcripts/lecture.txt"],
        "removed": [],
        "unchanged": 10,
        "errors": [],
    }
    text = build_index_summary(result)
    assert "Added: 1" in text
    assert "new.pdf" in text
    assert "lecture.txt" in text
