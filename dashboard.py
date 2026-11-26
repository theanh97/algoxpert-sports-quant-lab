"""Interactive research dashboard; reads generated artifacts and displays real results."""

from __future__ import annotations

import json

import pandas as pd
import plotly.express as px
import streamlit as st

from sports_quant_lab.constants import ARTIFACTS_DIR
from sports_quant_lab.evaluation import calibration_table
from sports_quant_lab.research import MODEL_LABELS, MODEL_ORDER

st.set_page_config(page_title="Sports Quant Lab | MLS", page_icon="⚽", layout="wide")
st.markdown(
    "<style>.stApp{background:#07111d;color:#eaf4f6;}[data-testid=stSidebar]{background:#0d1b2a;color:#eaf4f6;}[data-testid=stSidebar] *{color:#eaf4f6;}[data-testid=stSidebar] .stSelectbox label{color:#92a6b5!important;}[data-testid=stSelectbox] .react-aria-ComboBox>div{background:#13263a!important;border:1px solid #29435a!important;}[data-testid=stSelectbox] .react-aria-ComboBox input{color:#eaf4f6!important;-webkit-text-fill-color:#eaf4f6!important;}[data-testid=stMetric]{background:#0d1b2a;border:1px solid #20354a;padding:16px;border-radius:12px;}[data-testid=stMetricLabel]{color:#92a6b5!important;}[data-testid=stMetricValue],[data-testid=stMetricValue] div{color:#eaf4f6!important;font-size:1.2rem!important;}h1,h2,h3{color:#eaf4f6;}header[data-testid=stHeader]{background:#07111d;}</style>",
    unsafe_allow_html=True,
)


@st.cache_data
def load_artifacts():
    required = [
        ARTIFACTS_DIR / "model_metrics.csv",
        ARTIFACTS_DIR / "metrics_by_season.csv",
        ARTIFACTS_DIR / "predictions.csv",
        ARTIFACTS_DIR / "data_audit.json",
        ARTIFACTS_DIR / "scoreline_distribution.csv",
    ]
    if not all(path.exists() for path in required):
        return None
    return (
        pd.read_csv(required[0]),
        pd.read_csv(required[1]),
        pd.read_csv(required[2], parse_dates=["date_time_utc"]),
        json.loads(required[3].read_text(encoding="utf-8")),
        pd.read_csv(required[4]),
    )


artifacts = load_artifacts()
if artifacts is None:
    st.title("AlgoXpert Sports Quant Lab")
    st.error("Research artifacts are missing. Run `sports-quant run` after installing dependencies.")
    st.stop()

metrics, by_season, predictions, audit, scorelines = artifacts
st.title("SPORTS QUANT LAB")
st.caption("AlgoXpert Research Initiative  /  MLS case study  /  Probability verification")
st.markdown("Quantitative models are assessed with held-out seasons, proper scoring rules, and explicit data lineage.")

with st.sidebar:
    st.header("Research controls")
    model = st.selectbox(
        "Forecast model",
        options=list(MODEL_ORDER),
        format_func=lambda x: MODEL_LABELS[x],
        index=MODEL_ORDER.index("dixon_coles_temp"),
    )
    available_seasons = sorted(predictions.test_season.unique())
    season = st.selectbox("Held-out season", options=["All"] + [int(x) for x in available_seasons])
    st.divider()
    st.caption(f"Source: American Soccer Analysis API\n\nRetrieved: {audit['retrieved_utc']}\n\nLicense: CC BY-SA 4.0")
    st.caption(f"Verification gates: {audit['verification']['status']}")

selected = predictions.loc[predictions.model == model].copy()
if season != "All":
    selected = selected.loc[selected.test_season == int(season)]
selected_metrics = metrics.loc[metrics.model == model].iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric("Matches", f"{len(selected):,}")
col2.metric("Log loss", f"{selected_metrics.log_loss:.3f}", help="Lower is better; proper multiclass probability score.")
col3.metric("Brier score", f"{selected_metrics.brier:.3f}", help="Mean multiclass squared probability error; lower is better.")
col4.metric("Top-label ECE", f"{selected_metrics.top_label_ece_10:.3f}", help="Ten-bin expected calibration error; binning-sensitive.")

