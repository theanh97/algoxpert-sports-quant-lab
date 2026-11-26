"""Portfolio-grade visual evidence generated only from experiment artifacts."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from sports_quant_lab.constants import FIGURES_DIR
from sports_quant_lab.evaluation import calibration_table
from sports_quant_lab.research import MODEL_LABELS, MODEL_ORDER

BG = "#07111d"
PANEL = "#0d1b2a"
GRID = "#20354a"
TEXT = "#eaf4f6"
MUTED = "#92a6b5"
TEAL = "#35dfbd"
CYAN = "#47b9ff"
AMBER = "#ffbd69"
PINK = "#fa7891"
VIOLET = "#b294ff"
GREEN = "#80e5a4"
MODEL_COLORS = {
    "league_prior": MUTED,
    "elo_raw": "#5e8cc5",
    "elo_temp": CYAN,
    "logistic_raw": "#cb82dd",
    "logistic_temp": VIOLET,
    "dixon_coles_raw": "#e88864",
    "dixon_coles_temp": TEAL,
}


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BG,
            "axes.facecolor": PANEL,
            "axes.edgecolor": GRID,
            "axes.labelcolor": MUTED,
            "text.color": TEXT,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.titlecolor": TEXT,
            "axes.titleweight": "bold",
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.65,
            "savefig.facecolor": BG,
            "savefig.edgecolor": BG,
        }
    )


def _save(fig: plt.Figure, name: str, svg: bool = False) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=190, bbox_inches="tight")
    if svg:
        fig.savefig(FIGURES_DIR / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def _cover() -> None:
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.set_facecolor(BG)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.add_patch(Rectangle((0.55, 0.55), 14.9, 7.9, fill=False, ec="#17384a", lw=1.2))
    ax.plot([8, 8], [0.55, 8.45], color="#17384a", lw=1.1)
    ax.add_patch(plt.Circle((8, 4.5), 1.15, fill=False, ec="#17384a", lw=1.1))
    ax.add_patch(Rectangle((0.55, 2.55), 1.7, 3.9, fill=False, ec="#17384a", lw=1.1))
    ax.add_patch(Rectangle((13.75, 2.55), 1.7, 3.9, fill=False, ec="#17384a", lw=1.1))
    x = np.linspace(8.7, 14.8, 400)
    y = 4.5 + 1.1 * np.sin(x * 1.15) * np.exp(-(x - 8.7) / 8.5)
    ax.plot(x, y, color=TEAL, lw=2.6, alpha=0.9)
    ax.fill_between(x, y, 4.5, color=TEAL, alpha=0.08)
    for x0, height in [(9.3, 0.38), (10.6, 0.52), (11.9, 0.29), (13.2, 0.67), (14.5, 0.46)]:
        ax.add_patch(Rectangle((x0, 1.15), 0.56, height, color=CYAN, alpha=0.62))
    ax.text(1.05, 7.65, "ALGOXPERT  /  RESEARCH INITIATIVE", color=TEAL, fontsize=12, weight="bold", va="top")
    ax.text(1.0, 6.25, "SPORTS\nQUANT LAB", color=TEXT, fontsize=40, weight="bold", va="top", linespacing=1.0)
    ax.text(1.08, 3.75, "MLS CASE STUDY  ·  PROBABILITY, NOT PICK RATE", color=CYAN, fontsize=12, weight="bold")
    ax.text(1.08, 3.18, "Walk-forward evidence. Leakage checks. Reproducible research.", color=MUTED, fontsize=14)
    ax.text(1.08, 1.1, "RESEARCH RELEASE  v1.0   /   2013-2026 SOURCE COVERAGE", color=MUTED, fontsize=9, family="monospace")
    fig.subplots_adjust(0, 0, 1, 1)
    _save(fig, "portfolio_cover", svg=True)


def _architecture() -> None:
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_facecolor(BG)
    nodes = [
        (0.4, 5.4, 2.3, 1.25, "01  SOURCE", "ASA public API\nCC BY-SA 4.0", CYAN),
        (3.25, 5.4, 2.3, 1.25, "02  SNAPSHOT", "Raw JSON + SHA-256\nimmutable retrieval", VIOLET),
        (6.1, 5.4, 2.3, 1.25, "03  DATA AUDIT", "Coverage · duplicates\nmissingness · cutoffs", AMBER),
        (8.95, 5.4, 2.3, 1.25, "04  MODELS", "Prior / Elo / Logistic\nDixon-Coles", TEAL),
        (11.8, 5.4, 2.6, 1.25, "05  EVALUATE", "Season holdouts\nproper scores + CI", GREEN),
        (2.15, 2.55, 3.0, 1.35, "CALIBRATION", "Prior-season OOF\ntemperature scaling", CYAN),
        (6.0, 2.55, 3.0, 1.35, "VERIFICATION", "Leakage gates · tests\nreliability · limitations", AMBER),
        (9.85, 2.55, 3.0, 1.35, "DELIVER", "Streamlit · reports\nfigures · content", TEAL),
    ]
    centers = []
    for x, y, w, h, title, body, color in nodes:
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.12", fc=PANEL, ec=color, lw=1.6)
        ax.add_patch(box)
        ax.text(x + 0.18, y + h - 0.3, title, color=color, fontsize=10, weight="bold", va="top")
        ax.text(x + 0.18, y + 0.25, body, color=TEXT, fontsize=10, va="bottom", linespacing=1.35)
        centers.append((x + w / 2, y + h / 2))
    for start, end in [(0, 1), (1, 2), (2, 3), (3, 4), (4, 7), (7, 6), (6, 5)]:
        arrow = FancyArrowPatch(centers[start], centers[end], arrowstyle="-|>", mutation_scale=14, lw=1.4, color="#66869a", connectionstyle="arc3,rad=0.0")
        ax.add_patch(arrow)
    ax.text(0.5, 7.42, "RESEARCH SYSTEM  /  REPRODUCIBLE MLS CASE STUDY", color=TEXT, fontsize=16, weight="bold")
    ax.text(0.52, 0.92, "Current release: outcome-only match history. No market odds or execution layer.", color=MUTED, fontsize=11)
    _save(fig, "architecture_diagram", svg=True)


def _benchmark(metrics: pd.DataFrame) -> None:
    ordered = metrics.set_index("model").loc[list(MODEL_ORDER)].reset_index()
    labels = ordered.display_name.tolist()
    colors = [MODEL_COLORS[name] for name in ordered.model]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7), gridspec_kw={"width_ratios": [1.0, 1.1]})
    y = np.arange(len(ordered))
    ax1.barh(y, ordered.log_loss, color=colors, height=0.65, alpha=0.94)
    ax1.set_yticks(y, labels)
    ax1.invert_yaxis()
    ax1.set_xlabel("Multiclass log loss  ·  lower is better")
    ax1.set_title("Out-of-sample probability score")
    for yi, value in zip(y, ordered.log_loss):
        ax1.text(value + 0.008, yi, f"{value:.3f}", va="center", color=TEXT, fontsize=9)
    delta = ordered.bootstrap_delta_log_loss_vs_prior.to_numpy()
    low = ordered.bootstrap_delta_log_loss_ci95_low.to_numpy()
    high = ordered.bootstrap_delta_log_loss_ci95_high.to_numpy()
    ax2.axvline(0, color=TEXT, lw=1, alpha=0.55)
    ax2.errorbar(
        delta, y, xerr=np.vstack([delta - low, high - delta]), fmt="o", capsize=4,
        color=CYAN, ecolor="#9bb2c1", markersize=6, lw=1.2,
    )
    ax2.set_yticks(y, ["" for _ in labels])
    ax2.invert_yaxis()
    ax2.set_xlabel("Δ log loss vs league prior  ·  paired 95% bootstrap interval")
    ax2.set_title("Uncertainty in the score difference")
    ax2.text(0.02, -0.15, "Negative values favor the model; intervals overlapping zero are inconclusive.", transform=ax2.transAxes, color=MUTED, fontsize=9)
    fig.suptitle("MLS walk-forward benchmark  |  all evaluated test seasons", x=0.06, ha="left", fontsize=16, weight="bold")
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    _save(fig, "model_benchmark", svg=True)


def _calibration(predictions: pd.DataFrame) -> None:
    selected_models = ["league_prior", "elo_temp", "logistic_temp", "dixon_coles_temp"]
    styles = {"league_prior": "--", "elo_temp": ":", "logistic_temp": "-.", "dixon_coles_temp": "-"}
    table_items = []
    for model in selected_models:
        subset = predictions.loc[predictions.model == model]
        table = calibration_table(subset.outcome, subset[["p_home", "p_draw", "p_away"]].to_numpy())
        table["model"] = model
        table_items.append(table)
    all_bins = pd.concat(table_items, ignore_index=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.3), sharex=True, sharey=True)
    for ax, label, column, title in zip(axes, ("H", "D", "A"), ("p_home", "p_draw", "p_away"), ("Home win", "Draw", "Away win")):
        ax.plot([0, 1], [0, 1], color=MUTED, lw=1, linestyle="--", alpha=0.65)
        for model in selected_models:
            rows = all_bins.loc[(all_bins.model == model) & (all_bins["class"] == label)].sort_values("bin")
            if rows.empty:
                continue
            ax.plot(
                rows.mean_probability, rows.observed_frequency,
                color=MODEL_COLORS[model], marker="o", ms=4, lw=1.6,
                linestyle=styles[model], label=MODEL_LABELS[model],
            )
        ax.set_title(title)
        ax.set_xlabel("Mean predicted probability")
        ax.grid(True, alpha=0.65)
    axes[0].set_ylabel("Observed frequency")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.04), fontsize=8)
    fig.suptitle("Probability reliability  |  prior-season calibrated variants", x=0.04, ha="left", fontsize=15, weight="bold")
    fig.tight_layout(rect=(0, 0.11, 1, 0.9))
    _save(fig, "calibration_curve", svg=True)


def _score_distribution() -> None:
    path = FIGURES_DIR.parent / "scoreline_distribution.csv"
    table = pd.read_csv(path)
    k = min(8, int(table.home_goals.max()) + 1)
    pred = table.pivot(index="home_goals", columns="away_goals", values="predicted_probability").to_numpy()[:k, :k]
    obs = table.pivot(index="home_goals", columns="away_goals", values="observed_frequency").to_numpy()[:k, :k]
    fig = plt.figure(figsize=(16, 5.7), layout="constrained")
    grid = fig.add_gridspec(1, 5, width_ratios=[1, 1, 0.055, 0.9, 0.055], wspace=0.18)
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[0, 3])]
    vmax = max(pred.max(), obs.max()) * 100
    for ax, data, title in [(axes[0], pred * 100, "Forecast mass"), (axes[1], obs * 100, "Observed frequency")]:
        im = ax.imshow(data, cmap="viridis", origin="lower", vmin=0, vmax=vmax)
        ax.set_title(title)
        ax.set_xlabel("Away goals")
        ax.set_ylabel("Home goals")
        ax.set_xticks(range(k))
        ax.set_yticks(range(k))
    fig.colorbar(im, cax=fig.add_subplot(grid[0, 2]), label="Share of matches (%)")
    difference = (obs - pred) * 100
    vmax_diff = max(0.5, float(np.nanmax(np.abs(difference))))
    im2 = axes[2].imshow(difference, cmap="coolwarm", origin="lower", vmin=-vmax_diff, vmax=vmax_diff)
    axes[2].set_title("Observed - forecast")
    axes[2].set_xlabel("Away goals")
    axes[2].set_ylabel("Home goals")
    axes[2].set_xticks(range(k))
    axes[2].set_yticks(range(k))
    fig.colorbar(im2, cax=fig.add_subplot(grid[0, 4]), label="Percentage points")
    fig.suptitle("Dixon-Coles scoreline distribution  |  held-out matches", x=0.04, ha="left", fontsize=15, weight="bold")
    _save(fig, "score_distribution", svg=True)


def _walk_forward(by_season: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(13, 6.5))
    for model in MODEL_ORDER:
        rows = by_season.loc[by_season.model == model].sort_values("season")
        ax.plot(rows.season, rows.log_loss, marker="o", ms=4, lw=1.8, color=MODEL_COLORS[model], label=MODEL_LABELS[model])
    ax.set_xlabel("Held-out season")
    ax.set_ylabel("Multiclass log loss  ·  lower is better")
    ax.set_title("Annual walk-forward performance", loc="left", fontsize=15, pad=16)
    ax.set_xticks(sorted(by_season.season.unique()))
    ax.tick_params(axis="x", rotation=30)
    ax.legend(ncol=2, frameon=False, fontsize=8)
    fig.tight_layout()
    _save(fig, "walk_forward", svg=True)


def _coverage(audit: dict) -> None:
    table = pd.DataFrame(audit["coverage_by_season"]).fillna(0).sort_values("season")
    table["Regular season"] = table.get("Regular season", 0)
    table["Knockout"] = table.get("Knockout", 0)
    fig, ax = plt.subplots(figsize=(13, 5.7))
    x = np.arange(len(table))
    ax.bar(x, table["Regular season"], color=TEAL, label="Regular season", width=0.72)
    ax.bar(x, table["Knockout"], bottom=table["Regular season"], color=AMBER, label="Knockout", width=0.72)
    ax.set_xticks(x, table.season.astype(int), rotation=35)
    ax.set_ylabel("Completed matches in API snapshot")
    ax.set_title("MLS source coverage by season  |  completed ASA records", loc="left", fontsize=15, pad=16)
    ax.legend(frameon=False)
    for xi, value in zip(x, table["Regular season"]):
        ax.text(xi, value + 4, str(int(value)), ha="center", color=TEXT, fontsize=8)
    fig.tight_layout()
    _save(fig, "data_coverage", svg=True)


def _verification(audit: dict) -> None:
    checks = audit["verification"]["checks"]
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.2, len(checks) + 2.0)
    ax.axis("off")
    status_color = GREEN if audit["verification"]["status"] == "PASS" else PINK
    ax.text(0.3, len(checks) + 1.1, f"VERIFICATION  /  {audit['verification']['status']}", color=status_color, fontsize=17, weight="bold")
    for i, check in enumerate(checks):
        y = len(checks) - i
        marker = "PASS" if check["passed"] else "FAIL"
        color = GREEN if check["passed"] else PINK
        ax.add_patch(FancyBboxPatch((0.35, y - 0.35), 1.0, 0.48, boxstyle="round,pad=0.03,rounding_size=0.08", fc=color, ec="none", alpha=0.18))
        ax.text(0.85, y - 0.11, marker, color=color, fontsize=8, weight="bold", ha="center", va="center")
        ax.text(1.6, y, check["name"], color=TEXT, fontsize=11, va="center")
        ax.text(9.55, y, "✓" if check["passed"] else "×", color=color, fontsize=14, ha="right", va="center")
    ax.text(0.4, 0.05, "Source revision history is not point-in-time; see report limitations.", color=MUTED, fontsize=9)
    _save(fig, "verification_report", svg=True)


def _collage() -> None:
    names = [
        ("portfolio_cover", "Portfolio cover"),
        ("architecture_diagram", "Research architecture"),
        ("model_benchmark", "Model benchmark"),
        ("calibration_curve", "Calibration"),
        ("score_distribution", "Scoreline distribution"),
        ("walk_forward", "Walk-forward stability"),
        ("data_coverage", "Data coverage"),
        ("verification_report", "Verification report"),
    ]
    fig, axes = plt.subplots(2, 4, figsize=(18, 9))
    for ax, (name, title) in zip(axes.flat, names):
        ax.imshow(plt.imread(FIGURES_DIR / f"{name}.png"))
        ax.axis("off")
        ax.set_title(title, color=TEXT, fontsize=10, pad=7)
    fig.suptitle("AlgoXpert Sports Quant Lab  ·  evidence pack", fontsize=17, weight="bold", color=TEXT, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    _save(fig, "portfolio_collage")


def generate_visuals(
    matches: pd.DataFrame,
    predictions: pd.DataFrame,
    metrics: pd.DataFrame,
    by_season: pd.DataFrame,
    audit: dict,
) -> None:
    _style()
    _cover()
    _architecture()
    _benchmark(metrics)
    _calibration(predictions)
    _score_distribution()
    _walk_forward(by_season)
    _coverage(audit)
    _verification(audit)
    _collage()

