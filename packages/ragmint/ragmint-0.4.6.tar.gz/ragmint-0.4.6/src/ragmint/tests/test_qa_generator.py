import os
import json
import tempfile
from pathlib import Path
import pytest

from ragmint.qa_generator import generate_validation_qa


class DummyLLM:
    """Mock LLM that returns predictable JSON output."""
    def generate_content(self, prompt):
        class DummyResponse:
            text = '[{"query": "What is X?", "expected_answer": "Y"}]'
        return DummyResponse()


@pytest.fixture
def dummy_docs(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for i in range(3):
        (docs_dir / f"doc_{i}.txt").write_text(f"This is test document number {i}. It contains some content.")
    return docs_dir


@pytest.fixture
def output_path(tmp_path):
    return tmp_path / "validation_qa.json"


def test_generate_validation_qa(monkeypatch, dummy_docs, output_path):
    """Ensure QA generator runs end-to-end with mocked LLM."""
    # --- Mock LLM setup ---
    from sentence_transformers import SentenceTransformer
    monkeypatch.setattr("ragmint.qa_generator.setup_llm", lambda *_: (DummyLLM(), "gemini"))
    monkeypatch.setattr(SentenceTransformer, "encode", lambda self, x, normalize_embeddings=True: [[0.1] * 3] * len(x))

    # --- Run function ---
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
    assert all("query" in d and "expected_answer" in d for d in data), "Each entry must have query and answer"
    assert len(data) > 0, "At least one QA pair should be generated"


def test_handles_empty_folder(monkeypatch, tmp_path):
    """Ensure no crash when docs folder is empty."""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    output_file = tmp_path / "qa.json"

    monkeypatch.setattr("ragmint.qa_generator.setup_llm", lambda *_: (DummyLLM(), "gemini"))

    generate_validation_qa(docs_path=empty_dir, output_path=output_file, sleep_between_batches=0)
    data = json.loads(output_file.read_text())
    assert data == [], "Empty folder should produce empty QA list"
