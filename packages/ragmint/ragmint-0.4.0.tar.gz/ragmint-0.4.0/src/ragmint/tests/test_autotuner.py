import os
import json
import pytest
from ragmint.autotuner import AutoRAGTuner


def setup_docs(tmp_path):
    """Create a temporary corpus with multiple text files for testing."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "short_doc.txt").write_text("AI is changing the world.")
    (corpus / "long_doc.txt").write_text("Machine learning enables RAG pipelines to optimize retrievals. " * 50)
    return str(corpus)


def test_analyze_corpus(tmp_path):
    """Ensure AutoRAGTuner analyzes corpus correctly."""
    docs_path = setup_docs(tmp_path)
    tuner = AutoRAGTuner(docs_path)
    stats = tuner.corpus_stats

    assert stats["num_docs"] == 2, "Should detect all documents"
    assert stats["size"] > 0, "Corpus size should be positive"
    assert stats["avg_len"] > 0, "Average document length should be computed"


@pytest.mark.parametrize("size,expected_retriever", [
    (10_000, "Chroma"),
    (500_000, "FAISS"),
    (1_000, "BM25"),
])
def test_recommendation_logic(tmp_path, monkeypatch, size, expected_retriever):
    """Validate retriever recommendation based on corpus size and chunk suggestion."""
    docs_path = setup_docs(tmp_path)
    tuner = AutoRAGTuner(docs_path)

    # Mock corpus stats manually
    tuner.corpus_stats = {"size": size, "avg_len": 300, "num_docs": 10}

    # Provide mandatory num_chunk_pairs
    rec = tuner.recommend(num_chunk_pairs=3)

    assert "retriever" in rec and "embedding_model" in rec
    assert rec["retriever"] == expected_retriever, f"Expected {expected_retriever}"
    assert rec["chunk_size"] > 0 and rec["overlap"] >= 0
    assert "chunk_candidates" in rec, "Should include suggested chunk pairs"
    assert len(rec["chunk_candidates"]) == 3, "Should generate correct number of chunk pairs"


def test_invalid_corpus_path(tmp_path):
    """Should handle missing directories gracefully."""
    missing_path = tmp_path / "nonexistent"
    tuner = AutoRAGTuner(str(missing_path))
    assert tuner.corpus_stats["size"] == 0
    assert tuner.corpus_stats["num_docs"] == 0


def test_suggest_chunk_sizes_requires_num_pairs(tmp_path):
    """Ensure suggest_chunk_sizes raises error if num_pairs is not provided."""
    docs_path = setup_docs(tmp_path)
    tuner = AutoRAGTuner(docs_path)

    with pytest.raises(ValueError):
        tuner.suggest_chunk_sizes()
