import time
from typing import Dict, Any
from difflib import SequenceMatcher


class Evaluator:
    """
    Simple evaluation of generated answers:
      - Faithfulness (similarity between answer and context)
      - Latency
    """

    def __init__(self):
        pass

    def evaluate(self, query: str, answer: str, context: str) -> Dict[str, Any]:
        start = time.time()
        faithfulness = self._similarity(answer, context)
        latency = time.time() - start

        return {
            "faithfulness": faithfulness,
            "latency": latency,
        }

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

def evaluate_config(config, validation_data):
    evaluator = Evaluator()
    results = []
    for sample in validation_data:
        query = sample.get("query", "")
        answer = sample.get("answer", "")
        context = sample.get("context", "")
        results.append(evaluator.evaluate(query, answer, context))
    return results

