"""
RAGMint Dashboard
-----------------
Gradio UI for AutoRAG / RAGMint:
- Upload corpus files
- Run recommend() (autotuner quick suggestion)
- Run full optimize() using grid/random/bayesian
- View leaderboard entries (local JSONL)
- Request LLM explanation for the best run
- Simple analytics: score histogram, latency summary, runs over time

Usage:
    pip install gradio pandas matplotlib
    export ANTHROPIC_API_KEY=...
    export GOOGLE_API_KEY=...
    python app.py
"""

import os
import json
import time
from typing import List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr

from ragmint.autotuner import AutoRAGTuner
from ragmint.tuner import RAGMint
from ragmint.leaderboard import Leaderboard
from ragmint.explainer import explain_results


# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
DATA_DIR = "data/docs"
LEADERBOARD_PATH = "data/leaderboard.jsonl"
LOGO_PATH = "assets/img/ragmint-banner.png"

BG_COLOR = "#F7F4ED"       # soft beige background
PRIMARY_GREEN = "#1D5C39"  # brand green

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LEADERBOARD_PATH) or ".", exist_ok=True)
leaderboard = Leaderboard(storage_path=LEADERBOARD_PATH)


# ----------------------------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------------------------
def save_uploaded_files(files) -> List[str]:
    saved = []
    for f in files:
        path = os.path.join(DATA_DIR, f.name)
        with open(path, "wb") as out:
            out.write(f.read())
        saved.append(path)
    return saved


def read_leaderboard_df():
    if not os.path.exists(LEADERBOARD_PATH) or os.path.getsize(LEADERBOARD_PATH) == 0:
        return pd.DataFrame()
    return pd.read_json(LEADERBOARD_PATH, lines=True)


def plot_score_histogram(results: List[Dict[str, Any]]):
    if not results:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No results yet", ha="center")
        return fig
    scores = [r.get("faithfulness", r.get("score", 0)) for r in results]
    fig, ax = plt.subplots()
    ax.hist(scores, bins=min(10, max(1, len(scores))), edgecolor="black", color=PRIMARY_GREEN)
    ax.set_title("Score Distribution", color=PRIMARY_GREEN)
    ax.set_xlabel("Score", color=PRIMARY_GREEN)
    ax.set_ylabel("Count", color=PRIMARY_GREEN)
    return fig


# ----------------------------------------------------------------------
# ACTION HANDLERS
# ----------------------------------------------------------------------
def handle_upload(files):
    if not files:
        return "No files provided."
    saved = save_uploaded_files(files)
    return f"✅ Saved {len(saved)} files to {DATA_DIR}."


def do_recommend(embedding_model: str = None, num_chunk_pairs: int = 5):
    tuner = AutoRAGTuner(docs_path=DATA_DIR)
    rec = tuner.recommend(embedding_model=embedding_model, num_chunk_pairs=num_chunk_pairs)
    summary = {
        "retriever": rec["retriever"],
        "embedding": rec["embedding_model"],
        "strategy": rec["strategy"],
        "chunk_candidates_count": len(rec["chunk_candidates"]),
    }
    return json.dumps(rec, indent=2), json.dumps(summary, indent=2)


def do_optimize(search_type: str = "random", trials: int = 5, embedding_model: str = None):
    tuner = AutoRAGTuner(docs_path=DATA_DIR)
    rec = tuner.recommend(embedding_model=embedding_model, num_chunk_pairs=3)
    chunk_candidates = tuner.suggest_chunk_sizes(model_name=rec["embedding_model"], num_pairs=None, step=20)
    chunk_sizes = sorted({c for c, _ in chunk_candidates})
    overlaps = sorted({o for _, o in chunk_candidates})

    rag = RAGMint(
        docs_path=DATA_DIR,
        retrievers=[rec["retriever"]],
        embeddings=[rec["embedding_model"]],
        rerankers=["mmr"],
        chunk_sizes=chunk_sizes,
        overlaps=overlaps,
        strategies=[rec["strategy"]],
    )

    start_time = time.time()
    best, results = rag.optimize(validation_set=None, metric="faithfulness", search_type=search_type, trials=trials)
    elapsed = time.time() - start_time

    run_id = f"run_{int(time.time())}"
    corpus_stats = {
        "num_docs": len(rag.documents),
        "avg_len": sum(len(d.split()) for d in rag.documents) / max(1, len(rag.documents)),
        "corpus_size": sum(len(d) for d in rag.documents),
    }

    leaderboard.upload(
        run_id=run_id,
        best_config=best,
        best_score=best.get("faithfulness", best.get("score", 0.0)),
        all_results=results,
        documents=os.listdir(DATA_DIR),
        model=best.get("embedding_model", rec["embedding_model"]),
        corpus_stats=corpus_stats,
    )

    fig = plot_score_histogram(results)
    return json.dumps(best, indent=2), f"✅ Completed in {elapsed:.1f}s — {len(results)} trials", fig


def show_leaderboard_table():
    df = read_leaderboard_df()
    if df.empty:
        return "No runs yet.", ""
    table = df[["run_id", "timestamp", "best_score", "model", "best_config"]].sort_values(
        "best_score", ascending=False
    )
    return table, df.to_json(orient="records", indent=2)


def do_explain(run_id: str, llm_model: str = "gemini-2.5-flash-lite"):
    entry = leaderboard.all_results()
    matched = [r for r in entry if r["run_id"] == run_id]
    if not matched:
        return f"Run {run_id} not found."
    record = matched[0]
    best = record["best_config"]
    all_results = record["all_results"]
    corpus_stats = record.get("corpus_stats", {})
    return explain_results(best, all_results, corpus_stats=corpus_stats, model=llm_model)


def analytics_overview():
    df = read_leaderboard_df()
    if df.empty:
        return "No data yet."
    top_score = df["best_score"].max()
    runs = len(df)
    latencies = []
    for row in df["all_results"]:
        for r in row:
            if isinstance(r, dict) and "latency" in r:
                latencies.append(r["latency"])
    avg_latency = sum(latencies) / len(latencies) if latencies else None
    summary = {
        "num_runs": runs,
        "top_score": float(top_score),
        "avg_trial_latency": float(avg_latency) if avg_latency else None,
    }
    return json.dumps(summary, indent=2)


# ----------------------------------------------------------------------
# CUSTOM STYLING
# ----------------------------------------------------------------------
custom_css = f"""
body {{
    background-color: {BG_COLOR};
    font-family: 'Inter', sans-serif;
}}

#logo {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    padding: 1rem 1.5rem;
    background-color: {BG_COLOR};
}}

#logo img {{
    height: 80px;
    margin-right: 15px;
}}

h1, h2, h3, label {{
    color: {PRIMARY_GREEN} !important;
}}

button {{
    background-color: {PRIMARY_GREEN} !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}}

button:hover {{
    opacity: 0.9;
}}

textarea, input {{
    border-radius: 10px !important;
    border-color: #ddd !important;
}}

.gr-box {{
    background: white;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    padding: 1rem;
}}
"""


# ----------------------------------------------------------------------
# BUILD GRADIO APP
# ----------------------------------------------------------------------
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    with gr.Row(elem_id="logo"):
        gr.Image(value=LOGO_PATH, show_label=False, interactive=False)
        gr.Markdown(f"<h1 style='color:{PRIMARY_GREEN}; font-size:2.5em;'>RAGMint Dashboard</h1>")

    gr.Markdown(
        f"<p style='font-size:1.1em; color:{PRIMARY_GREEN}; margin-left:20px;'>"
        "Auto-tune your RAG pipeline, benchmark performance, visualize results, and get AI-driven explanations."
        "</p>"
    )

    with gr.Tab("📂 Corpus Upload"):
        uploader = gr.File(label="Upload corpus files", file_count="multiple")
        upload_btn = gr.Button("Save files")
        upload_status = gr.Textbox(label="Status", interactive=False)
        upload_btn.click(fn=handle_upload, inputs=[uploader], outputs=[upload_status])

    with gr.Tab("🎯 Autotuner"):
        embed_model = gr.Textbox(value="sentence-transformers/all-MiniLM-L6-v2", label="Embedding model")
        num_pairs = gr.Number(value=5, label="Chunk candidates")
        rec_btn = gr.Button("Recommend setup")
        rec_json = gr.Textbox(label="Recommendation (JSON)", interactive=False)
        rec_summary = gr.Textbox(label="Summary", interactive=False)
        rec_btn.click(fn=do_recommend, inputs=[embed_model, num_pairs], outputs=[rec_json, rec_summary])

    with gr.Tab("⚙️ Optimization"):
        search_type = gr.Dropdown(choices=["random", "grid", "bayesian"], value="random", label="Search type")
        trials = gr.Slider(minimum=1, maximum=50, step=1, value=5, label="Trials")
        optimize_btn = gr.Button("Run Optimize")
        best_json = gr.Textbox(label="Best config", interactive=False)
        optimize_status = gr.Textbox(label="Status", interactive=False)
        score_plot = gr.Plot(label="Score Distribution")
        optimize_btn.click(fn=do_optimize, inputs=[search_type, trials, embed_model], outputs=[best_json, optimize_status, score_plot])

    with gr.Tab("🏆 Leaderboard"):
        show_btn = gr.Button("Refresh leaderboard")
        lb_table = gr.Dataframe(label="Leaderboard", interactive=False)
        lb_json = gr.Textbox(label="Raw JSON", interactive=False)
        show_btn.click(fn=show_leaderboard_table, outputs=[lb_table, lb_json])

    with gr.Tab("💬 Explain"):
        run_id_input = gr.Textbox(label="Run ID", placeholder="run_12345")
        llm_model_input = gr.Textbox(value="gemini-2.5-flash-lite", label="LLM Model")
        explain_btn = gr.Button("Explain Best Run")
        explanation_out = gr.Textbox(label="Explanation", interactive=False, lines=10)
        explain_btn.click(fn=do_explain, inputs=[run_id_input, llm_model_input], outputs=[explanation_out])

    with gr.Tab("📊 Analytics"):
        analytics_btn = gr.Button("Refresh Analytics")
        analytics_out = gr.Textbox(label="Summary", interactive=False)
        analytics_btn.click(fn=analytics_overview, outputs=[analytics_out])

    gr.Markdown(
        f"<center><p style='color:{PRIMARY_GREEN}; font-size:0.9em;'>"
        "Built with ❤️ using RAGMint · © 2025 andyolivers.com</p></center>"
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
