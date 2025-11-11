import time
from typing import Dict, Any, List
import numpy as np
from .embeddings import Embeddings


class Evaluator:
    """
    Semantic evaluation of generated answers:
      - Faithfulness: cosine similarity between answer and context embeddings
      - Latency: time to compute embeddings and similarity
    """

    def __init__(self, embeddings: Embeddings = None):
        self.embeddings = embeddings or Embeddings()  # default to HuggingFace all-MiniLM-L6-v2

    def evaluate(self, query: str, answer: str, context: str) -> Dict[str, Any]:
        start = time.time()

        # Compute embeddings
        emb_answer = self.embeddings.encode(answer)
        emb_context = self.embeddings.encode(context)

        # Compute cosine similarity
        faithfulness = self._cosine_similarity(emb_answer, emb_context)

        faithfulness = np.clip(faithfulness, 0.0, 1.0)

        latency = time.time() - start
        return {
            "faithfulness": faithfulness,
            "latency": latency,
        }

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        # Ensure vectors are 1D
        a = a.flatten()
        b = b.flatten()
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def evaluate_config(config: Dict[str, Any], validation_data: List[Dict[str, str]], embeddings: Embeddings = None) -> \
List[Dict[str, Any]]:
    """
    Evaluate a set of model outputs against validation data.
    """
    evaluator = Evaluator(embeddings=embeddings)
    results = []
    for sample in validation_data:
        query = sample.get("query", "")
        answer = sample.get("answer", "")
        context = sample.get("context", "")
        results.append(evaluator.evaluate(query, answer, context))
    return results
