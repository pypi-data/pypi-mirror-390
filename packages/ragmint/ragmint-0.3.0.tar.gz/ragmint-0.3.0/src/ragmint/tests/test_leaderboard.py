import json
import tempfile
from pathlib import Path
from ragmint.leaderboard import Leaderboard


def test_leaderboard_add_and_top(tmp_path):
    """Ensure local leaderboard persistence works without Supabase."""
    file_path = tmp_path / "leaderboard.jsonl"
    lb = Leaderboard(storage_path=str(file_path))

    # Add two runs
    lb.upload("run1", {"retriever": "FAISS"}, 0.91)
    lb.upload("run2", {"retriever": "Chroma"}, 0.85)

    # Verify file content
    assert file_path.exists()
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f]
    assert len(lines) == 2

    # Get top results
    top = lb.top_results(limit=1)
    assert isinstance(top, list)
    assert len(top) == 1
    assert "score" in top[0]


def test_leaderboard_append_existing(tmp_path):
    """Ensure multiple uploads append properly."""
    file_path = tmp_path / "leaderboard.jsonl"
    lb = Leaderboard(storage_path=str(file_path))

    for i in range(3):
        lb.upload(f"run{i}", {"retriever": "BM25"}, 0.8 + i * 0.05)

    top = lb.top_results(limit=2)
    assert len(top) == 2
    assert top[0]["score"] >= top[1]["score"]
