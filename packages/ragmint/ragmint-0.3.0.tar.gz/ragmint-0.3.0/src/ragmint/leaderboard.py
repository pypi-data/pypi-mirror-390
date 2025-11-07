import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client

class Leaderboard:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        self.client = None
        if url and key:
            self.client = create_client(url, key)
        elif not storage_path:
            raise EnvironmentError("Set SUPABASE_URL/SUPABASE_KEY or pass storage_path")

    def upload(self, run_id: str, config: Dict[str, Any], score: float):
        data = {
            "run_id": run_id,
            "config": config,
            "score": score,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if self.client:
            return self.client.table("experiments").insert(data).execute()
        else:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(data) + "\n")
            return data

    def top_results(self, limit: int = 10):
        if self.client:
            return (
                self.client.table("experiments")
                .select("*")
                .order("score", desc=True)
                .limit(limit)
                .execute()
            )
        else:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f]
            return sorted(lines, key=lambda x: x["score"], reverse=True)[:limit]
