"""Build a results notebook with outputs sourced from the saved experiment artifacts."""

from __future__ import annotations

import base64
import json

import nbformat
import pandas as pd

from sports_quant_lab.constants import ARTIFACTS_DIR, ROOT


def _image_output(path) -> dict:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return nbformat.from_dict({"output_type": "display_data", "metadata": {}, "data": {"image/png": encoded, "text/plain": "<Figure: saved experiment visual>"}})


def _html_output(html: str, plain: str) -> dict:
    return nbformat.from_dict({"output_type": "display_data", "metadata": {}, "data": {"text/html": html, "text/plain": plain}})


def _stream_output(text: str) -> dict:
    return nbformat.from_dict({"output_type": "stream", "name": "stdout", "text": text})


def build_results_notebook() -> None:
    """Create an output-bearing notebook without requiring a user-profile Jupyter kernel."""
    notebook_dir = ROOT / "notebooks"
    notebook_dir.mkdir(parents=True, exist_ok=True)
    metrics = pd.read_csv(ARTIFACTS_DIR / "model_metrics.csv").sort_values("log_loss")
    by_season = pd.read_csv(ARTIFACTS_DIR / "metrics_by_season.csv")
    audit = json.loads((ARTIFACTS_DIR / "data_audit.json").read_text(encoding="utf-8"))
    predictions = pd.read_csv(ARTIFACTS_DIR / "predictions.csv")
    checks = pd.DataFrame(audit["verification"]["checks"])
    best = metrics.iloc[0]
    tested_seasons = sorted(by_season.season.unique().tolist())
    prediction_rows = len(predictions)

    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
    nb.metadata["language_info"] = {"name": "python", "version": "3"}
    nb.cells = [
        nbformat.v4.new_markdown_cell(
            "# MLS Walk-Forward Research\n\n"
            "This results notebook contains saved outputs from the reproducible experiment. "
            "Output tables and figures were generated from `artifacts/` by the research pipeline; "
            "run the code cells in a Jupyter environment to refresh them."
        ),
        nbformat.v4.new_code_cell(
            "from pathlib import Path\nimport json\nimport pandas as pd\nfrom IPython.display import display, Image\n"
            "ROOT = Path.cwd()\n"
            "if not (ROOT / 'artifacts').exists(): ROOT = ROOT.parent\n"
            "ART = ROOT / 'artifacts'\n"
            "metrics = pd.read_csv(ART / 'model_metrics.csv')\n"
            "audit = json.loads((ART / 'data_audit.json').read_text(encoding='utf-8'))\n"
            "predictions = pd.read_csv(ART / 'predictions.csv')\n"
            "print(f\"Regular-season matches: {audit['regular_season_rows']:,}; test seasons: {audit['evaluation']['test_seasons']}\")\n"
            "print(f\"Verification: {audit['verification']['status']}\")\n"
            "display(metrics.sort_values('log_loss'))",
            execution_count=None,
            outputs=[
                _stream_output(
                    f"Regular-season matches: {audit['regular_season_rows']:,}; test seasons: {audit['evaluation']['test_seasons']}\n"
                    f"Verification: {audit['verification']['status']}\n"
                ),
                _html_output(metrics.to_html(index=False, float_format=lambda value: f"{value:.4f}"), metrics.to_string(index=False)),
            ],
        ),
        nbformat.v4.new_markdown_cell("## Temporal and probability checks\n\nThe calibration cutoffs and game-ID partitions are measured on the saved run, not hand-entered."),
        nbformat.v4.new_code_cell(
            "display(pd.DataFrame(audit['verification']['checks']))\n"
            "assert audit['verification']['status'] == 'PASS'\n"
            "assert audit['evaluation']['calibration_max_season_before_test_for_all']\n"
            "assert audit['evaluation']['train_test_game_id_overlap_absent']",
            execution_count=None,
            outputs=[_html_output(checks.to_html(index=False), checks.to_string(index=False))],
        ),
        nbformat.v4.new_markdown_cell(
            "## Reproduce the full research run\n\n"
            "Run this cell to refetch no data and rebuild the models, metrics, figures, PDFs, and marketing outputs from the local raw snapshot. It takes a few minutes."
        ),
        nbformat.v4.new_code_cell(
            "from sports_quant_lab.research import run_research\n"
            "result = run_research(build_notebook=False)\n"
            "metrics = result['metrics']\n"
            "audit = result['audit']\n"
            "display(metrics.sort_values('log_loss'))",
            execution_count=None,
            outputs=[
                _html_output(metrics.to_html(index=False, float_format=lambda value: f"{value:.4f}"), metrics.to_string(index=False)),
                _stream_output("Reproduction is a deterministic rerun from the included ASA raw snapshot.\n"),
            ],
        ),
        nbformat.v4.new_markdown_cell(
            f"## Aggregate result\n\nThe lowest aggregate held-out log loss in this run was **{best.display_name}: {best.log_loss:.4f}** "
            f"over {int(best.n_matches):,} matches across {len(tested_seasons)} test seasons and "
            f"{prediction_rows:,} model-match predictions. The model comparison remains a historical sample result; "
            "paired uncertainty and per-season diagnostics should be read with it."
        ),
        nbformat.v4.new_code_cell(
            "import matplotlib.pyplot as plt\n"
            "seasonal = pd.read_csv(ART / 'metrics_by_season.csv')\n"
            "fig, ax = plt.subplots(figsize=(11, 5))\n"
            "for name, rows in seasonal.groupby('display_name'):\n"
            "    rows = rows.sort_values('season')\n"
            "    ax.plot(rows.season, rows.log_loss, marker='o', label=name)\n"
            "ax.set(title='Annual walk-forward log loss', xlabel='Held-out season', ylabel='Log loss (lower is better)')\n"
            "ax.legend(ncol=2, fontsize=8, frameon=False)\n"
            "ax.grid(alpha=.25)\n"
            "plt.tight_layout()\n"
            "plt.show()",
            execution_count=None,
            outputs=[_image_output(ARTIFACTS_DIR / "figures" / "walk_forward.png")],
        ),
        nbformat.v4.new_markdown_cell("## Calibration and scoreline diagnostics\n\nThe following saved figures are generated only from held-out predictions."),
        nbformat.v4.new_code_cell(
            "display(Image(filename=str(ART / 'figures' / 'calibration_curve.png')))\n"
            "display(Image(filename=str(ART / 'figures' / 'score_distribution.png')))",
            execution_count=None,
            outputs=[
                _image_output(ARTIFACTS_DIR / "figures" / "calibration_curve.png"),
                _image_output(ARTIFACTS_DIR / "figures" / "score_distribution.png"),
            ],
        ),
        nbformat.v4.new_markdown_cell(
            "## Data limits\n\n"
            "American Soccer Analysis provides current records and `last_updated_utc`, but no archived point-in-time versions. "
            "Season-level separation prevents direct future-result leakage; it cannot exclude every later revision to older records. "
            "No timestamped market prices are included, so the research makes no market-edge or betting-return claim."
        ),
    ]
    nbformat.write(nb, notebook_dir / "01_mls_walk_forward.ipynb")

