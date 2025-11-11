"""
Batched Validation QA Generator for Ragmint (Functional Version)

Generates a JSON QA dataset from a large corpus using an LLM.
Processes documents in batches to avoid token limits and API errors.
Uses topic-aware dynamic question count estimation.
"""

import os
import re
import json
import math
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer

# ---------- Utility functions ----------

def extract_json_from_markdown(text: str):
    """Extract JSON from a markdown-style code block."""
    if text is None:
        raise ValueError("No text provided to parse from LLM response.")
    match = re.search(r"```(?:json)?\s*(\[\s*[\s\S]*?\s*\])\s*```", text, re.MULTILINE)
    if match:
        json_str = match.group(1)
        return json.loads(json_str)
    else:
        cleaned = re.sub(r"^```\w*\n", "", text).strip()
        cleaned = re.sub(r"\n```$", "", cleaned).strip()
        return json.loads(cleaned)


def read_corpus(docs_path: str):
    """Load all text documents from a folder."""
    docs = []
    for file in Path(docs_path).glob("**/*.txt"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if text:
                docs.append({"filename": file.name, "text": text})
    return docs


def determine_question_count(text: str, embedder, min_q=3, max_q=25):
    """Estimate number of questions dynamically based on text length and topic diversity."""
    sentences = [s.strip() for s in text.split('.') if len(s.strip().split()) > 3]
    word_count = len(text.split())

    if word_count == 0:
        return min_q

    base_q = math.log1p(word_count / 150)

    # Topic diversity via clustering
    n_sent = len(sentences)
    if n_sent < 5:
        topic_factor = 1.0
    else:
        try:
            emb = embedder.encode(sentences, normalize_embeddings=True)
            n_clusters = min(max(2, n_sent // 10), 8)
            km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
            labels = km.fit_predict(emb)
            topic_factor = len(set(labels)) / n_clusters
        except Exception as e:
            print(f"[WARN] Clustering failed ({type(e).__name__}): {e}")
            topic_factor = 1.0

    score = base_q * (1 + 0.8 * topic_factor)
    question_count = round(min_q + score)
    return int(max(min_q, min(question_count, max_q)))


def setup_llm(llm_model="gemini-2.5-flash-lite", google_key: str | None = None, anthropic_key: str | None = None):
    """
    Configure Gemini or Claude based on available environment keys.

    - Always calls load_dotenv() so .env is read at call time (mirrors interpretability module).
    - Explicit keys passed here take precedence over environment variables.
    """
    # ensure .env is read now (so callers that import module earlier still pick it up)
    load_dotenv(override=False)

    google_key = google_key or os.getenv("GOOGLE_API_KEY")
    anthropic_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")

    if google_key:
        import google.generativeai as genai
        genai.configure(api_key=google_key)
        llm = genai.GenerativeModel(llm_model)
        return llm, "gemini"

    elif anthropic_key:
        from anthropic import Anthropic
        llm = Anthropic(api_key=anthropic_key)
        return llm, "claude"

    else:
        raise ValueError("Set ANTHROPIC_API_KEY or GOOGLE_API_KEY in your environment or pass keys explicitly.")


def generate_qa_for_batch(batch, llm, backend, embedder, min_q=3, max_q=25):
    """Send one LLM call for a batch of documents."""
    if backend is None or llm is None:
        # No LLM configured — return empty result for this batch.
        return []

    prompt_texts = []
    for doc in batch:
        n_questions = determine_question_count(doc["text"], embedder, min_q, max_q)
        prompt_texts.append(
            f"Document: {doc['text'][:1000]}\n"
            f"Generate {n_questions} factual question-answer pairs in JSON format."
        )

    prompt = "\n\n".join(prompt_texts)
    prompt += "\n\nReturn a single JSON array of objects like:\n" \
              '[{"query": "string", "expected_answer": "string"}]'

    try:
        if backend == "gemini":
            response = llm.generate_content(prompt)
            text_out = getattr(response, "text", None)
            if not text_out and hasattr(response, "candidates"):
                # handle alternative Gemini response shape
                text_out = response.candidates[0].content.parts[0].text
            return extract_json_from_markdown(text_out)

        elif backend == "claude":
            response = llm.messages.create(
                model="claude-3-opus-20240229",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
            )
            # anthopic response shape
            text_out = getattr(response.content[0], "text", None) or response.content[0]
            return extract_json_from_markdown(text_out)

    except Exception as e:
        print(f"[WARN] Failed to parse batch: {e}")
        return []


def save_json(output_path, data):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[INFO] Saved {len(data)} QAs → {output_path}")


def generate_validation_qa(
    docs_path="data/docs",
    output_path="experiments/validation_qa.json",
    llm_model="gemini-2.5-flash-lite",
    batch_size=5,
    sleep_between_batches=2,
    min_q=3,
    max_q=25,
    google_key: str | None = None,
    anthropic_key: str | None = None,
    skip_llm: bool = False,
):
    """
    Main pipeline to generate QAs.

    - pass google_key / anthropic_key to avoid relying on .env
    - set skip_llm=True to run without LLM (useful in tests/CI)
    """
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    if skip_llm:
        llm = None
        backend = None
        print("[INFO] skip_llm=True → no LLM will be initialized; output will be empty.")
    else:
        llm, backend = setup_llm(llm_model=llm_model, google_key=google_key, anthropic_key=anthropic_key)

    all_qa = []
    corpus = read_corpus(docs_path)
    print(f"[INFO] Loaded {len(corpus)} documents from {docs_path}")

    for i in range(0, len(corpus), batch_size):
        batch = corpus[i: i + batch_size]
        batch_qa = generate_qa_for_batch(batch, llm, backend, embedder, min_q, max_q)
        all_qa.extend(batch_qa)
        print(f"[INFO] Batch {i // batch_size + 1}: {len(batch_qa)} QAs (Total: {len(all_qa)})")
        time.sleep(sleep_between_batches)

    save_json(output_path, all_qa)


# ---------- CLI entry point ----------

def main():
    parser = argparse.ArgumentParser(description="Generate validation QA dataset for Ragmint.")
    parser.add_argument("--docs_path", type=str, default="data/docs")
    parser.add_argument("--output", type=str, default="experiments/validation_qa.json")
    parser.add_argument("--batch_size", type=int, default=5)
    parser.add_argument("--sleep", type=int, default=2)
    parser.add_argument("--min_q", type=int, default=3)
    parser.add_argument("--max_q", type=int, default=25)
    parser.add_argument("--skip_llm", action="store_true", help="Run without initializing an LLM (for tests)")
    args = parser.parse_args()

    generate_validation_qa(
        docs_path=args.docs_path,
        output_path=args.output,
        llm_model="gemini-2.5-flash-lite",
        batch_size=args.batch_size,
        sleep_between_batches=args.sleep,
        min_q=args.min_q,
        max_q=args.max_q,
        skip_llm=args.skip_llm,
    )


if __name__ == "__main__":
    main()
