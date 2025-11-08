"""
Auto-RAG Tuner
--------------
Automatically recommends and optimizes RAG configurations based on corpus statistics.
Integrates with RAGMint to perform full end-to-end tuning.
"""

import os
import logging
from statistics import mean
from typing import Dict, Any, Tuple, List

from .tuner import RAGMint
from .core.evaluation import evaluate_config

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class AutoRAGTuner:
    def __init__(self, docs_path: str):
        """
        AutoRAGTuner automatically analyzes a corpus and runs an optimized RAG tuning pipeline.

        Args:
            docs_path (str): Path to the directory containing documents (.txt, .md, .rst)
        """
        self.docs_path = docs_path
        self.corpus_stats = self._analyze_corpus()

    # -----------------------------
    # Corpus Analysis
    # -----------------------------
    def _analyze_corpus(self) -> Dict[str, Any]:
        """Compute corpus size, average length, and number of documents."""
        docs = []
        total_chars = 0
        num_docs = 0

        if not os.path.exists(self.docs_path):
            logging.warning(f"⚠️ Corpus path not found: {self.docs_path}")
            return {"size": 0, "avg_len": 0, "num_docs": 0}

        for file in os.listdir(self.docs_path):
            if file.endswith((".txt", ".md", ".rst")):
                with open(os.path.join(self.docs_path, file), "r", encoding="utf-8") as f:
                    content = f.read()
                    docs.append(content)
                    total_chars += len(content)
                    num_docs += 1

        avg_len = int(mean([len(d) for d in docs])) if docs else 0
        stats = {"size": total_chars, "avg_len": avg_len, "num_docs": num_docs}
        logging.info(f"📊 Corpus stats: {stats}")
        return stats

    # -----------------------------
    # Recommendation Logic
    # -----------------------------
    def recommend(self) -> Dict[str, Any]:
        """Recommend retriever, embedding, and chunking based on corpus stats."""
        size = self.corpus_stats.get("size", 0)
        avg_len = self.corpus_stats.get("avg_len", 0)
        num_docs = self.corpus_stats.get("num_docs", 0)

        # Heuristic-based tuning
        # Determine chunking heuristics first
        if avg_len < 200:
            chunk_size, overlap = 300, 50
        elif avg_len < 500:
            chunk_size, overlap = 500, 100
        else:
            chunk_size, overlap = 800, 150

        # Determine retriever–embedding based on corpus size
        if size <= 2000:
            retriever = "BM25"
            embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        elif size <= 10000:
            retriever = "Chroma"
            embedding_model = "sentence-transformers/paraphrase-MiniLM-L6-v2"
        else:
            retriever = "FAISS"
            embedding_model = "sentence-transformers/all-mpnet-base-v2"

        strategy = "fixed" if avg_len < 400 else "sentence"

        recommendation = {
            "retriever": retriever,
            "embedding_model": embedding_model,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "strategy": strategy,
        }

        logging.info(f"🔮 AutoRAG Recommendation: {recommendation}")
        return recommendation

    # -----------------------------
    # Full Auto-Tuning
    # -----------------------------
    def auto_tune(
        self,
        validation_set: str = None,
        metric: str = "faithfulness",
        trials: int = 5,
        search_type: str = "random",
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run a full automatic optimization using RAGMint.

        Automatically:
        - Recommends initial config (retriever, embedding, chunking)
        - Launches RAGMint optimization trials
        - Returns best configuration and results
        """
        rec = self.recommend()

        logging.info("🚀 Launching full AutoRAG optimization with RAGMint")

        tuner = RAGMint(
            docs_path=self.docs_path,
            retrievers=[rec["retriever"]],
            embeddings=[rec["embedding_model"]],
            rerankers=["mmr"],
            chunk_sizes=[rec["chunk_size"]],
            overlaps=[rec["overlap"]],
            strategies=[rec["strategy"]],
        )

        best, results = tuner.optimize(
            validation_set=validation_set,
            metric=metric,
            trials=trials,
            search_type=search_type,
        )

        logging.info(f"🏁 AutoRAG tuning complete. Best: {best}")
        return best, results
