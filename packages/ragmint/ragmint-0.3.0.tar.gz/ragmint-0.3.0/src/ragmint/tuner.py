import os
import json
import logging
from typing import Any, Dict, List, Tuple
from time import perf_counter

from .core.pipeline import RAGPipeline
from .core.embeddings import Embeddings
from .core.retriever import Retriever
from .core.reranker import Reranker
from .core.evaluation import Evaluator
from .optimization.search import GridSearch, RandomSearch, BayesianSearch
from .utils.data_loader import load_validation_set

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class RAGMint:
    """
    Main RAG pipeline optimizer and evaluator.
    Runs combinations of retrievers, embeddings, and rerankers to find the best setup.
    """

    def __init__(
        self,
        docs_path: str,
        retrievers: List[str],
        embeddings: List[str],
        rerankers: List[str],
    ):
        self.docs_path = docs_path
        self.retrievers = retrievers
        self.embeddings = embeddings
        self.rerankers = rerankers

        self.documents: List[str] = self._load_docs()
        self.embeddings_cache: Dict[str, Any] = {}

    # -------------------------
    # Document Loading
    # -------------------------
    def _load_docs(self) -> List[str]:
        if not os.path.exists(self.docs_path):
            logging.warning(f"Corpus path not found: {self.docs_path}")
            return []

        docs = []
        for file in os.listdir(self.docs_path):
            if file.endswith((".txt", ".md", ".rst")):
                with open(os.path.join(self.docs_path, file), "r", encoding="utf-8") as f:
                    docs.append(f.read())

        logging.info(f"📚 Loaded {len(docs)} documents from {self.docs_path}")
        return docs

    # -------------------------
    # Embedding Cache
    # -------------------------
    def _embed_docs(self, model_name: str) -> Any:
        """Compute and cache document embeddings."""
        if model_name in self.embeddings_cache:
            return self.embeddings_cache[model_name]

        model = Embeddings(backend="huggingface", model_name=model_name)
        embeddings = model.encode(self.documents)
        self.embeddings_cache[model_name] = embeddings
        return embeddings

    # -------------------------
    # Build Pipeline
    # -------------------------
    def _build_pipeline(self, config: Dict[str, str]) -> RAGPipeline:
        """Builds a pipeline from one configuration."""
        retriever_backend = config["retriever"]
        model_name = config["embedding_model"]
        reranker_name = config["reranker"]

        # Load embeddings (cached)
        embeddings = self._embed_docs(model_name)
        embedder = Embeddings(backend="huggingface", model_name=model_name)

        # Initialize retriever with backend
        logging.info(f"⚙️ Initializing retriever backend: {retriever_backend}")
        retriever = Retriever(
            embedder=embedder,
            documents=self.documents,
            embeddings=embeddings,
            backend=retriever_backend,
        )

        reranker = Reranker(reranker_name)
        evaluator = Evaluator()

        return RAGPipeline(retriever, reranker, evaluator)

    # -------------------------
    # Evaluate Configuration
    # -------------------------
    def _evaluate_config(
        self, config: Dict[str, Any], validation: List[Dict[str, str]], metric: str
    ) -> Dict[str, float]:
        """Evaluates a single configuration."""
        pipeline = self._build_pipeline(config)
        scores = []
        start = perf_counter()

        for sample in validation:
            query = sample.get("question") or sample.get("query") or ""
            result = pipeline.run(query)
            score = result["metrics"].get(metric, 0.0)
            scores.append(score)

        elapsed = perf_counter() - start
        avg_score = sum(scores) / len(scores) if scores else 0.0

        return {
            metric: avg_score,
            "latency": elapsed / max(1, len(validation)),
        }

    # -------------------------
    # Optimize
    # -------------------------
    def optimize(
        self,
        validation_set: str,
        metric: str = "faithfulness",
        search_type: str = "random",
        trials: int = 10,
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """Run optimization search over retrievers/embeddings/rerankers."""
        validation = load_validation_set(validation_set or "default")

        search_space = {
            "retriever": self.retrievers,
            "embedding_model": self.embeddings,
            "reranker": self.rerankers,
        }

        logging.info(f"🚀 Starting {search_type} optimization with {trials} trials")

        # Select search strategy
        try:
            if search_type == "grid":
                searcher = GridSearch(search_space)
            elif search_type == "bayesian":
                searcher = BayesianSearch(search_space)
            else:
                searcher = RandomSearch(search_space, n_trials=trials)
        except Exception as e:
            logging.warning(f"⚠️ Fallback to RandomSearch due to missing deps: {e}")
            searcher = RandomSearch(search_space, n_trials=trials)

        # Run trials
        results = []
        for config in searcher:
            metrics = self._evaluate_config(config, validation, metric)
            result = {**config, **metrics}
            results.append(result)
            logging.info(f"🔹 Tested config: {config} -> {metrics}")

        best = max(results, key=lambda r: r.get(metric, 0.0)) if results else {}
        logging.info(f"🏆 Best configuration: {best}")

        return best, results
