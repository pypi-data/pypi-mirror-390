import pytest
from ragmint.explainer import explain_results


def test_explain_results_gemini():
    """Gemini explanation should contain model-specific phrasing."""
    config_a = {"retriever": "FAISS", "embedding_model": "OpenAI"}
    config_b = {"retriever": "Chroma", "embedding_model": "SentenceTransformers"}
    result = explain_results(config_a, config_b, model="gemini")
    assert isinstance(result, str)
    assert "Gemini" in result or "gemini" in result


def test_explain_results_claude():
    """Claude explanation should contain model-specific phrasing."""
    config_a = {"retriever": "FAISS"}
    config_b = {"retriever": "Chroma"}
    result = explain_results(config_a, config_b, model="claude")
    assert isinstance(result, str)
    assert "Claude" in result or "claude" in result
