"""Generate portable, evidence-backed research and portfolio PDFs."""

from __future__ import annotations

from html import escape

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from sports_quant_lab.constants import FIGURES_DIR, REPORTS_DIR
from sports_quant_lab.research import MODEL_LABELS

NAVY = colors.HexColor("#0B1825")
TEAL = colors.HexColor("#0B9F86")
PALE = colors.HexColor("#EAF4F6")
MID = colors.HexColor("#587080")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=27, leading=31, textColor=NAVY, alignment=TA_LEFT, spaceAfter=10),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=12, leading=17, textColor=MID, spaceAfter=10),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=2, spaceAfter=10),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=TEAL, spaceBefore=10, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["BodyText"], fontSize=9.3, leading=14, textColor=NAVY, spaceAfter=7),
        "small": ParagraphStyle("small", parent=base["BodyText"], fontSize=7.5, leading=10, textColor=MID, spaceAfter=4),
        "kpi": ParagraphStyle("kpi", parent=base["BodyText"], fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=NAVY, alignment=TA_CENTER),
        "kpi_label": ParagraphStyle("kpi_label", parent=base["BodyText"], fontSize=7.6, leading=10, textColor=MID, alignment=TA_CENTER),
        "center": ParagraphStyle("center", parent=base["BodyText"], fontSize=9, leading=12, textColor=MID, alignment=TA_CENTER),
    }


def _page(canvas, doc):
    canvas.saveState()
    width, _ = letter
    canvas.setStrokeColor(colors.HexColor("#D5E2E8"))
    canvas.setLineWidth(0.5)
    canvas.line(0.65 * inch, 0.52 * inch, width - 0.65 * inch, 0.52 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MID)
    canvas.drawString(0.65 * inch, 0.34 * inch, "AlgoXpert Sports Quant Lab | MLS Case Study")
    canvas.drawRightString(width - 0.65 * inch, 0.34 * inch, f"{doc.page}")
    canvas.restoreState()


def _image(name: str, width: float = 7.0 * inch, height: float = 3.8 * inch) -> Image:
    image = Image(str(FIGURES_DIR / f"{name}.png"))
    ratio = image.imageWidth / image.imageHeight
    if width / height > ratio:
        image.drawHeight = height
        image.drawWidth = height * ratio
    else:
        image.drawWidth = width
        image.drawHeight = width / ratio
    image.hAlign = "CENTER"
    return image


def _p(text: str, style):
    return Paragraph(text, style)


def _metric_table(metrics: pd.DataFrame, styles: dict) -> Table:
    frame = metrics.sort_values("log_loss")
    header = ["Model", "N", "Log loss", "Brier", "Accuracy", "ECE"]
    rows = [header]
    for item in frame.itertuples():
        rows.append(
            [
                MODEL_LABELS.get(item.model, item.model),
                f"{int(item.n_matches):,}",
                f"{item.log_loss:.4f}",
                f"{item.brier:.4f}",
                f"{item.accuracy:.1%}",
                f"{item.top_label_ece_10:.3f}",
            ]
        )
    table = Table(rows, colWidths=[2.08 * inch, 0.53 * inch, 0.84 * inch, 0.75 * inch, 0.8 * inch, 0.62 * inch], repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
                ("TEXTCOLOR", (0, 1), (-1, -1), NAVY),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, 0), 0.7, TEAL),
            ]
        )
    )
    return table


def _kpis(metrics: pd.DataFrame, audit: dict, styles: dict) -> Table:
    best = metrics.sort_values("log_loss").iloc[0]
    values = [
        (f"{int(audit['regular_season_rows']):,}", "REGULAR-SEASON MATCHES"),
        (f"{len(audit['seasons'])}", "COVERED SEASONS"),
        (f"{best.log_loss:.3f}", f"BEST HOLDOUT LOG LOSS\n{best.display_name}"),
        (audit["verification"]["status"], "VERIFICATION GATES"),
    ]
    cards = []
    for value, label in values:
        card = Table([[Paragraph(value, styles["kpi"])], [Paragraph(label, styles["kpi_label"]) ]], colWidths=[1.65 * inch], rowHeights=[0.36 * inch, 0.4 * inch])
        card.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CADCE4")), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        cards.append(card)
    row = Table([cards], colWidths=[1.75 * inch] * 4)
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]))
    return row


