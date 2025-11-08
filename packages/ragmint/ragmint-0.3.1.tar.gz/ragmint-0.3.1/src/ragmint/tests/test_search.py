from ragmint.optimization.search import GridSearch, RandomSearch


def test_grid_search_iterates():
    space = {"retriever": ["faiss"], "embedding_model": ["openai"], "reranker": ["mmr"]}
    search = GridSearch(space)
    combos = list(search)
    assert len(combos) == 1
    assert "retriever" in combos[0]


def test_random_search_n_trials():
    space = {"retriever": ["faiss", "bm25"], "embedding_model": ["openai", "st"], "reranker": ["mmr"]}
    search = RandomSearch(space, n_trials=5)
    combos = list(search)
    assert len(combos) == 5
    assert all("retriever" in c for c in combos)
