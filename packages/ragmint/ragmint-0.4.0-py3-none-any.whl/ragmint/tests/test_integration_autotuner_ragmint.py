import os
import json
import pytest
from ragmint.autotuner import AutoRAGTuner
from ragmint.tuner import RAGMint


def setup_docs(tmp_path):
    """Create a temporary corpus for integration testing."""
    corpus = tmp_path / "docs"
    corpus.mkdir()
    (corpus / "doc1.txt").write_text("This document discusses Artificial Intelligence and Machine Learning.")
    (corpus / "doc2.txt").write_text("Retrieval-Augmented Generation combines retrievers and LLMs effectively.")
    return str(corpus)


def setup_validation_file(tmp_path):
    """Create a temporary validation QA dataset."""
    data = [
        {"question": "What is AI?", "answer": "Artificial Intelligence"},
        {"question": "Define RAG", "answer": "Retrieval-Augmented Generation"},
    ]
    file = tmp_path / "validation_qa.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return str(file)


def test_autotune_integration(tmp_path):
    """Test that AutoRAGTuner can fully run a RAGMint optimization."""
    docs_path = setup_docs(tmp_path)
    val_file = setup_validation_file(tmp_path)

    tuner = AutoRAGTuner(docs_path)
    best, results = tuner.auto_tune(
        validation_set=val_file,
        metric="faithfulness",
        trials=2,
        search_type="random",
    )

    # Assertions on the results
    assert isinstance(best, dict), "Best configuration should be a dict"
    assert isinstance(results, list), "Results should be a list"
    assert len(results) > 0, "Optimization should produce results"
    assert "retriever" in best and "embedding_model" in best
    assert best.get("faithfulness", 0.0) >= 0.0, "Metric value should be non-negative"
