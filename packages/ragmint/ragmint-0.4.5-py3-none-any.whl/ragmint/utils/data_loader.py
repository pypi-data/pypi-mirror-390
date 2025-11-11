import json
import csv
from typing import List, Dict
from pathlib import Path
import os

try:
    from datasets import load_dataset
except ImportError:
    load_dataset = None  # optional dependency

DEFAULT_VALIDATION_PATH = Path(__file__).parent.parent / "experiments" / "validation_qa.json"


def load_json(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_csv(path: str) -> List[Dict]:
    with open(path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)


def save_json(path: str, data: Dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_validation_set(path: str | None = None) -> List[Dict]:
    """
    Loads a validation dataset (QA pairs) from:
    - Built-in default JSON file
    - User-provided JSON or CSV
    - Hugging Face dataset by name
    """
    # Default behavior
    if path is None or path == "default":
        if not DEFAULT_VALIDATION_PATH.exists():
            raise FileNotFoundError(f"Default validation set not found at {DEFAULT_VALIDATION_PATH}")
        return load_json(DEFAULT_VALIDATION_PATH)

    # Hugging Face dataset
    if not os.path.exists(path) and load_dataset:
        try:
            dataset = load_dataset(path, split="validation")
            data = [
                {"question": q, "answer": a}
                for q, a in zip(dataset["question"], dataset["answers"])
            ]
            return data
        except Exception:
            pass  # fall through to file loading

    # Local file
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Validation file not found: {path}")

    if p.suffix.lower() == ".json":
        return load_json(path)
    elif p.suffix.lower() in [".csv", ".tsv"]:
        return load_csv(path)
    else:
        raise ValueError("Unsupported validation set format. Use JSON, CSV, or a Hugging Face dataset name.")