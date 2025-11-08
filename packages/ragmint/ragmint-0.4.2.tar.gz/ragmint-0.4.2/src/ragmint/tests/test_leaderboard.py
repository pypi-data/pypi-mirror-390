import os
import json
import tempfile
import pytest
from datetime import datetime
from ragmint.leaderboard import Leaderboard


@pytest.fixture
def temp_leaderboard():
    """Create a temporary leaderboard file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "leaderboard.jsonl")
        lb = Leaderboard(storage_path=path)
        yield lb, path


def test_upload_and_persistence(temp_leaderboard):
    lb, path = temp_leaderboard

    # --- Mock experiment data ---
    run_id = "run_001"
    best_config = {"retriever": "FAISS", "embedding_model": "all-MiniLM"}
    best_score = 0.92
    all_results = [
        {"retriever": "FAISS", "score": 0.92},
        {"retriever": "BM25", "score": 0.85},
    ]
    documents = ["docs/a.txt", "docs/b.txt"]
    model = "gemini"
    corpus_stats = {"size": 20000, "avg_len": 400, "num_docs": 10}

    # --- Upload ---
    record = lb.upload(
        run_id=run_id,
        best_config=best_config,
        best_score=best_score,
        all_results=all_results,
        documents=documents,
        model=model,
        corpus_stats=corpus_stats,
    )

    # --- Validate returned record ---
    assert record["run_id"] == run_id
    assert record["model"] == "gemini"
    assert "timestamp" in record
    assert record["best_score"] == 0.92
    assert all(doc in record["documents"] for doc in ["a.txt", "b.txt"])

    # --- File should contain JSON line ---
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 1
    parsed = json.loads(lines[0])
    assert parsed["run_id"] == run_id


def test_top_results_ordering(temp_leaderboard):
    lb, _ = temp_leaderboard

    # Upload multiple runs with varying scores
    for i, score in enumerate([0.8, 0.95, 0.7]):
        lb.upload(
            run_id=f"run_{i}",
            best_config={"retriever": "FAISS"},
            best_score=score,
            all_results=[],
            documents=["file.txt"],
            model="claude",
        )

    # --- Get top results ---
    top = lb.top_results(limit=2)
    assert len(top) == 2

    # --- Ensure ordering descending by score ---
    assert top[0]["best_score"] >= top[1]["best_score"]
    assert top[0]["best_score"] == 0.95


def test_all_results_reads_all_entries(temp_leaderboard):
    lb, _ = temp_leaderboard

    # Add two runs
    lb.upload("run_a", {}, 0.5, [], ["doc1.txt"], "gemini")
    lb.upload("run_b", {}, 0.7, [], ["doc2.txt"], "claude")

    results = lb.all_results()
    assert len(results) == 2
    run_ids = {r["run_id"] for r in results}
    assert {"run_a", "run_b"} <= run_ids
