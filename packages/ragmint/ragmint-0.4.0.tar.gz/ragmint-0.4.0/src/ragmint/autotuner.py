"""
Auto-RAG Tuner
--------------
Automatically recommends and optimizes RAG configurations based on corpus statistics.
Integrates with RAGMint to perform full end-to-end tuning.
"""

import os
import logging
from statistics import mean
from typing import Dict, Any, Tuple, List, Optional
import random

from sentence_transformers import SentenceTransformer
from .tuner import RAGMint
from .core.evaluation import evaluate_config

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class AutoRAGTuner:
    DEFAULT_EMBEDDINGS = "sentence-transformers/all-MiniLM-L6-v2"

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
    # Chunk Size Suggestion
    # -----------------------------
    def suggest_chunk_sizes(
            self,
            model_name: Optional[str] = None,
            num_pairs: Optional[int] = None
    ) -> List[Tuple[int, int]]:
        if num_pairs is None:
            raise ValueError("⚠️ You must specify the number of pairs you want (num_pairs).")

        if model_name is None:
            model_name = self.DEFAULT_EMBEDDINGS
            logging.warning(f"⚠️ No embedding model provided. Using default: {model_name}")

        model = SentenceTransformer(model_name)
        max_tokens = getattr(model, "max_seq_length", 256)

        approx_words = max(1, int(max_tokens * 0.75))
        avg_len = self.corpus_stats.get("avg_len", 400)

        chunk_sizes = []
        for _ in range(num_pairs):
            max_chunk = max(50, min(approx_words, max(avg_len * 2, 50)))
            low = max(10, int(max_chunk * 0.5))
            high = max(low, max_chunk)
            chunk_size = random.randint(low, high)
            overlap = random.randint(10, min(300, chunk_size // 2))
            chunk_sizes.append((chunk_size, overlap))

        logging.info(f"📦 Suggested {num_pairs} (chunk_size, overlap) pairs: {chunk_sizes}")
        return chunk_sizes

    # -----------------------------
    # Recommendation Logic
    # -----------------------------
    def recommend(
        self,
        embedding_model: Optional[str] = None,
        num_chunk_pairs: Optional[int] = 5
    ) -> Dict[str, Any]:
        """
        Recommend retriever, embedding, chunking, and strategy based on corpus stats.

        Args:
            embedding_model (str, optional): User-provided embedding model.
            num_chunk_pairs (int, optional): Number of (chunk_size, overlap) pairs to generate.

        Returns:
            Dict[str, Any]: Recommended RAG configuration
        """
        size = self.corpus_stats.get("size", 0)
        avg_len = self.corpus_stats.get("avg_len", 0)

        # Determine retriever
        if size <= 2000:
            retriever = "BM25"
            if embedding_model is None:
                embedding_model = self.DEFAULT_EMBEDDINGS
        elif size <= 10000:
            retriever = "Chroma"
            if embedding_model is None:
                embedding_model = "sentence-transformers/paraphrase-MiniLM-L6-v2"
        else:
            retriever = "FAISS"
            if embedding_model is None:
                embedding_model = "sentence-transformers/all-mpnet-base-v2"

        if embedding_model is None:
            embedding_model = self.DEFAULT_EMBEDDINGS
            logging.warning(f"⚠️ Using default embedding model: {embedding_model}")

        # Suggest chunk sizes
        chunk_candidates = self.suggest_chunk_sizes(embedding_model, num_pairs=num_chunk_pairs)
        # Pick the first pair as default recommendation
        chunk_size, overlap = chunk_candidates[0]

        strategy = "fixed" if avg_len < 400 else "sentence"

        recommendation = {
            "retriever": retriever,
            "embedding_model": embedding_model,
            "chunk_size": chunk_size,
            "overlap": overlap,
            "strategy": strategy,
            "chunk_candidates": chunk_candidates,
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
        embedding_model: Optional[str] = None,
        num_chunk_pairs: Optional[int] = 5
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run a full automatic optimization using RAGMint.

        Args:
            validation_set (str): Path to validation set.
            metric (str): Metric to optimize.
            trials (int): Number of optimization trials.
            search_type (str): Search strategy.
            embedding_model (str, optional): User-provided embedding model.
            num_chunk_pairs (int, optional): Number of chunk pairs to try.

        Returns:
            Tuple[Dict[str, Any], List[Dict[str, Any]]]: Best configuration and all trial results.
        """
        rec = self.recommend(embedding_model=embedding_model, num_chunk_pairs=num_chunk_pairs)

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