tab1, tab2, tab3, tab4 = st.tabs(["Benchmark", "Calibration", "Scorelines", "Data & verification"])
with tab1:
    st.subheader("Model comparison")
    chart = metrics.set_index("display_name")[["log_loss", "brier", "accuracy", "top_label_ece_10"]].reset_index()
    chart_long = chart.melt(id_vars="display_name", var_name="metric", value_name="value")
    fig = px.bar(chart_long, x="display_name", y="value", color="metric", barmode="group", title="Out-of-sample model scores")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#07111d", plot_bgcolor="#0d1b2a", font_color="#eaf4f6", title_font_color="#eaf4f6", legend_font_color="#eaf4f6", legend_title_font_color="#92a6b5", xaxis_tickfont_color="#92a6b5", yaxis_tickfont_color="#92a6b5", legend_title="Metric", xaxis_title="Model", yaxis_title="Score")
    st.plotly_chart(fig, use_container_width=True)
    seasonal = by_season.loc[by_season.model == model].sort_values("season")
    fig2 = px.line(seasonal, x="season", y="log_loss", markers=True, title=f"Annual walk-forward log loss: {MODEL_LABELS[model]}")
    fig2.update_layout(template="plotly_dark", paper_bgcolor="#07111d", plot_bgcolor="#0d1b2a", font_color="#eaf4f6", title_font_color="#eaf4f6", legend_font_color="#eaf4f6", xaxis_tickfont_color="#92a6b5", yaxis_tickfont_color="#92a6b5", xaxis_title="Held-out season", yaxis_title="Log loss (lower is better)")
    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(
        metrics[["display_name", "n_matches", "log_loss", "brier", "accuracy", "ranked_probability_score", "top_label_ece_10", "bootstrap_delta_log_loss_vs_prior", "bootstrap_delta_log_loss_ci95_low", "bootstrap_delta_log_loss_ci95_high"]].sort_values("log_loss"),
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.subheader("Reliability by outcome")
    calibration = calibration_table(selected.outcome, selected[["p_home", "p_draw", "p_away"]].to_numpy())
    calibration["outcome"] = calibration["class"].map({"H": "Home win", "D": "Draw", "A": "Away win"})
    fig = px.line(
        calibration,
        x="mean_probability",
        y="observed_frequency",
        color="outcome",
        markers=True,
        facet_col="outcome",
        facet_col_spacing=0.08,
        title=f"Calibration curve: {MODEL_LABELS[model]}",
    )
    fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1, line={"color": "#92a6b5", "dash": "dash"})
    fig.update_layout(template="plotly_dark", paper_bgcolor="#07111d", plot_bgcolor="#0d1b2a", font_color="#eaf4f6", title_font_color="#eaf4f6", legend_font_color="#eaf4f6", xaxis_tickfont_color="#92a6b5", yaxis_tickfont_color="#92a6b5", showlegend=False)
    fig.update_xaxes(title="Mean predicted probability", range=[0, 1])
    fig.update_yaxes(title="Observed frequency", range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)
    st.info("Temperature scalers use temporally out-of-fold predictions from earlier seasons only. Curves use the held-out rows shown in the selected controls.")

with tab3:
    st.subheader("Dixon-Coles scoreline distribution")
    view = scorelines.query("home_goals <= 7 and away_goals <= 7").copy()
    view["forecast"] = view.predicted_probability * 100
    matrix = view.pivot(index="home_goals", columns="away_goals", values="forecast")
    fig = px.imshow(
        matrix,
        text_auto=".1f",
        color_continuous_scale="Viridis",
        labels={"x": "Away goals", "y": "Home goals", "color": "Forecast %"},
        title="Average held-out forecast mass (%)",
    )
    fig.update_layout(template="plotly_dark", paper_bgcolor="#07111d", plot_bgcolor="#0d1b2a", font_color="#eaf4f6", title_font_color="#eaf4f6", legend_font_color="#eaf4f6", xaxis_tickfont_color="#92a6b5", yaxis_tickfont_color="#92a6b5")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Whole-season forecast distribution averaged over held-out matches; the file includes empirical observed frequencies for comparison.")

with tab4:
    st.subheader("Data coverage")
    coverage = pd.DataFrame(audit["coverage_by_season"]).fillna(0).sort_values("season")
    value_vars = [x for x in ["Regular season", "Knockout"] if x in coverage]
    melted = coverage.melt(id_vars="season", value_vars=value_vars, var_name="match type", value_name="completed matches")
    fig = px.bar(melted, x="season", y="completed matches", color="match type", barmode="stack", title="ASA completed-match records by season")
    fig.update_layout(template="plotly_dark", paper_bgcolor="#07111d", plot_bgcolor="#0d1b2a", font_color="#eaf4f6", title_font_color="#eaf4f6", legend_font_color="#eaf4f6", xaxis_tickfont_color="#92a6b5", yaxis_tickfont_color="#92a6b5")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Source coverage:** {audit['regular_season_rows']:,} regular-season matches from {min(audit['seasons'])} to {max(audit['seasons'])}; {audit['knockout_rows_in_full_time_snapshot']:,} knockout rows excluded from the primary study.")
    st.markdown(f"**Verification status: {audit['verification']['status']}**")
    for item in audit["verification"]["checks"]:
        st.write(("✅ " if item["passed"] else "❌ ") + item["name"])
    st.warning("The API exposes current records and last_updated_utc, but no archived point-in-time versions. Historical source revisions therefore cannot be fully replayed.")
    st.caption("No market benchmark, betting return, arbitrage execution, or staking claim is included.")

st.divider()
st.markdown("#### Held-out matches")
columns = ["match_date_utc", "test_season", "home_team", "away_team", "home_score", "away_score", "outcome", "p_home", "p_draw", "p_away"]
st.dataframe(selected.sort_values("date_time_utc", ascending=False)[columns].head(150), use_container_width=True, hide_index=True)
st.caption("Data: American Soccer Analysis (ASA), CC BY-SA 4.0. Research snapshot retrieved 2026-11-26.")
