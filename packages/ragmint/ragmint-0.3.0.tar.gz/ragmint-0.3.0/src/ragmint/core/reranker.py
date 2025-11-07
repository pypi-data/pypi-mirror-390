from typing import List, Dict, Any
import numpy as np


class Reranker:
    """
    Supports:
      - MMR (Maximal Marginal Relevance)
      - Dummy CrossEncoder (for demonstration)
    """

    def __init__(self, mode: str = "mmr", lambda_param: float = 0.5, seed: int = 42):
        self.mode = mode
        self.lambda_param = lambda_param
        np.random.seed(seed)

    def rerank(self, query: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not docs:
            return []

        if self.mode == "crossencoder":
            return self._crossencoder_rerank(query, docs)
        return self._mmr_rerank(query, docs)

    def _mmr_rerank(self, query: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform MMR reranking using dummy similarity scores."""
        selected = []
        remaining = docs.copy()

        while remaining and len(selected) < len(docs):
            if not selected:
                # pick doc with highest base score
                best = max(remaining, key=lambda d: d["score"])
            else:
                # MMR balancing between relevance and diversity
                mmr_scores = []
                for d in remaining:
                    max_div = max(
                        [self._similarity(d["text"], s["text"]) for s in selected],
                        default=0,
                    )
                    mmr_score = (
                        self.lambda_param * d["score"]
                        - (1 - self.lambda_param) * max_div
                    )
                    mmr_scores.append(mmr_score)
                best = remaining[int(np.argmax(mmr_scores))]
            selected.append(best)
            remaining.remove(best)

        return selected

    def _crossencoder_rerank(self, query: str, docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Adds a small random perturbation to simulate crossencoder reranking."""
        for d in docs:
            d["score"] += np.random.uniform(0, 0.1)
        return sorted(docs, key=lambda d: d["score"], reverse=True)

    def _similarity(self, a: str, b: str) -> float:
        """Dummy similarity function between two strings."""
        # Deterministic pseudo-similarity based on hash
        return abs(hash(a + b)) % 100 / 100.0
