"""
Interpretability Layer
----------------------
Uses Gemini or Anthropic Claude to explain why a particular RAG configuration
performed best, considering both optimizer results and corpus characteristics.
"""

import os
import json
from dotenv import load_dotenv

# Load .env if available
load_dotenv()

def explain_results(best_result: dict, all_results: list, corpus_stats: dict = None,
                    model: str = "gemini-2.5-flash-lite") -> str:
    """
    Generate a detailed natural-language explanation for RAG optimization results.

    Parameters:
      - best_result: dict containing the best configuration and metrics.
      - all_results: list of all trial results with metrics and configs.
      - corpus_stats: optional dict with corpus info (size, avg_len, num_docs).
      - model: LLM model name (Gemini or Claude).

    Returns:
      A natural-language explanation string.
    """

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")

    # Build dynamic context
    corpus_info = json.dumps(corpus_stats or {}, indent=2)
    best_json = json.dumps(best_result, indent=2)
    all_json = json.dumps(list(all_results)[:10], indent=2) #cap for safety

    prompt = f"""
    You are an expert AI researcher specializing in Retrieval-Augmented Generation (RAG) optimization.

    A RAG auto-tuner was run on a corpus with these characteristics:
    {corpus_info}

    The tuner evaluated multiple configurations and metrics. Below are:
    - The BEST configuration:
    {best_json}

    - A sample of ALL evaluated configurations:
    {all_json}

    Please:
    1. Explain WHY this best configuration likely performs better than others.
    2. Highlight trade-offs between accuracy, latency, and resource usage.
    3. Suggest potential improvements (different chunking, embedding, retriever, etc.).
    4. Provide a concise summary of which setup you recommend for this corpus.
    Keep it structured, under 300 words, and easy to read.
    """

    # --- 1️⃣ Anthropic Claude first ---
    if anthropic_key:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            return f"[Claude unavailable] {e}"

    # --- 2️⃣ Gemini fallback ---
    elif google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[Gemini unavailable] {e}"

    # --- 3️⃣ Fallback message ---
    else:
        return (
            "[No LLM available] Please set ANTHROPIC_API_KEY or GOOGLE_API_KEY "
            "to enable interpretability via Claude or Gemini."
        )
