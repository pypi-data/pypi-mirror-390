import numpy as np
from ragmint.core.retriever import Retriever
from ragmint.core.embeddings import Embeddings


def test_retrieve_basic():
    docs = ["doc A", "doc B", "doc C"]
    embedder = Embeddings(backend="dummy")
    retriever = Retriever(embedder=embedder, documents=docs)

    results = retriever.retrieve("sample query", top_k=2)
    assert isinstance(results, list)
    assert len(results) == 2
    assert "text" in results[0]
    assert "score" in results[0]
