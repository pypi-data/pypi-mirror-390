import os
import json
import pytest
from pathlib import Path

from ragmint.qa_generator import generate_validation_qa


class DummyLLM:
    """Mock LLM that returns predictable JSON output."""
    def generate_content(self, prompt):
        class DummyResponse:
            text = '[{"query": "What is X?", "expected_answer": "Y"}]'
        return DummyResponse()


@pytest.fixture
def dummy_docs(tmp_path):
    """Create a temporary folder with dummy text files."""
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for i in range(3):
        (docs_dir / f"doc_{i}.txt").write_text(
            f"This is test document number {i}. It contains some content."
        )
    return docs_dir


@pytest.fixture
def output_path(tmp_path):
    """Return a temporary path for output JSON file."""
    return tmp_path / "validation_qa.json"


def test_generate_validation_qa(monkeypatch, dummy_docs, output_path):
    """Ensure QA generator runs end-to-end with a mocked LLM backend."""
    from sentence_transformers import SentenceTransformer

    # --- Mock LLM and embeddings ---
    monkeypatch.setattr(
        "ragmint.qa_generator.setup_llm",
        lambda *_, **__: (DummyLLM(), "gemini")
    )
    monkeypatch.setattr(
        SentenceTransformer,
        "encode",
        lambda self, x, normalize_embeddings=True: [[0.1] * 3] * len(x)
    )

    # --- Run the QA generation ---
    generate_validation_qa(
        docs_path=dummy_docs,
        output_path=output_path,
        llm_model="gemini-2.5-flash-lite",
        batch_size=2,
        sleep_between_batches=0,
    )

    # --- Validate output ---
    assert output_path.exists(), "Output JSON file should be created"
    data = json.loads(output_path.read_text())
    assert isinstance(data, list), "Output must be a list"
    assert all("query" in d and "expected_answer" in d for d in data), \
        "Each entry must have 'query' and 'expected_answer'"
    assert len(data) > 0, "At least one QA pair should be generated"


def test_handles_empty_folder(monkeypatch, tmp_path):
    """Ensure no crash when docs folder is empty."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    output_file = tmp_path / "qa.json"

    # Mock setup_llm so it doesn't require an API key
    monkeypatch.setattr(
        "ragmint.qa_generator.setup_llm",
        lambda *_, **__: (DummyLLM(), "gemini")
    )

    # Run with empty docs directory
    generate_validation_qa(
        docs_path=empty_dir,
        output_path=output_file,
        sleep_between_batches=0,
    )

    assert output_file.exists(), "Output file should be created"
    data = json.loads(output_file.read_text())
    assert data == [], "Empty folder should produce an empty QA list"
