"""
RAGMint → LangChain Config Adapter
----------------------------------
Takes RAGMint or AutoRAGTuner recommendations and converts them into
a normalized, pickle-safe configuration that can be used to build
a LangChain RAG pipeline later.
"""

import json
import pickle
from pathlib import Path
from typing import Dict, Any


class LangchainConfigAdapter:
    """
    Converts RAGMint recommendations into LangChain-compatible configs.

    Example:
        adapter = LangChainConfigAdapter()
        cfg = adapter.prepare(recommendation)
        adapter.save(cfg, "best_config.pkl")
    """

    DEFAULT_EMBEDDINGS = {
        "OpenAI": "sentence-transformers/all-MiniLM-L6-v2",
        "SentenceTransformers": "sentence-transformers/all-MiniLM-L6-v2",
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "InstructorXL": "hkunlp/instructor-xl"
    }

    SUPPORTED_RETRIEVERS = {"faiss", "chroma", "bm25", "numpy", "sklearn"}

    def __init__(self, recommendation: Dict[str, Any] | None = None):
        self.recommendation = recommendation

    def prepare(self, recommendation: Dict[str, Any] | None = None) -> Dict[str, Any]:
        recommendation = recommendation or self.recommendation or {}
        """
        Normalize and validate configuration for LangChain use.

        Returns:
            dict with clean retriever, embedding, and chunking settings.
        """
        retriever = recommendation.get("retriever", "faiss").lower()
        embedding_model = recommendation.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        chunk_size = recommendation.get("chunk_size", 400)
        overlap = recommendation.get("overlap", 100)

        # Normalize embedding model names
        embedding_model = self.DEFAULT_EMBEDDINGS.get(embedding_model, embedding_model)

        # Validate retriever backend
        if retriever not in self.SUPPORTED_RETRIEVERS:
            raise ValueError(f"Unsupported retriever backend: {retriever}")

        config = {
            "retriever": retriever,
            "embedding_model": embedding_model,
            "chunk_size": int(chunk_size),
            "overlap": int(overlap),
        }

        return config

    def save(self, config: Dict[str, Any], path: str):
        """
        Save configuration to a pickle file.
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(config, f)
        print(f"💾 Saved LangChain config → {path}")

    def load(self, path: str) -> Dict[str, Any]:
        """
        Load configuration from a pickle file.
        """
        with open(path, "rb") as f:
            cfg = pickle.load(f)
        print(f"✅ Loaded LangChain config ← {path}")
        return cfg

    def to_json(self, config: Dict[str, Any], path: str):
        """
        Save configuration as JSON (for human readability).
        """
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        print(f"📝 Exported LangChain config → {path}")

    # Alias for backward compatibility
    def to_standard_config(self, recommendation: Dict[str, Any] | None = None) -> Dict[str, Any]:
        """Alias for backward compatibility with older test suites."""
        return self.prepare(recommendation)