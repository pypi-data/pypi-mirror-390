import numpy as np
from dotenv import load_dotenv

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None


class Embeddings:
    """
    Wrapper for embedding backends: HuggingFace (SentenceTransformers) or Dummy.

    Example:
        model = Embeddings("huggingface", model_name="all-MiniLM-L6-v2")
        embeddings = model.encode(["example text"])
    """

    def __init__(self, backend: str = "huggingface", model_name: str = None):
        load_dotenv()
        self.backend = backend.lower()
        self.model_name = model_name or "all-MiniLM-L6-v2"

        if self.backend == "huggingface":
            if SentenceTransformer is None:
                raise ImportError("Please install `sentence-transformers` to use HuggingFace embeddings.")
            self.model = SentenceTransformer(self.model_name)
            self.dim = self.model.get_sentence_embedding_dimension()

        elif self.backend == "dummy":
            self.model = None
            self.dim = 768  # Default embedding dimension for dummy backend

        else:
            raise ValueError(f"Unsupported embedding backend: {backend}")

    def encode(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        if self.backend == "huggingface":
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        elif self.backend == "dummy":
            # Return a NumPy array of shape (len(texts), dim)
            embeddings = np.random.rand(len(texts), self.dim).astype(np.float32)

        else:
            raise ValueError(f"Unknown embedding backend: {self.backend}")

        # ✅ Always ensure NumPy array output
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.array(embeddings, dtype=np.float32)

        return embeddings
