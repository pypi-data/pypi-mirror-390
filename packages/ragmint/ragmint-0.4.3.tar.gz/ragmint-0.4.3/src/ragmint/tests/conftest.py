# src/ragmint/tests/conftest.py
import os
from dotenv import load_dotenv
import pytest

# Load .env from project root
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

def pytest_configure(config):
    """Print which keys are loaded (debug)."""
    google = os.getenv("GEMINI_API_KEY")
    anthropic = os.getenv("ANTHROPIC_API_KEY")
    if google:
        print("✅ GOOGLE_API_KEY loaded")
    if anthropic:
        print("✅ ANTHROPIC_API_KEY loaded")
