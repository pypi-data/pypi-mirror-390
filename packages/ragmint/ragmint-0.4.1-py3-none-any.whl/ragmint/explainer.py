"""
Interpretability Layer
----------------------
Uses Gemini or Anthropic Claude to explain why one RAG configuration
outperforms another. Falls back gracefully if no API key is provided.
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

def explain_results(results_a: dict, results_b: dict, model: str = "gemini-2.5-flash-lite") -> str:
    """
    Generate a natural-language explanation comparing two RAG experiment results.
    Priority:
      1. Anthropic Claude (if ANTHROPIC_API_KEY is set)
      2. Google Gemini (if GOOGLE_API_KEY is set)
      3. Fallback text message
    """
    prompt = f"""
    You are an AI evaluation expert.
    Compare these two RAG experiment results and explain why one performs better.
    Metrics A: {json.dumps(results_a, indent=2)}
    Metrics B: {json.dumps(results_b, indent=2)}
    Provide a concise, human-friendly explanation and practical improvement tips.
    """

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")  # fixed var name

    # 1️⃣ Try Anthropic Claude first
    if anthropic_key:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except Exception as e:
            return f"[Claude unavailable] {e}"

    # 2️⃣ Fallback to Google Gemini
    elif google_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=google_key)
            response = genai.GenerativeModel(model).generate_content(prompt)
            return response.text
        except Exception as e:
            return f"[Gemini unavailable] {e}"

    # 3️⃣ Fallback if neither key is available
    else:
        return (
            "[No LLM available] Please set ANTHROPIC_API_KEY or GOOGLE_API_KEY "
            "to enable interpretability via Claude or Gemini."
        )
