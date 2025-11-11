from pathlib import Path
from ragmint.tuner import RAGMint

def main():
    # Dynamically resolve the path to the installed ragmint package
    base_dir = Path(__file__).resolve().parent

    docs_path = base_dir / "experiments" / "corpus"
    validation_file = base_dir / "experiments" / "validation_qa.json"

    rag = RAGMint(
        docs_path=str(docs_path),
        retrievers=["faiss"],
        embeddings=["openai/text-embedding-3-small"],
        rerankers=["mmr"],
    )

    best, results = rag.optimize(
        validation_set=str(validation_file),
        metric="faithfulness",
        search_type="bayesian",
        trials=10,
    )

    print("Best config found:\n", best)

if __name__ == "__main__":
    main()
