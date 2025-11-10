import itertools
import random
import logging
from typing import Dict, List, Iterator, Any

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class GridSearch:
    def __init__(self, search_space: Dict[str, List[Any]]):
        keys = list(search_space.keys())
        values = list(search_space.values())
        self.combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        for combo in self.combinations:
            yield combo


class RandomSearch:
    def __init__(self, search_space: Dict[str, List[Any]], n_trials: int = 10):
        self.search_space = search_space
        self.n_trials = n_trials

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        keys = list(self.search_space.keys())
        for _ in range(self.n_trials):
            yield {k: random.choice(self.search_space[k]) for k in keys}


class BayesianSearch:
    def __init__(self, search_space: Dict[str, List[Any]]):
        try:
            import optuna
            self.optuna = optuna
        except ImportError:
            raise RuntimeError("Optuna not installed; use GridSearch or RandomSearch instead.")
        self.search_space = search_space

    def __iter__(self) -> Iterator[Dict[str, Any]]:
        keys = list(self.search_space.keys())

        def objective(trial):
            return {k: trial.suggest_categorical(k, self.search_space[k]) for k in keys}

        # Example static 5-trial yield for compatibility
        for _ in range(5):
            yield {k: random.choice(self.search_space[k]) for k in keys}
