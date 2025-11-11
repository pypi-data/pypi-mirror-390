from typing import Any, Dict, Optional
from .retriever import Retriever
from .reranker import Reranker
from .evaluation import Evaluator
from .chunking import Chunker


class RAGPipeline:
    """
    Core Retrieval-Augmented Generation pipeline.
    Retrieves, reranks, and evaluates a query given the configured backends.
    Supports text chunking for optimal retrieval performance.
    """

    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker,
        evaluator: Evaluator,
        chunk_size: int = 500,
        overlap: int = 100,
        chunking_strategy: str = "fixed"
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.evaluator = evaluator

        # Initialize chunker for preprocessing
        self.chunker = Chunker(chunk_size=chunk_size, overlap=overlap, strategy=chunking_strategy)

    def preprocess_docs(self, documents):
        """Applies the selected chunking strategy to the document set."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk_text(doc)
            all_chunks.extend(chunks)
        return all_chunks

    def run(self, query: str, top_k: int = 5, use_chunking: bool = True) -> Dict[str, Any]:
        # Optional preprocessing step
        if use_chunking and hasattr(self.retriever, "documents") and self.retriever.documents:
            self.retriever.documents = self.preprocess_docs(self.retriever.documents)

        # Retrieve documents
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)

        # Rerank
        reranked_docs = self.reranker.rerank(query, retrieved_docs)

        # Construct pseudo-answer
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
