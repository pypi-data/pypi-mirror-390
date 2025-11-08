import pytest
from ragmint.integrations.config_adapter import LangchainConfigAdapter

def test_default_conversion():
    """Test that default config values are applied correctly."""
    cfg = {
        "retriever": "FAISS",
        "embedding_model": "all-MiniLM-L6-v2",
        "chunk_size": 500,
        "overlap": 100
    }

    adapter = LangchainConfigAdapter(cfg)
    result = adapter.to_standard_config()

    assert result["retriever"].lower() == "faiss"
    assert result["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
    assert result["chunk_size"] == 500
    assert result["overlap"] == 100


def test_missing_fields_are_defaulted():
    """Ensure missing optional fields (e.g. chunk params) are filled in."""
    cfg = {"retriever": "BM25", "embedding_model": "all-MiniLM-L6-v2"}
    adapter = LangchainConfigAdapter(cfg)
    result = adapter.to_standard_config()

    assert "chunk_size" in result
    assert "overlap" in result
    assert result["chunk_size"] > 0
    assert result["overlap"] >= 0


def test_validation_of_invalid_retriever():
    """Ensure invalid retriever names raise an informative error."""
    cfg = {"retriever": "InvalidBackend", "embedding_model": "all-MiniLM-L6-v2"}

    with pytest.raises(ValueError, match="Unsupported retriever backend"):
        LangchainConfigAdapter(cfg).to_standard_config()
