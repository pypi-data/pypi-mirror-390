from typing import List, Dict, Any, Optional
import numpy as np
from .embeddings import Embeddings

# Optional imports
try:
    import faiss
except ImportError:
    faiss = None

try:
    import chromadb
except ImportError:
    chromadb = None

try:
    from sklearn.neighbors import BallTree
except ImportError:
    BallTree = None

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None


class Retriever:
    """
    Multi-backend retriever supporting:
        - "numpy"  : basic cosine similarity (dense)
        - "faiss"  : high-performance dense retriever
        - "chroma" : persistent vector DB
        - "sklearn": BallTree (cosine or Euclidean)
        - "bm25"   : lexical retriever using Rank-BM25

    Example:
        retriever = Retriever(embedder, documents=["A", "B", "C"], backend="bm25")
        results = retriever.retrieve("example query", top_k=3)
    """

    def __init__(
        self,
        embedder: Optional[Embeddings] = None,
        documents: Optional[List[str]] = None,
        embeddings: Optional[np.ndarray] = None,
        backend: str = "numpy",
    ):
        self.embedder = embedder
        self.documents = documents or []
        self.backend = backend.lower()
        self.embeddings = None
        self.index = None
        self.client = None
        self.bm25 = None

        # Initialize embeddings for dense backends
        if self.backend not in ["bm25"]:
            if embeddings is not None:
                self.embeddings = np.array(embeddings)
            elif self.documents and self.embedder:
                self.embeddings = self.embedder.encode(self.documents)
            else:
                self.embeddings = np.zeros((0, getattr(self.embedder, "dim", 768)))

            # Normalize for cosine
            if self.embeddings.size > 0:
                self.embeddings = self._normalize(self.embeddings)

        # Initialize backend
        self._init_backend()

    # ------------------------
    # Backend Initialization
    # ------------------------
    def _init_backend(self):
        if self.backend == "faiss":
            if faiss is None:
                raise ImportError("faiss not installed. Run `pip install faiss-cpu`.")
            self.index = faiss.IndexFlatIP(self.embedder.dim)
            self.index.add(self.embeddings.astype("float32"))

        elif self.backend == "chroma":
            if chromadb is None:
                raise ImportError("chromadb not installed. Run `pip install chromadb`.")
            self.client = chromadb.Client()
            self.collection = self.client.create_collection(name="ragmint_retriever")
            for i, doc in enumerate(self.documents):
                self.collection.add(
                    ids=[str(i)],
                    documents=[doc],
                    embeddings=[self.embeddings[i].tolist()],
                )

        elif self.backend == "sklearn":
            if BallTree is None:
                raise ImportError("scikit-learn not installed. Run `pip install scikit-learn`.")
            self.index = BallTree(self.embeddings)

        elif self.backend == "bm25":
            if BM25Okapi is None:
                raise ImportError("rank-bm25 not installed. Run `pip install rank-bm25`.")
            tokenized_corpus = [doc.lower().split() for doc in self.documents]
            self.bm25 = BM25Okapi(tokenized_corpus)

        elif self.backend != "numpy":
            raise ValueError(f"Unsupported retriever backend: {self.backend}")

    # ------------------------
    # Retrieval
    # ------------------------
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if len(self.documents) == 0:
            return [{"text": "", "score": 0.0}]

        # BM25 retrieval (lexical)
        if self.backend == "bm25":
            tokenized_query = query.lower().split()
            scores = self.bm25.get_scores(tokenized_query)
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [
                {"text": self.documents[i], "score": float(scores[i])}
                for i in top_indices
            ]

        # Dense retrieval (others)
        if self.embeddings is None or self.embeddings.size == 0:
            return [{"text": "", "score": 0.0}]

        query_vec = self.embedder.encode([query])[0]
        query_vec = self._normalize(query_vec)

        if self.backend == "numpy":
            scores = np.dot(self.embeddings, query_vec)
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [{"text": self.documents[i], "score": float(scores[i])} for i in top_indices]

        elif self.backend == "faiss":
            query_vec = np.expand_dims(query_vec.astype("float32"), axis=0)
            scores, indices = self.index.search(query_vec, top_k)
            return [{"text": self.documents[int(i)], "score": float(scores[0][j])} for j, i in enumerate(indices[0])]

        elif self.backend == "chroma":
            results = self.collection.query(query_texts=[query], n_results=top_k)
            docs = results["documents"][0]
            scores = results["distances"][0]
            return [{"text": d, "score": 1 - s} for d, s in zip(docs, scores)]

        elif self.backend == "sklearn":
            distances, indices = self.index.query([query_vec], k=top_k)
            scores = 1 - distances[0]
            return [{"text": self.documents[int(i)], "score": float(scores[j])} for j, i in enumerate(indices[0])]

        else:
            raise ValueError(f"Unknown backend: {self.backend}")

    # ------------------------
    # Utils
    # ------------------------
    @staticmethod
    def _normalize(vectors: np.ndarray) -> np.ndarray:
        if vectors.ndim == 1:
            norm = np.linalg.norm(vectors)
            return vectors / norm if norm > 0 else vectors
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return np.divide(vectors, norms, out=np.zeros_like(vectors), where=norms != 0)