def _technical_pdf(metrics: pd.DataFrame, by_season: pd.DataFrame, audit: dict, path) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=0.68 * inch, leftMargin=0.68 * inch, topMargin=0.62 * inch, bottomMargin=0.7 * inch, title="AlgoXpert Sports Quant Lab - MLS Research Report", author="AlgoXpert")
    story = []
    story += [_p("ALGOXPERT  /  SPORTS QUANT LAB", styles["h2"]), _p("MLS probability research", styles["title"]), _p("Technical research report | Research release v1.0 | Retrieved 2026-11-26", styles["subtitle"]), _image("portfolio_cover", 7.0 * inch, 3.0 * inch), Spacer(1, 0.12 * inch), _kpis(metrics, audit, styles), Spacer(1, 0.2 * inch)]
    best = metrics.sort_values("log_loss").iloc[0]
    story.append(_p("Research question", styles["h2"]))
    story.append(_p("Can transparent team-strength and goal models produce useful three-way MLS probabilities under a strict season-level walk-forward evaluation? This release benchmarks historical outcome frequencies, Elo, regularized team-identity logistic regression, and a Dixon-Coles score model. The target is the home/draw/away result; no betting edge or future performance claim is made.", styles["body"]))
    story.append(_p("Headline result", styles["h2"]))
    fitted = metrics.loc[metrics.model != "league_prior"]
    worse_count = int((fitted.log_loss > best.log_loss).sum())
    significant = fitted.loc[fitted.bootstrap_delta_log_loss_ci95_low > 0, "display_name"].tolist()
    interval_note = "Paired intervals above zero for " + ", ".join(significant) + "." if significant else "No paired interval excluded zero."
    story.append(_p(f"The lowest aggregate held-out log loss was {escape(str(best.display_name))} at {best.log_loss:.4f} over {int(best.n_matches):,} matches. Its paired match-bootstrap difference from the league-prior baseline was {best.bootstrap_delta_log_loss_vs_prior:+.4f} (95% interval {best.bootstrap_delta_log_loss_ci95_low:+.4f} to {best.bootstrap_delta_log_loss_ci95_high:+.4f}). All {worse_count} fitted variants had higher aggregate log loss than the prior; {interval_note} Treat this as evidence about this sample, not proof of a durable advantage.", styles["body"]))
    story.append(PageBreak())
    story.append(_p("Aggregate model benchmark", styles["h1"]))
    story.append(_metric_table(metrics, styles))
    story.append(Spacer(1, 0.12 * inch))
    story.append(_p("Log loss and multiclass Brier score are proper probability scores; lower is better. Accuracy is a hard top-class hit rate and is not a substitute for probability quality. ECE uses ten fixed top-confidence bins and is sensitive to binning choices.", styles["small"]))
    story.append(_image("model_benchmark", 7.0 * inch, 3.7 * inch))
    story.append(PageBreak())

    story.append(_p("01  Data and scope", styles["h1"]))
    story.append(_p(f"Source: American Soccer Analysis public API, retrieved {audit['retrieved_utc']}. The raw snapshot contains {audit['raw_rows']:,} completed records spanning {audit['first_match_utc'][:10]} to {audit['last_match_utc'][:10]}. The experiment retains {audit['regular_season_rows']:,} regular-season matches, excludes {audit['knockout_rows_in_full_time_snapshot']:,} records flagged as knockout games, and covers seasons {min(audit['seasons'])}-{max(audit['seasons'])}.", styles["body"]))
    story.append(_p("Data by American Soccer Analysis; API data are licensed under CC BY-SA 4.0. The raw JSON snapshots and SHA-256 hashes are included with this release. The source API provides completed scores and team IDs, not point-in-time pre-match odds. Football-Data was excluded because its public free-data terms restrict use to private individuals and disallow commercial use and automated data-training products.", styles["body"]))
    story.append(_p("Source links", styles["h2"]))
    story.append(_p('<link href="https://app.americansocceranalysis.com/api/v1/openapi.json" color="#0B9F86">ASA API documentation and license</link>  |  <link href="https://football-data.co.uk/data.php" color="#0B9F86">Football-Data usage terms</link>  |  <link href="https://doi.org/10.1111/1467-9876.00065" color="#0B9F86">Dixon and Coles (1997)</link>', styles["body"]))
    story.append(_image("data_coverage", 7.0 * inch, 3.4 * inch))
    story.append(Spacer(1, 0.1 * inch))
    story.append(_p(f"SHA-256: matches `{audit['games_sha256']}`; team map `{audit['teams_sha256']}`. See `data/README.md` for attribution and redistribution terms.", styles["small"]))
    story.append(_p("Methods reference", styles["h2"]))
    story.append(_p("Dixon, M.J. and Coles, S.G. (1997). Modelling association football scores and inefficiencies in the football betting market. Journal of the Royal Statistical Society: Series C, 46(2), 265-280. DOI: 10.1111/1467-9876.00065. This release implements a regularized static team-strength adaptation; it does not reproduce the original dynamic weighting or test its betting-market result.", styles["small"]))
    story.append(PageBreak())

    story.append(_p("02  Research design", styles["h1"]))
    story.append(_p("Annual expanding-window holdout: each test season is predicted using only earlier seasons, and every match in a test season is held out together. Test seasons are " + ", ".join(map(str, audit["evaluation"]["test_seasons"])) + ". The fixed model settings are in the source code; no hyperparameter selection used these test seasons.", styles["body"]))
    story.append(_p("Models", styles["h2"]))
    story.append(_p("League prior forecasts the training-set outcome frequencies. Elo updates team ratings only on training matches. Logistic regression uses one-hot pre-match home and away team IDs. The Dixon-Coles model estimates regularized team attack and defence effects and applies a low-score adjustment to the independent-Poisson score distribution. All models produce H/D/A probabilities.", styles["body"]))
    story.append(_p("Calibration", styles["h2"]))
    story.append(_p("Temperature scaling is fit to temporally out-of-fold predictions from earlier seasons only. For each outer test season, the calibrator's latest training season precedes that test season. Raw and calibrated variants are both reported. Reliability curves use one-vs-rest bins for each outcome class.", styles["body"]))
    story.append(_image("architecture_diagram", 7.0 * inch, 3.0 * inch))
    story.append(_p("Verification gates", styles["h2"]))
    story.append(_p(f"Status: {audit['verification']['status']}. The run checks season cutoffs, game-ID separation, prior-only calibration, probability bounds and sums, and excludes test scores from predictors. Full evidence is in `artifacts/data_audit.json`.", styles["body"]))
    story.append(PageBreak())

    story.append(_p("03  Results and diagnostics", styles["h1"]))
    story.append(_p("Season-by-season log loss and reliability diagnostics", styles["h2"]))
    story.append(_image("walk_forward", 7.0 * inch, 3.4 * inch))
    story.append(Spacer(1, 0.08 * inch))
    story.append(_image("calibration_curve", 7.0 * inch, 3.0 * inch))
    story.append(PageBreak())
    story.append(_p("04  Scoreline distribution", styles["h1"]))
    story.append(_image("score_distribution", 7.0 * inch, 4.1 * inch))
    story.append(_p("The scoreline chart compares mean Dixon-Coles forecast mass with empirical held-out score frequencies. Cells above the display cap are omitted from the chart, while probabilities were normalized over the model's 0-10 goal grid.", styles["small"]))
    dc = metrics.loc[metrics.model.eq("dixon_coles_temp")].iloc[0]
    story.append(_p(f"Dixon-Coles temperature-scaled goal diagnostics: home goals MAE {dc.home_goal_mae:.3f}; away goals MAE {dc.away_goal_mae:.3f}; home/away Poisson negative log likelihood {dc.home_goal_poisson_nll:.3f}/{dc.away_goal_poisson_nll:.3f} per team score.", styles["body"]))

    story.append(_p("05  Limitations and reproducibility", styles["h1"]))
    limitations = [
        "The public API exposes current records with last_updated_utc but no historical versions. We can verify that only earlier-season outcomes enter each fold, but cannot certify that every historical value was available unchanged at the original cutoff.",
        "Whole-season forecasts do not simulate in-season updates, roster changes, injuries, lineups, travel, or schedule congestion.",
        "Only results and team identifiers are modeled. No market odds, closing-line value, betting return, arbitrage execution, or financial value is evaluated.",
        "ASA coverage and data definitions can change; rerun the audit after each snapshot. Team identities and expansion history may require league-specific mapping when porting the pipeline.",
        "This is research software, not a betting recommendation or guarantee of future forecast quality.",
    ]
    for item in limitations:
        story.append(_p("- " + escape(item), styles["body"]))
    story.append(_p("Reproduce", styles["h2"]))
    story.append(_p("1. `python -m venv .venv`<br/>2. `python -m pip install -e .[dev]`<br/>3. `sports-quant run`<br/>4. `pytest` and `ruff check src tests`<br/>5. `streamlit run dashboard.py`", styles["body"]))
    story.append(_p("Artifacts", styles["h2"]))
    story.append(_p("Predictions and scores: `artifacts/predictions.csv`, `artifacts/model_metrics.csv`, `artifacts/metrics_by_season.csv`. Data audit and verification: `artifacts/data_audit.json`. Visual evidence: `artifacts/figures/`. Notebook: `notebooks/01_mls_walk_forward.ipynb`.", styles["body"]))
    doc.build(story, onFirstPage=_page, onLaterPages=_page)


