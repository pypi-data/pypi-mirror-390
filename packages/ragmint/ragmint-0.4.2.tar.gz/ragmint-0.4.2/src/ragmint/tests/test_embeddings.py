import numpy as np
import pytest
from ragmint.core.embeddings import Embeddings


def test_dummy_backend_output_shape():
    model = Embeddings(backend="dummy")
    texts = ["hello", "world"]
    embeddings = model.encode(texts)

    # Expect 2x768 array
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 768)
    assert embeddings.dtype == np.float32


def test_dummy_backend_single_string():
    model = Embeddings(backend="dummy")
    text = "test"
    embeddings = model.encode(text)

    assert embeddings.shape == (1, 768)
    assert isinstance(embeddings, np.ndarray)


'''@pytest.mark.skipif(
    not hasattr(__import__('importlib').util.find_spec("sentence_transformers"), "loader"),
    reason="sentence-transformers not installed"
)
def test_huggingface_backend_output_shape():
    model = Embeddings(backend="huggingface", model_name="all-MiniLM-L6-v2")
    texts = ["This is a test.", "Another sentence."]
    embeddings = model.encode(texts)

    # Expect 2x384 for MiniLM-L6-v2
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.ndim == 2
    assert embeddings.shape[0] == len(texts)
    assert embeddings.dtype == np.float32
'''

def test_invalid_backend():
    try:
        Embeddings(backend="unknown")
    except ValueError as e:
        assert "Unsupported embedding backend" in str(e)
