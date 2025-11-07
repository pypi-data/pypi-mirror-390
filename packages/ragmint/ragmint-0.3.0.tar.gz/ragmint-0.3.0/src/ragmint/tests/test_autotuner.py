import pytest
from ragmint.autotuner import AutoRAGTuner


def test_autorag_recommend_small():
    """Small corpus should trigger BM25 + OpenAI."""
    tuner = AutoRAGTuner({"size": 500, "avg_len": 150})
    rec = tuner.recommend()
    assert rec["retriever"] == "BM25"
    assert rec["embedding_model"] == "OpenAI"


def test_autorag_recommend_medium():
    """Medium corpus should trigger Chroma + SentenceTransformers."""
    tuner = AutoRAGTuner({"size": 5000, "avg_len": 200})
    rec = tuner.recommend()
    assert rec["retriever"] == "Chroma"
    assert rec["embedding_model"] == "SentenceTransformers"


def test_autorag_recommend_large():
    """Large corpus should trigger FAISS + InstructorXL."""
    tuner = AutoRAGTuner({"size": 50000, "avg_len": 300})
    rec = tuner.recommend()
    assert rec["retriever"] == "FAISS"
    assert rec["embedding_model"] == "InstructorXL"


def test_autorag_auto_tune(monkeypatch):
    """Test auto_tune with a mock validation dataset."""
    tuner = AutoRAGTuner({"size": 12000, "avg_len": 250})

    # Monkeypatch evaluate_config inside autotuner
    import ragmint.autotuner as autotuner
    def mock_eval(config, data):
        return {"faithfulness": 0.9, "latency": 0.01}
    monkeypatch.setattr(autotuner, "evaluate_config", mock_eval)

    result = tuner.auto_tune([{"question": "What is AI?", "answer": "Artificial Intelligence"}])
    assert "recommended" in result
    assert "results" in result
    assert isinstance(result["results"], dict)
