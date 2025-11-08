from typing import List
import numpy as np
from difflib import SequenceMatcher


def bleu_score(reference: str, candidate: str) -> float:
    """
    Simple BLEU-like precision approximation.
    """
    ref_tokens = reference.split()
    cand_tokens = candidate.split()
    if not cand_tokens:
        return 0.0

    matches = sum(1 for token in cand_tokens if token in ref_tokens)
    return matches / len(cand_tokens)


def rouge_l(reference: str, candidate: str) -> float:
    """
    Approximation of ROUGE-L using sequence matcher ratio.
    """
    return SequenceMatcher(None, reference, candidate).ratio()


def mean_score(scores: List[float]) -> float:
    return float(np.mean(scores)) if scores else 0.0
