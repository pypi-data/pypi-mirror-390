"""
Auto-RAG Tuner
--------------
Recommends retriever–embedding pairs dynamically based on corpus size
and dataset characteristics. Integrates seamlessly with RAGMint evaluator.
"""

from .core.evaluation import evaluate_config


class AutoRAGTuner:
    def __init__(self, corpus_stats: dict):
        """
        corpus_stats: dict
            Example: {'size': 12000, 'avg_len': 240}
        """
        self.corpus_stats = corpus_stats

    def recommend(self):
        size = self.corpus_stats.get("size", 0)
        avg_len = self.corpus_stats.get("avg_len", 0)

        if size < 1000:
            return {"retriever": "BM25", "embedding_model": "OpenAI"}
        elif size < 10000:
            return {"retriever": "Chroma", "embedding_model": "SentenceTransformers"}
        else:
            return {"retriever": "FAISS", "embedding_model": "InstructorXL"}

    def auto_tune(self, validation_data):
        config = self.recommend()
        results = evaluate_config(config, validation_data)
        return {"recommended": config, "results": results}
