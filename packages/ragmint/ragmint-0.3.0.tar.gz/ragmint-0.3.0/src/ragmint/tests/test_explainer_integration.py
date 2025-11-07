import os
import pytest
from ragmint.explainer import explain_results


@pytest.mark.integration
def test_real_gemini_explanation():
    """Run real Gemini call if GOOGLE_API_KEY is set."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not set")

    config_a = {"retriever": "FAISS", "embedding_model": "OpenAI"}
    config_b = {"retriever": "Chroma", "embedding_model": "SentenceTransformers"}

    result = explain_results(config_a, config_b, model="gemini-1.5-pro")
    assert isinstance(result, str)
    assert len(result) > 0
    print("\n[Gemini explanation]:", result[:200], "...")
