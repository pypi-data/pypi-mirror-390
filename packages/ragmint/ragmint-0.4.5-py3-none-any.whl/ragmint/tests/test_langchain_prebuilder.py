import pytest
from unittest.mock import MagicMock, patch
from ragmint.integrations.langchain_prebuilder import LangchainPrebuilder


@pytest.fixture
def sample_docs():
    """Small sample corpus for testing."""
    return ["AI is transforming the world.", "RAG pipelines improve retrieval."]


@pytest.fixture
def sample_config():
    """Default configuration for tests."""
    return {
        "retriever": "faiss",
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "chunk_size": 200,
        "overlap": 50,
    }


@patch("ragmint.integrations.langchain_prebuilder.HuggingFaceEmbeddings", autospec=True)
@patch("ragmint.integrations.langchain_prebuilder.RecursiveCharacterTextSplitter", autospec=True)
def test_prepare_creates_components(mock_splitter, mock_embedder, sample_config, sample_docs):
    """Ensure prepare() builds retriever and embedding components properly."""
    mock_splitter.return_value.create_documents.return_value = ["doc1", "doc2"]
    mock_embedder.return_value = MagicMock()

    # Patch FAISS to avoid building a real index
    with patch("ragmint.integrations.langchain_prebuilder.FAISS", autospec=True) as mock_faiss:
        mock_db = MagicMock()
        mock_faiss.from_documents.return_value = mock_db
        mock_db.as_retriever.return_value = "mock_retriever"

        builder = LangchainPrebuilder(sample_config)
        retriever, embeddings = builder.prepare(sample_docs)

        assert retriever == "mock_retriever"
        assert embeddings == mock_embedder.return_value

        mock_splitter.assert_called_once()
        mock_embedder.assert_called_once_with(model_name="sentence-transformers/all-MiniLM-L6-v2")
        mock_faiss.from_documents.assert_called_once()


@pytest.mark.parametrize("backend", ["faiss", "chroma", "bm25"])
def test_build_retriever_backends(sample_config, sample_docs, backend):
    """Check retriever creation for each backend."""
    cfg = dict(sample_config)
    cfg["retriever"] = backend

    builder = LangchainPrebuilder(cfg)

    # Mock embeddings + docs
    fake_embeddings = MagicMock()
    fake_docs = ["d1", "d2"]

    with patch("ragmint.integrations.langchain_prebuilder.FAISS.from_documents", return_value=MagicMock()) as mock_faiss, \
         patch("ragmint.integrations.langchain_prebuilder.Chroma.from_documents", return_value=MagicMock()) as mock_chroma, \
         patch("ragmint.integrations.langchain_prebuilder.BM25Retriever.from_texts", return_value=MagicMock()) as mock_bm25:
        retriever = builder._build_retriever(fake_docs, fake_embeddings)

        # Validate retriever creation per backend
        if backend == "faiss":
            mock_faiss.assert_called_once()
        elif backend == "chroma":
            mock_chroma.assert_called_once()
        elif backend == "bm25":
            mock_bm25.assert_called_once()

        assert retriever is not None


def test_invalid_backend_raises(sample_config):
    """Ensure ValueError is raised for unsupported retriever."""
    cfg = dict(sample_config)
    cfg["retriever"] = "invalid"

    builder = LangchainPrebuilder(cfg)
    with pytest.raises(ValueError, match="Unsupported retriever backend"):
        builder._build_retriever(["doc"], MagicMock())
