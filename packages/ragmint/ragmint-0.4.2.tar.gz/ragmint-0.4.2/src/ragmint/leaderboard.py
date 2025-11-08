import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class Leaderboard:
    def __init__(self, storage_path: Optional[str] = "leaderboard.jsonl"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path) or ".", exist_ok=True)

        if not os.path.exists(self.storage_path):
            open(self.storage_path, "w", encoding="utf-8").close()

    def upload(
        self,
        run_id: str,
        best_config: Dict[str, Any],
        best_score: float,
        all_results: List[Dict[str, Any]],
        documents: List[str],
        model: str,
        corpus_stats: Optional[Dict[str, Any]] = None,
    ):
        """Persist a full experiment run to local leaderboard."""
        data = {
            "run_id": run_id,
            "timestamp": datetime.utcnow().isoformat(),
            "best_config": best_config,
            "best_score": best_score,
            "all_results": all_results,
            "documents": [os.path.basename(d) for d in documents],
            "model": model,
            "corpus_stats": corpus_stats or {},
        }

        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        return data

    def all_results(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.storage_path):
            return []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def top_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return top experiments by score."""
        results = self.all_results()
        return sorted(results, key=lambda x: x.get("best_score", 0.0), reverse=True)[:limit]
