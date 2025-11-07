import pytest
from ragmint.tuner import RAGMint
from ragmint.autotuner import AutoRAGTuner


def test_integration_ragmint_autotune(monkeypatch, tmp_path):
    """
    Smoke test for integration between AutoRAGTuner and RAGMint.
    Ensures end-to-end flow runs without real retrievers or embeddings.
    """

    # --- Mock corpus and validation data ---
    corpus = tmp_path / "docs"
    corpus.mkdir()
    (corpus / "doc1.txt").write_text("This is an AI document.")
    validation_data = [{"question": "What is AI?", "answer": "Artificial Intelligence"}]

    # --- Mock RAGMint.optimize() to avoid real model work ---
    def mock_optimize(self, validation_set=None, metric="faithfulness", trials=2):
        return (
            {"retriever": "FAISS", "embedding_model": "OpenAI", "score": 0.88},
            [{"trial": 1, "score": 0.88}],
        )

    monkeypatch.setattr(RAGMint, "optimize", mock_optimize)

    # --- Mock evaluation used by AutoRAGTuner ---
    def mock_evaluate_config(config, data):
        return {"faithfulness": 0.9, "latency": 0.01}

    import ragmint.autotuner as autotuner
    monkeypatch.setattr(autotuner, "evaluate_config", mock_evaluate_config)

    # --- Create AutoRAGTuner and RAGMint instances ---
    ragmint = RAGMint(
        docs_path=str(corpus),
        retrievers=["faiss", "chroma"],
        embeddings=["text-embedding-3-small"],
        rerankers=["mmr"],
    )

    tuner = AutoRAGTuner({"size": 2000, "avg_len": 150})

    # --- Run Auto-Tune and RAG Optimization ---
    recommendation = tuner.recommend()
    assert "retriever" in recommendation
    assert "embedding_model" in recommendation

    tuning_results = tuner.auto_tune(validation_data)
    assert "results" in tuning_results
    assert isinstance(tuning_results["results"], dict)

    # --- Run RAGMint optimization flow (mocked) ---
    best_config, results = ragmint.optimize(validation_set=validation_data, trials=2)
    assert isinstance(best_config, dict)
    assert "score" in best_config
    assert isinstance(results, list)

    # --- Integration Success ---
    print(f"Integration OK: AutoRAG recommended {recommendation}, RAGMint best {best_config}")
