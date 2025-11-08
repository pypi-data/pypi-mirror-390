"""
LangChain Pre-Build Integration
-------------------------------
This module bridges RAGMint's auto-tuning system with LangChain,
returning retriever and embedding components that can plug directly
into any LangChain RAG pipeline.

Example:
    from ragmint.integrations.langchain_prebuilder import LangChainPrebuilder
    from langchain.chains import RetrievalQA
    from langchain_openai import ChatOpenAI

    prebuilder = LangChainPrebuilder(best_cfg)
    retriever, embeddings = prebuilder.prepare(documents)

    llm = ChatOpenAI(model="gpt-4o-mini")
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
"""

from typing import List, Tuple, Dict, Any


try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.retrievers import BM25Retriever


class LangchainPrebuilder:
    """
    Dynamically builds LangChain retriever and embedding objects
    based on a RAGMint configuration dictionary.
    """

    def __init__(self, cfg: Dict[str, Any]):
        """
        Args:
            cfg (dict): RAGMint configuration with keys:
                - retriever: "faiss" | "chroma" | "bm25"
                - embedding_model: HuggingFace model name
                - chunk_size: int (default=500)
                - overlap: int (default=100)
        """
        self.cfg = cfg
        self.retriever_backend = cfg.get("retriever", "faiss").lower()
        self.embedding_model = cfg.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")
        self.chunk_size = int(cfg.get("chunk_size", 500))
        self.overlap = int(cfg.get("overlap", 100))

    def prepare(self, documents: List[str]) -> Tuple[Any, Any]:
        """
        Prepares LangChain-compatible retriever and embeddings.

        Args:
            documents (list[str]): Corpus texts

        Returns:
            (retriever, embeddings): Tuple of initialized LangChain retriever and embedding model
        """
        # 1️⃣ Split into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.overlap
        )
        docs = splitter.create_documents(documents)

        # 2️⃣ Create embeddings
        embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model)

        # 3️⃣ Build retriever
        retriever = self._build_retriever(docs, embeddings)
        return retriever, embeddings

    def _build_retriever(self, docs, embeddings):
        """Internal helper for building retriever backend."""
        backend = self.retriever_backend

        if backend == "faiss":
            db = FAISS.from_documents(docs, embeddings)
            return db.as_retriever(search_kwargs={"k": 5})

        elif backend == "chroma":
            db = Chroma.from_documents(docs, embeddings, collection_name="ragmint_docs")
            return db.as_retriever(search_kwargs={"k": 5})


        elif backend == "bm25":
            # Support both Document objects and raw text strings
            texts = [getattr(d, "page_content", d) for d in docs]
            retriever = BM25Retriever.from_texts(texts)
            retriever.k = 5
            return retriever

        else:
            raise ValueError(f"Unsupported retriever backend: {backend}")