def _portfolio_pdf(metrics: pd.DataFrame, by_season: pd.DataFrame, audit: dict, path) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=0.68 * inch, leftMargin=0.68 * inch, topMargin=0.62 * inch, bottomMargin=0.7 * inch, title="AlgoXpert MLS Quant Research Portfolio Case Study", author="AlgoXpert")
    story = [
        _p("ALGOXPERT  /  SPORTS QUANT LAB", styles["h2"]),
        _p("MLS probability research with evidence gates", styles["title"]),
        _p("Portfolio case study | Research release v1.0", styles["subtitle"]),
        _image("portfolio_cover", 7.0 * inch, 3.45 * inch),
        Spacer(1, 0.15 * inch),
        _kpis(metrics, audit, styles),
        Spacer(1, 0.18 * inch),
        _p("The challenge", styles["h2"]),
        _p("Sports forecasting demos often show a hit rate without testing whether probabilities are reliable or whether a historical split leaks future information. This MLS case study turns the problem into a repeatable research workflow: source lineage, held-out seasons, multiple baselines, calibrated probabilities, and visible limitations.", styles["body"]),
        _p("What was built", styles["h2"]),
        _p("Python package and data audit; league-prior, Elo, multinomial team logistic, and Dixon-Coles models; temporal out-of-fold temperature scaling; Streamlit research dashboard; results notebook with saved outputs; CI workflow; technical report; and marketing-ready evidence assets.", styles["body"]),
        PageBreak(),
        _p("Experimental evidence", styles["h1"]),
        _p(f"ASA snapshot retrieved {audit['retrieved_utc']}: {audit['regular_season_rows']:,} regular-season matches, seasons {min(audit['seasons'])}-{max(audit['seasons'])}. Outer test seasons: {', '.join(map(str, audit['evaluation']['test_seasons']))}. Each entire test season is held out while models and calibrators use earlier data only.", styles["body"]),
        _metric_table(metrics, styles),
        Spacer(1, 0.08 * inch),
        _p("The league prior remained the lowest-log-loss model; learned variants did not improve on it in this sample. The paired bootstrap interval, per-season performance, and calibration plots are included for inspection.", styles["small"]),
        _image("model_benchmark", 7.0 * inch, 3.65 * inch),
        PageBreak(),
        _p("Verification and delivery", styles["h1"]),
        _image("verification_report", 7.0 * inch, 3.25 * inch),
        _p("Evidence gates check temporal cutoffs, disjoint game IDs, prior-only calibrator training, valid probability ranges, and sum-to-one outputs. The API does not provide point-in-time record history, so revision leakage cannot be ruled out completely.", styles["body"]),
        _image("walk_forward", 7.0 * inch, 3.4 * inch),
        _p("Source: American Soccer Analysis API, CC BY-SA 4.0. Code: MIT. No market-odds benchmark or betting-return claim is included. Full reproducibility commands and limitations are in the repository README and technical report.", styles["small"]),
    ]
    doc.build(story, onFirstPage=_page, onLaterPages=_page)


