from typing import List
import re

try:
    import tiktoken
except ImportError:
    tiktoken = None

try:
    import nltk
    nltk.download("punkt", quiet=True)
    from nltk.tokenize import sent_tokenize
except ImportError:
    sent_tokenize = None


class Chunker:
    """
    Handles text chunking strategies:
    - fixed: character-based
    - token: token-based (requires tiktoken)
    - sentence: splits by full sentences (requires nltk)
    """

    def __init__(self, chunk_size: int = 500, overlap: int = 100, strategy: str = "fixed"):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.strategy = strategy

    def chunk_text(self, text: str) -> List[str]:
        """Dispatches to the correct chunking strategy."""
        if self.strategy == "token" and tiktoken:
            return self._chunk_by_tokens(text)
        elif self.strategy == "sentence" and sent_tokenize:
            return self._chunk_by_sentences(text)
        else:
            return self._chunk_fixed(text)

    # -------------------------------
    # Fixed-length (default)
    # -------------------------------
    def _chunk_fixed(self, text: str) -> List[str]:
        chunks = []
        start = 0
        while start < len(text):
            end = start + self.chunk_size
            chunks.append(text[start:end])
            start += self.chunk_size - self.overlap
        return chunks

    # -------------------------------
    # Token-based (for LLM embedding)
    # -------------------------------
    def _chunk_by_tokens(self, text: str) -> List[str]:
        if not tiktoken:
            raise ImportError("tiktoken is required for token-based chunking.")
        enc = tiktoken.get_encoding("cl100k_base")
        tokens = enc.encode(text)

        chunks = []
        for i in range(0, len(tokens), self.chunk_size - self.overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunks.append(enc.decode(chunk_tokens))
        return chunks

    # -------------------------------
    # Sentence-based
    # -------------------------------
    def _chunk_by_sentences(self, text: str) -> List[str]:
        if not sent_tokenize:
            raise ImportError("nltk is required for sentence-based chunking.")
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks
