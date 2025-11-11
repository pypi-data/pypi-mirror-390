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

"""

import os
import json
import time
from typing import List, Dict, Any
import pandas as pd
import matplotlib.pyplot as plt
import gradio as gr
from dotenv import set_key, load_dotenv
from ragmint.autotuner import AutoRAGTuner
from ragmint.tuner import RAGMint
from ragmint.leaderboard import Leaderboard
from ragmint.explainer import explain_results
from matplotlib.ticker import MultipleLocator
import yaml

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
DATA_DIR = "data/docs"
LEADERBOARD_PATH = "data/leaderboard.jsonl"
LOGO_PATH = "src/ragmint/assets/img/ragmint_logo.png"
ENV_PATH = ".env"

BG_COLOR = "#F7F4ED"       # soft beige background
PRIMARY_GREEN = "#1D5C39"  # brand green

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LEADERBOARD_PATH) or ".", exist_ok=True)
leaderboard = Leaderboard(storage_path=LEADERBOARD_PATH)

load_dotenv(ENV_PATH)

# ----------------------------------------------------------------------
# UTILITY FUNCTIONS
# ----------------------------------------------------------------------
def save_uploaded_files(files):
    saved_files = []
    for f in files:
        # f is a gradio.files.NamedString
        src_path = f.name  # full path to the temp file
        filename = os.path.basename(src_path)  # extract just the name
        dest_path = os.path.join(DATA_DIR, filename)
        with open(src_path, "rb") as src, open(dest_path, "wb") as dst:
            dst.write(src.read())
        saved_files.append(filename)
    return saved_files

def handle_validation_upload(file):
    if not file:
        return "⚠️ Please select a file first."
    dest_path = os.path.join(DATA_DIR, "validation_qa.json")
    with open(file.name, "rb") as src, open(dest_path, "wb") as dst:
        dst.write(src.read())
    return "✅ Validation file saved as validation_qa.json"

# --- Validation toggle ---
def toggle_validation_inputs(choice):
    return (
        gr.update(visible=(choice == "Upload JSON")),
        gr.update(visible=(choice == "HuggingFace Dataset"), interactive=True),
        f"Selected: {choice}"
    )

# --- API key save function with type ---
def save_api_key(api_key: str, provider: str):
    if not api_key:
        return "⚠️ No API key provided."
    if provider == "Google":
        set_key(ENV_PATH, "GOOGLE_API_KEY", api_key)
    elif provider == "Anthropic":
        set_key(ENV_PATH, "ANTHROPIC_API_KEY", api_key)
    return f"✅ {provider} API key saved to .env."

def read_leaderboard_df():
    if not os.path.exists(LEADERBOARD_PATH) or os.path.getsize(LEADERBOARD_PATH) == 0:
        return pd.DataFrame()
    return pd.read_json(LEADERBOARD_PATH, lines=True)


def plot_score_scatter(results: List[Dict[str, Any]], best_index: int = None):
    if not results:
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "No results yet", ha="center", va="center")
        return fig

    scores = [r.get("faithfulness", r.get("score", 0)) for r in results]
    fig, ax = plt.subplots()
    ax.scatter(range(len(scores)), scores, color="#1D5C39", label="Trials", alpha=0.7)

    if best_index is not None and 0 <= best_index < len(scores):
        ax.scatter(best_index, scores[best_index], color="gold", s=120, edgecolor="black", label="Best Run")

    ax.set_title("Trial Scores", color="#1D5C39")
    ax.set_xlabel("Trial #")
    ax.set_ylabel("Faithfulness")
    ax.legend()

    # Force integer steps on the X axis
    ax.xaxis.set_major_locator(MultipleLocator(1))
    ax.set_xlim(-0.5, len(scores) - 0.5)  # better spacing on the ends

    plt.tight_layout()
    return fig

def export_best_config(best_json_str: str):
    """
    Export best configuration as config.yaml with only selected fields.
    """
    try:
        best = json.loads(best_json_str)
        allowed_fields = ["retriever", "embedding_model", "reranker", "chunk_size", "overlap", "strategy"]
        config = {k: best[k] for k in allowed_fields if k in best}

        if not config:
            return "⚠️ No valid configuration fields found."

        config_path = os.path.join(DATA_DIR, "config.yaml")
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        return f"✅ Exported configuration to {config_path}"

    except Exception as e:
        return f"⚠️ Error exporting config: {str(e)}"


# ----------------------------------------------------------------------
# ACTION HANDLERS
# ----------------------------------------------------------------------
def handle_upload(files):
    if not files:
        return "No files provided."
    saved = save_uploaded_files(files)
    return f"✅ Saved {len(saved)} files to {DATA_DIR}."

def do_auto_tune(
    embedding_model: str,
    num_chunk_pairs: int,
    search_type: str,
    trials: int,
    validation_choice: str,
    hf_dataset: str = None
):
    tuner = AutoRAGTuner(docs_path=DATA_DIR)
    rec = tuner.recommend(embedding_model=embedding_model, num_chunk_pairs=num_chunk_pairs)
    num_chunk_pairs = int(num_chunk_pairs)

    # FIX: use num_chunk_pairs instead of None
    chunk_candidates = tuner.suggest_chunk_sizes(
        model_name=rec["embedding_model"],
        num_pairs=num_chunk_pairs,
        step=20
    )
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

    validation_set = None
    if validation_choice == "Upload JSON":
        validation_path = os.path.join(DATA_DIR, "validation_qa.json")
        if os.path.exists(validation_path):
            validation_set = validation_path
    elif validation_choice == "HuggingFace Dataset" and hf_dataset:
        validation_set = hf_dataset.strip()

    try:
        best, results = rag.optimize(
            validation_set=validation_set,
            metric="faithfulness",
            search_type=search_type,
            trials=trials,
        )

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

        # --- Plot scatter ---
        best_index = next((i for i, r in enumerate(results)
                           if r.get("faithfulness") == best.get("faithfulness")), None)
        fig = plot_score_scatter(results, best_index)

        # --- Inline explanation (string/markdown) ---
        explanation = explain_results(best, results, corpus_stats=corpus_stats)

        # Return exactly three outputs matching your Gradio components:
        # 1) best configuration JSON (string)
        # 2) Matplotlib figure
        # 3) explanation markdown/string
        return (
            json.dumps(best, indent=2),
            fig,
            explanation
        )

    except Exception as e:
        # Return a placeholder figure if there’s an error and match output types
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, str(e), ha="center", va="center", color="red")
        ax.axis("off")
        # 1) error string for best_json  2) placeholder fig  3) explanation/error markdown
        return "Error during tuning", fig, f"⚠️ {str(e)}"

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

#logo {{
    display: flex;
    align-items: center;
    justify-content: center; /* center horizontally */
    padding: 0;            /* remove padding */
    margin: 0;             /* remove margin */
    box-shadow: none;      /* remove shadow */
    border: none;          /* remove any border */
}}

#logo img {{
    height: 80px;
    width: auto;
}}

#logo button {{
    background-color: rgba(29, 92, 57, 0.1); !important;
    color: white !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}}

.custom-summary {{
    background-color: #f4f4f4;               /* clean light grey background */
    border: 1px solid rgba(0, 0, 0, 0.08);   /* subtle border */
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);   /* soft depth */
    transition: all 0.3s ease-in-out;
}}

"""


# ----------------------------------------------------------------------
# BUILD GRADIO APP
# ----------------------------------------------------------------------

with gr.Blocks(css=custom_css, theme=gr.themes.Ocean()) as demo:
    with gr.Row(elem_id="logo"):
        gr.Image(value=LOGO_PATH, show_label=False, interactive=False, elem_id="logo_img")

    gr.Markdown(f"# Ragmint - RAG Automated Tuning")
    gr.Markdown("Auto-tune your RAG pipeline, benchmark performance, visualize results, and get AI-driven insights.")

    # --- Corpus & API Key Upload ---
    with gr.Tab("📂 Configuration"):
        with gr.Row():
            # --- LEFT SIDE: Main Steps ---
            with gr.Column(scale=3):
                gr.Markdown("### 1️⃣ Upload Corpus Files")
                uploader = gr.File(label="Upload corpus files", file_count="multiple")
                upload_btn = gr.Button("Upload Files", variant="primary")

                gr.Markdown("### 2️⃣ Add LLM Key")
                api_provider = gr.Radio(
                    label="Provider",
                    choices=["Google", "Anthropic"],
                    value="Google"
                )

                api_key_input = gr.Textbox(
                    label="API Key",
                    placeholder="Paste your API key here",
                    type="password"
                )
                save_api_btn = gr.Button("Save API Key", variant="primary")



                gr.Markdown("### 3️⃣ Validation Dataset (Optional)")
                validation_source = gr.Radio(
                    label="Validation Source",
                    choices=["Default File","Upload JSON","HuggingFace Dataset"],
                    value="Default File"
                )

                with gr.Row(visible=False) as validation_upload_row:
                    validation_file = gr.File(
                        label="Upload validation_qa.json",
                        file_count="single",
                        interactive=True
                    )
                    upload_validation_btn = gr.Button("Upload Validation File", variant="primary")

                validation_hf_dataset = gr.Textbox(
                    label="HuggingFace Dataset Name",
                    placeholder="e.g. squad, hotpot_qa, or your own dataset",
                    interactive=True,
                    visible=False
                )



            # --- RIGHT SIDE: Status Summary ---
            with gr.Column(scale=1, elem_classes=["custom-summary"]):
                gr.Markdown("### ⚙️ Configuration")
                gr.Markdown("Monitor your current setup below:")
                upload_status = gr.Textbox(label="File Upload Status", interactive=False)
                save_status = gr.Textbox(label="API Key Status", interactive=False)
                validation_status = gr.Textbox(label="Validation Selection", interactive=False)

        # --- Event bindings ---
        upload_btn.click(fn=handle_upload, inputs=[uploader], outputs=[upload_status])
        save_api_btn.click(
            fn=save_api_key,
            inputs=[api_key_input, api_provider],
            outputs=[save_status]
        )
        upload_validation_btn.click(fn=handle_validation_upload, inputs=[validation_file], outputs=[validation_status])
        validation_source.change(
            fn=toggle_validation_inputs,
            inputs=[validation_source],
            outputs=[validation_upload_row, validation_hf_dataset, validation_status]
        )

    # --- Unified AutoTune ---
    with gr.Tab("🤖 AutoTune"):
        # 🌿 Custom CSS for dashboard-like cards
        gr.HTML("""
        <style>
        .card {
            background-color: #f4f4f4;               /* clean light grey background */
            border: 1px solid rgba(0, 0, 0, 0.08);   /* subtle border */
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);   /* soft depth */
            transition: all 0.3s ease-in-out;
        }
        .card:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }
        .section-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1D5C39;
            margin-bottom: 8px;
        }
        </style>
        """)

        # ⚙️ Settings
        with gr.Column(elem_classes=["card"]):
            gr.Markdown("⚙️ <span class='section-title'>AutoTuner Settings</span>")
            with gr.Accordion("Advanced Settings", open=False):
                embed_model = gr.Textbox(
                    value="sentence-transformers/all-MiniLM-L6-v2",
                    label="Embedding Model",
                    info="Model used to generate text embeddings for retrieval."
                )
                num_pairs = gr.Number(
                    value=5,
                    label="Chunk Candidates",
                    info="Number of chunk size-overlap pairs to test."
                )
                search_type = gr.Dropdown(
                    choices=["random", "grid", "bayesian"],
                    value="grid",
                    label="Search Type",
                    info="Method used for optimization search over hyperparameters."
                )
                trials = gr.Slider(
                    minimum=1, maximum=50, step=1, value=5,
                    label="Trials",
                    info="Number of trials to run during optimization."
                )

            autotune_btn = gr.Button("🚀 Run AutoTune", elem_id="autotune_btn", variant="primary")

        # 🏆 Best Configuration
        with gr.Row(elem_classes=["card"]):
            with gr.Column():
                gr.Markdown("🏆 <span class='section-title'>Best Configuration</span>")
                best_json = gr.Textbox(label="", interactive=False, lines=10)

        # 📊 Trial Scores
        with gr.Row(elem_classes=["card"]):
            with gr.Column():
                gr.Markdown("📊 <span class='section-title'>Trial Scores</span>")
                score_plot = gr.Plot(label="")

        # 💡 Explanation
        with gr.Row(elem_classes=["card"]):
            with gr.Column():
                gr.Markdown("💡 <span class='section-title'>Explanation</span>")
                explanation_md = gr.Markdown(label="")

        export_btn = gr.Button("Export Best Configuration", variant="primary", visible=False)
        export_status = gr.Textbox(label="Export Status", interactive=False, visible=False)

        # 🔗 Connect button logic
        autotune_btn.click(
            fn=do_auto_tune,
            inputs=[embed_model, num_pairs, search_type, trials, validation_source, validation_hf_dataset],
            outputs=[best_json, score_plot, explanation_md],
            show_progress=True
        ).then(
            fn=lambda: (gr.update(visible=True), gr.update(visible=True)),
            inputs=None,
            outputs=[export_btn, export_status]
        )

        export_btn.click(
            fn=export_best_config,
            inputs=[best_json],
            outputs=[export_status]
        )

    with gr.Tab("🏆 Leaderboard"):
        show_btn = gr.Button("Refresh",variant="primary")
        lb_table = gr.Dataframe(label="Leaderboard", interactive=False)
        lb_json = gr.Textbox(label="Raw JSON", interactive=False)
        show_btn.click(fn=show_leaderboard_table, outputs=[lb_table, lb_json])


    gr.Markdown(
        f"<center><p font-size:0.9em;'>"
        "Built with ❤️ using RAGMint · © 2025 andyolivers.com</p></center>"
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, show_api=False)
