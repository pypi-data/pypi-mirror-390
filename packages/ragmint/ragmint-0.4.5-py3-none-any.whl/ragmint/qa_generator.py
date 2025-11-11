"""
Batched Validation QA Generator for Ragmint

Generates a JSON QA dataset from a large corpus using an LLM.
Processes documents in batches to avoid token limits and API errors.
Now uses topic-aware dynamic question count estimation.
"""

import os
import json
import math
import time
import argparse
from pathlib import Path
from dotenv import load_dotenv

# --- New imports for topic detection ---
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer


class QADataGenerator:
    def __init__(
        self,
        docs_path="data/docs",
        output_path="experiments/validation_qa.json",
        llm_model="gemini-2.5-flash-lite",
        batch_size=5,
        sleep_between_batches=2,
        base_density=0.005,
        min_q=3,
        max_q=25,
    ):
        load_dotenv()
        self.docs_path = docs_path
        self.output_path = output_path
        self.llm_model = llm_model
        self.batch_size = batch_size
        self.sleep = sleep_between_batches
        self.base_density = base_density
        self.min_q = min_q
        self.max_q = max_q
        self.all_qa = []

        # --- Load embedding model once for topic awareness ---
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

        # --- LLM setup ---
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if self.google_key:
            import google.generativeai as genai
            genai.configure(api_key=self.google_key)
            self.llm = genai.GenerativeModel(self.llm_model)
            self.backend = "gemini"
        elif self.anthropic_key:
            from anthropic import Anthropic
            self.llm = Anthropic(api_key=self.anthropic_key)
            self.backend = "claude"
        else:
            raise ValueError("Set ANTHROPIC_API_KEY or GOOGLE_API_KEY in .env")

    # ---------- Utility Methods ----------

    def read_corpus(self):
        """Load all text documents from a folder"""
        docs = []
        for file in Path(self.docs_path).glob("**/*.txt"):
            with open(file, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    docs.append({"filename": file.name, "text": text})
        return docs

    def determine_question_count(self, text):
        """
        Determine number of questions based on:
        - Text length (logarithmic scaling)
        - Topic diversity (semantic clusters)
        """
        sentences = [s.strip() for s in text.split('.') if len(s.strip().split()) > 3]
        word_count = len(text.split())

        if word_count == 0:
            return self.min_q

        # Base factor by length (log growth)
        base_q = math.log1p(word_count / 150)

        # Topic factor by clustering
        n_sent = len(sentences)
        if n_sent < 5:
            topic_factor = 1.0
        else:
            try:
                emb = self.embedder.encode(sentences, normalize_embeddings=True)
                n_clusters = min(max(2, n_sent // 10), 8)
                km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
                labels = km.fit_predict(emb)
                topic_factor = len(set(labels)) / n_clusters
            except Exception as e:
                print(f"[WARN] Clustering failed ({type(e).__name__}): {e}")
                topic_factor = 1.0

        # Combined score
        score = base_q * (1 + 0.8 * topic_factor)
        question_count = round(self.min_q + score)

        # Clip to range
        return int(max(self.min_q, min(question_count, self.max_q)))

    def generate_qa_for_batch(self, batch):
        """Send one LLM call for a batch of documents"""
        prompt_texts = []
        for doc in batch:
            n_questions = self.determine_question_count(doc["text"])
            prompt_texts.append(
                f"Document: {doc['text'][:1000]}\n"
                f"Generate {n_questions} factual question-answer pairs in JSON format."
            )

        prompt = "\n\n".join(prompt_texts)
        prompt += (
            "\n\nReturn a single JSON array of objects like:\n"
            '[{"query": "string", "expected_answer": "string"}]'
        )

        try:
            if self.backend == "gemini":
                response = self.llm.generate_content(prompt)
                # Gemini responses may return .text or .candidates[0].content.parts[0].text
                text_out = getattr(response, "text", None)
                if not text_out and hasattr(response, "candidates"):
                    text_out = response.candidates[0].content.parts[0].text
                return json.loads(text_out)
            elif self.backend == "claude":
                response = self.llm.messages.create(
                    model="claude-3-opus-20240229",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000,
                )
                return json.loads(response.content[0].text)
        except Exception as e:
            print(f"[WARN] Failed to parse batch: {e}")
            return []

    # ---------- Main Process ----------

    def generate(self):
        corpus = self.read_corpus()
        print(f"[INFO] Loaded {len(corpus)} documents from {self.docs_path}")
        print(f"[INFO] Using density {self.base_density} ({self.min_q}-{self.max_q} Qs per doc)")

        for i in range(0, len(corpus), self.batch_size):
            batch = corpus[i : i + self.batch_size]
            try:
                batch_qa = self.generate_qa_for_batch(batch)
                self.all_qa.extend(batch_qa)
                print(
                    f"[INFO] Processed batch {i//self.batch_size + 1} "
                    f"({len(batch)} docs, total QAs: {len(self.all_qa)})"
                )
            except Exception as e:
                print(f"[WARN] Batch {i//self.batch_size + 1} failed: {e}")
            time.sleep(self.sleep)

        self.save_json()

    def save_json(self):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(self.all_qa, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Saved {len(self.all_qa)} QAs → {self.output_path}")


# ---------- CLI entry point ----------

def main():
    parser = argparse.ArgumentParser(description="Generate validation QA dataset for Ragmint.")
    parser.add_argument("--density", type=float, default=0.005, help="QAs per word (e.g., 0.005 = 5 per 1000 words)")
    args = parser.parse_args()

    generator = QADataGenerator(base_density=args.density)
    generator.generate()


if __name__ == "__main__":
    main()
