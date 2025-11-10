import os
import json
import pytest
from ragmint.tuner import RAGMint


def setup_validation_file(tmp_path):
    """Create a temporary validation QA dataset."""
    data = [
        {"question": "What is AI?", "answer": "Artificial Intelligence"},
        {"question": "Define ML", "answer": "Machine Learning"}
    ]
    file = tmp_path / "validation_qa.json"
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    return str(file)


def setup_docs(tmp_path):
    """Create a small document corpus for testing."""
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "doc1.txt").write_text("This is about Artificial Intelligence.")
    (corpus / "doc2.txt").write_text("This text explains Machine Learning.")
    return str(corpus)


@pytest.mark.parametrize("validation_mode", [
    None,  # Built-in dataset
    "data/custom_eval.json",  # Custom dataset path (mocked below)
])
def test_optimize_ragmint(tmp_path, validation_mode, monkeypatch):
    """Test RAGMint.optimize() with different dataset modes."""
    docs_path = setup_docs(tmp_path)
    val_file = setup_validation_file(tmp_path)

    # If using custom dataset, mock the path
    if validation_mode and "custom_eval" in validation_mode:
        custom_path = tmp_path / "custom_eval.json"
        os.rename(val_file, custom_path)
        validation_mode = str(custom_path)

    metric = "faithfulness"

    # Initialize RAGMint
    rag = RAGMint(
        docs_path=docs_path,
        retrievers=["faiss"],
        embeddings=["all-MiniLM-L6-v2"],
        rerankers=["mmr"]
    )

    # Run optimization
    best, results = rag.optimize(
        validation_set=validation_mode,
        metric=metric,
        trials=2
    )

    # Validate results
    assert isinstance(best, dict), "Best config should be a dict"
    assert isinstance(results, list), "Results should be a list of trials"
    assert len(results) > 0, "Optimization should produce results"

    # The best result can expose either 'score' or the metric name (e.g. 'faithfulness')
    assert any(k in best for k in ("score", metric)), \
        f"Best config should include either 'score' or '{metric}'"

    # Ensure the metric value is valid
    assert best.get(metric, best.get("score")) >= 0, \
        f"{metric} score should be non-negative"
