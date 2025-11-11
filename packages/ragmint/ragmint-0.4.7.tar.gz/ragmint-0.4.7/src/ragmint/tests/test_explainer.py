import pytest
import sys
import types
from ragmint.explainer import explain_results


def test_explain_results_with_claude(monkeypatch):
    """Claude explanation should use Anthropic API path when ANTHROPIC_API_KEY is set."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    # Create a fake anthropic module with the required interface
    mock_anthropic = types.ModuleType("anthropic")

    class MockContent:
        text = "Claude: The best configuration performs well due to optimized chunk size."

    class MockMessages:
        def create(self, *args, **kwargs):
            return type("MockResponse", (), {"content": [MockContent()]})()

    class MockClient:
        def __init__(self, api_key):
            self.messages = MockMessages()

    mock_anthropic.Anthropic = MockClient
    sys.modules["anthropic"] = mock_anthropic  # Inject fake module

    best = {"retriever": "Chroma", "metric": 0.9}
    all_results = [{"retriever": "FAISS", "metric": 0.85}]
    corpus_stats = {"size": 10000, "avg_len": 400, "num_docs": 20}

    result = explain_results(best, all_results, corpus_stats, model="claude-3-opus-20240229")

    assert isinstance(result, str)
    assert "Claude" in result or "claude" in result