def _verification_pdf(audit: dict, path) -> None:
    styles = _styles()
    doc = SimpleDocTemplate(str(path), pagesize=letter, rightMargin=0.68 * inch, leftMargin=0.68 * inch, topMargin=0.62 * inch, bottomMargin=0.7 * inch, title="AlgoXpert Verification Report", author="AlgoXpert")
    header = ParagraphStyle("table_header", parent=styles["small"], fontName="Helvetica-Bold", textColor=colors.white, spaceAfter=0)
    cell = ParagraphStyle("table_cell", parent=styles["small"], fontSize=7.4, leading=9, textColor=NAVY, spaceAfter=0)
    data = [[Paragraph("Check", header), Paragraph("Result", header), Paragraph("Evidence", header)]]
    for check in audit["verification"]["checks"]:
        detail = str(check.get("detail", check.get("max_abs_error", "")))
        data.append([Paragraph(escape(check["name"]), cell), Paragraph("PASS" if check["passed"] else "FAIL", cell), Paragraph(escape(detail), cell)])
    table = Table(data, colWidths=[2.3 * inch, 0.7 * inch, 3.8 * inch], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8), ("VALIGN", (0, 0), (-1, -1), "TOP"), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#cadce4")), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    story = [_p("AlgoXpert Sports Quant Lab", styles["h2"]), _p(f"Verification report: {audit['verification']['status']}", styles["title"]), _p("Generated from the run manifest and held-out predictions.", styles["subtitle"]), table, Spacer(1, 0.2 * inch), _image("verification_report", 7.0 * inch, 3.7 * inch), _p("Known limit: the ASA endpoint returns current records and last_updated_utc, but no archived point-in-time snapshots. Therefore historical source revisions cannot be independently replayed.", styles["body"])]
    doc.build(story, onFirstPage=_page, onLaterPages=_page)


def generate_reports(matches: pd.DataFrame, predictions: pd.DataFrame, metrics: pd.DataFrame, by_season: pd.DataFrame, audit: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    _technical_pdf(metrics, by_season, audit, REPORTS_DIR / "technical_research_report.pdf")
    _portfolio_pdf(metrics, by_season, audit, REPORTS_DIR / "upwork_portfolio_case_study.pdf")
    _verification_pdf(audit, REPORTS_DIR / "verification_report.pdf")

