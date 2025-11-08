import os
import json
import hashlib
import pickle
from typing import Any


class Cache:
    """
    Simple file-based cache for embeddings or retrievals.
    """

    def __init__(self, cache_dir: str = ".ragmint_cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _hash_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def exists(self, key: str) -> bool:
        return os.path.exists(os.path.join(self.cache_dir, self._hash_key(key)))

    def get(self, key: str) -> Any:
        path = os.path.join(self.cache_dir, self._hash_key(key))
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return pickle.load(f)

    def set(self, key: str, value: Any):
        path = os.path.join(self.cache_dir, self._hash_key(key))
        with open(path, "wb") as f:
            pickle.dump(value, f)

    def clear(self):
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))
