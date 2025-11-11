import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from ragmint.qa_generator import QADataGenerator


@pytest.fixture
def tmp_docs(tmp_path):
    """Create temporary docs directory with small text files."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "doc1.txt").write_text("Cisco routers provide secure networking.")
    (docs_dir / "doc2.txt").write_text("AI models can generate question-answer datasets.")
    return docs_dir


@pytest.fixture
def generator(tmp_docs, tmp_path):
    """Initialize QADataGenerator with fake keys and temp paths."""
    gen = QADataGenerator(
        docs_path=str(tmp_docs),
        output_path=str(tmp_path / "validation_qa.json"),
        batch_size=2,
    )
    gen.backend = "gemini"
    gen.llm = MagicMock()  # prevent real API call
    return gen


def test_read_corpus(generator):
    docs = generator.read_corpus()
    assert len(docs) == 2
    assert all("filename" in d and "text" in d for d in docs)


def test_determine_question_count_varies(generator):
    short = "short text"
    long = "word " * 2500
    q_short = generator.determine_question_count(short)
    q_long = generator.determine_question_count(long)
    assert generator.min_q <= q_short <= generator.max_q
    assert generator.min_q <= q_long <= generator.max_q
    assert q_long >= q_short  # longer text → more questions


@patch("ragmint.qa_generator.SentenceTransformer")
@patch("ragmint.qa_generator.KMeans")
def test_topic_factor_fallback(mock_kmeans, mock_st, generator):
    """Ensure topic clustering fallback works if embeddings or clustering fail."""
    mock_st.return_value.encode.side_effect = Exception("Embedding failed")
    result = generator.determine_question_count("This is a longer text with several sentences. " * 10)
    assert isinstance(result, int)
    assert generator.min_q <= result <= generator.max_q


def test_generate_qa_for_batch_gemini(generator):
    """Test LLM batch generation with mocked Gemini output."""
    fake_response = MagicMock()
    fake_response.text = json.dumps([
        {"query": "What is networking?", "expected_answer": "Connecting systems."}
    ])
    generator.llm.generate_content.return_value = fake_response

    batch = [{"filename": "doc.txt", "text": "Networking basics"}]
    result = generator.generate_qa_for_batch(batch)
    assert isinstance(result, list)
    assert result[0]["query"].startswith("What")


def test_generate_qa_for_batch_claude(generator):
    """Test LLM batch generation with mocked Claude output."""
    generator.backend = "claude"
    generator.llm.messages.create.return_value = MagicMock(
        content=[MagicMock(text=json.dumps([
            {"query": "What is AI?", "expected_answer": "Artificial Intelligence."}
        ]))]
    )
    batch = [{"filename": "doc.txt", "text": "AI models generate QAs."}]
    result = generator.generate_qa_for_batch(batch)
    assert len(result) == 1
    assert "expected_answer" in result[0]


@patch.object(QADataGenerator, "generate_qa_for_batch", return_value=[{"query": "Q?", "expected_answer": "A"}])
def test_full_generate_pipeline(mock_batch, generator):
    """Simulate entire generate() workflow including file save."""
    generator.generate()
    out_path = Path(generator.output_path)
    assert out_path.exists()
    data = json.loads(out_path.read_text())
    assert isinstance(data, list)
    assert all("query" in qa for qa in data)
