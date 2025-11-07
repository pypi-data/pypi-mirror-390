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


class Retriever:
    """
    Multi-backend retriever supporting NumPy, FAISS, Chroma, and Scikit-learn BallTree.

    Backends:
        - "numpy"  : basic cosine similarity using NumPy (default)
        - "faiss"  : fast dense vector search (in-memory)
        - "chroma" : persistent local vector database
        - "sklearn": BallTree for cosine or Euclidean distance

    Example:
        retriever = Retriever(embedder, documents=["A", "B", "C"], backend="faiss")
        retriever.retrieve("example query", top_k=3)
    """

    def __init__(
        self,
        embedder: Embeddings,
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

        # Initialize embeddings
        if embeddings is not None:
            self.embeddings = np.array(embeddings)
        elif self.documents:
            self.embeddings = self.embedder.encode(self.documents)
        else:
            self.embeddings = np.zeros((0, self.embedder.dim))

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

        elif self.backend != "numpy":
            raise ValueError(f"Unsupported retriever backend: {self.backend}")

    # ------------------------
    # Retrieval
    # ------------------------
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if len(self.documents) == 0 or self.embeddings.size == 0:
            return [{"text": "", "score": 0.0}]

        query_vec = self.embedder.encode([query])[0]
        query_vec = self._normalize(query_vec)

        if self.backend == "numpy":
            scores = np.dot(self.embeddings, query_vec)
            top_indices = np.argsort(scores)[::-1][:top_k]
            return [
                {"text": self.documents[i], "score": float(scores[i])}
                for i in top_indices
            ]

        elif self.backend == "faiss":
            query_vec = np.expand_dims(query_vec.astype("float32"), axis=0)
            scores, indices = self.index.search(query_vec, top_k)
            return [
                {"text": self.documents[int(i)], "score": float(scores[0][j])}
                for j, i in enumerate(indices[0])
            ]

        elif self.backend == "chroma":
            results = self.collection.query(query_texts=[query], n_results=top_k)
            docs = results["documents"][0]
            scores = results["distances"][0]
            return [{"text": d, "score": 1 - s} for d, s in zip(docs, scores)]

        elif self.backend == "sklearn":
            distances, indices = self.index.query([query_vec], k=top_k)
            scores = 1 - distances[0]
            return [
                {"text": self.documents[int(i)], "score": float(scores[j])}
                for j, i in enumerate(indices[0])
            ]

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
