from typing import Any, Dict
from .retriever import Retriever
from .reranker import Reranker
from .evaluation import Evaluator


class RAGPipeline:
    """
    Core Retrieval-Augmented Generation pipeline.
    Retrieves, reranks, and evaluates a query given the configured backends.
    """

    def __init__(self, retriever: Retriever, reranker: Reranker, evaluator: Evaluator):
        self.retriever = retriever
        self.reranker = reranker
        self.evaluator = evaluator

    def run(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        # Retrieve
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)

        # Rerank
        reranked_docs = self.reranker.rerank(query, retrieved_docs)

        # Construct pseudo-answer from top doc
        answer = reranked_docs[0]["text"] if reranked_docs else ""
        context = "\n".join([d["text"] for d in reranked_docs])

        # Evaluate
        metrics = self.evaluator.evaluate(query, answer, context)

        return {
            "query": query,
            "answer": answer,
            "docs": reranked_docs,
            "metrics": metrics,
        }
