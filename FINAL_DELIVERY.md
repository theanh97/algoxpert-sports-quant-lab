# AlgoXpert Sports Quant Lab - Final Delivery

**Release:** MLS quantitative modeling v1.0  
**Owner:** Jack (Pham The Anh), AlgoXpert  
**Evidence snapshot retrieved:** 2026-11-26

## Delivery status

The core research release is implemented locally. **24 of 25 acceptance items are complete.** The dashboard was opened and checked in Chrome: changing the model updates the KPIs, selecting season 2024 shows 493 matches, and all four tabs load their data. The latest local HTTP check returned 200. A real dashboard screenshot was captured for visual review, but the attempt to transfer the image through a `data:` URL was blocked by browser policy, which permits only HTTP/HTTPS and explicitly prohibits workarounds. No screenshot file is included in the repository.

The repository was not published. No marketing copy was posted, and no paid service or data source was used.

## Experiment and actual results

- Source: American Soccer Analysis (ASA) public API, retrieved 2026-11-26; CC BY-SA 4.0.
- Snapshot: 5,998 completed records, 5,732 regular-season matches and 266 knockout records excluded from the primary study; seasons 2013-2026.
- Holdout: 2019-2026, annual expanding-window evaluation, 3,641 held-out matches per model. Each test season is excluded from fitting.
- The league-prior baseline had the lowest aggregate held-out log loss: **1.060926**; accuracy **47.10%**, multiclass Brier **0.640174**, ranked probability score **0.225163**.
- Every fitted model had higher aggregate log loss than the league prior in this sample. For raw Dixon-Coles and raw team logistic, the paired match-bootstrap 95% intervals for the log-loss difference were above zero. The other fitted-model intervals included zero. This is a negative result for the learned variants in this evaluation, not evidence of market advantage or future performance.

| Model | Log loss | Brier | Accuracy | Delta vs prior (95% CI) |
|---|---:|---:|---:|---:|
| League prior | 1.060926 | 0.640174 | 47.10% | 0.000000 |
| Elo, raw | 1.062701 | 0.640993 | 45.18% | +0.001775 [-0.007003, +0.010766] |
| Elo, temperature scaled | 1.063072 | 0.641303 | 45.18% | +0.002145 [-0.006598, +0.011322] |
| Dixon-Coles, temperature scaled | 1.063784 | 0.641576 | 46.44% | +0.002858 [-0.003812, +0.009396] |
| Team logistic, temperature scaled | 1.065287 | 0.642526 | 46.33% | +0.004361 [-0.002349, +0.010882] |
| Dixon-Coles, raw | 1.068677 | 0.644829 | 46.44% | +0.007751 [+0.000676, +0.014635] |
| Team logistic, raw | 1.076342 | 0.649086 | 46.33% | +0.015416 [+0.007539, +0.023242] |

The paired intervals are match-bootstrap intervals against the league-prior predictions. Metrics and full-precision values are in `artifacts/model_metrics.csv`; seasonal scores are in `artifacts/metrics_by_season.csv`.

## Verification and reproducibility

Verification status: **PASS**.

- Annual training cutoffs precede every held-out season; train and test game IDs are disjoint.
- Temperature calibration uses temporally prior out-of-fold predictions only.
- Predicted probabilities are in [0, 1] and sum to one; maximum absolute sum error is `2.22e-16`.
- Test scores are not supplied to predictors. Model settings are fixed in code and were not tuned on test seasons.
- Local verification run: `pytest -q` passed **6 tests**; `ruff check src tests` passed.
- Research run completed with `sports-quant run --eval-start-season 2019` using the checked-in ASA snapshots.

Run from the project root with Python 3.10 or newer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
sports-quant run --eval-start-season 2019
pytest -q
ruff check src tests
streamlit run dashboard.py
```

The checked-in raw snapshot makes the study runnable offline. Refreshing it requires network access: `sports-quant fetch --league mls`.

## Delivered artifacts

- Package, model code, evaluation, and CLI: `src/sports_quant_lab/`
- Dashboard source: `dashboard.py`
- Research notebook with saved results: `notebooks/01_mls_walk_forward.ipynb`
- Source snapshots and attribution: `data/raw/`, `data/README.md`
- Predictions and metrics: `artifacts/predictions.csv`, `artifacts/model_metrics.csv`, `artifacts/metrics_by_season.csv`
- Source audit, calibration folds, and scorelines: `artifacts/data_audit.json`, `artifacts/calibration_oof_predictions.csv`, `artifacts/scoreline_distribution.csv`
- Visual evidence: `artifacts/figures/` (portfolio cover, architecture, benchmark, calibration, scoreline, walk-forward, data coverage, verification report, portfolio collage)
- PDFs: `artifacts/reports/technical_research_report.pdf` (6 pages), `artifacts/reports/upwork_portfolio_case_study.pdf` (3 pages), `artifacts/reports/verification_report.pdf` (1 page)
- Marketing drafts: bilingual LinkedIn, Medium, Reddit, B2B outreach, and demo-video storyboard in `content/`
- Local SEO case study: `website/index.html`
- GitHub-facing docs and CI: `README.md`, `CODEX_HANDOFF.md`, `MARKETING_BRIEF.md`, `.github/workflows/ci.yml`

## Acceptance checklist

### Engineering

- [x] Python package
- [x] Results notebook
- [x] ASA data pipeline and audit
- [x] Statistical and machine-learning model benchmarks
- [x] Calibration and verification gates
- [x] Unit tests and GitHub Actions CI

### Visual evidence

- [x] Portfolio cover
- [x] Architecture diagram
- [ ] Screenshot of the rendered live dashboard
- [x] Model benchmark chart
- [x] Calibration curve
- [x] Scoreline distribution
- [x] Walk-forward visualization
- [x] Verification report
- [x] Data coverage chart
- [x] Portfolio collage

### Commercial assets

- [x] GitHub README
- [x] Technical research report PDF
- [x] Upwork portfolio case study PDF
- [x] LinkedIn drafts, English and Vietnamese
- [x] Medium article drafts, English and Vietnamese
- [x] Reddit drafts, English and Vietnamese
- [x] Website SEO case study
- [x] B2B outreach draft
- [x] Demo-video storyboard

## Limitations and next actions

- ASA provides current records and `last_updated_utc`, but not historical point-in-time versions. We cannot rule out all source-revision leakage.
- Whole-season holdouts do not simulate in-season updates; no lineups, injuries, player-level features, odds, closing-line value, betting ROI, or arbitrage execution are modeled.
- Football-Data was excluded after reviewing its free-data terms, which do not support commercial or automated model-training use.
- Dashboard visual and interaction checks passed in Chrome. The repository still needs `artifacts/figures/dashboard_screenshot.png`; browser policy blocked direct transfer of the captured image to a local file, and disallows an alternate route.
- Streamlit AppTest did not complete even with a 90-second timeout; a retry with a 10-second script timeout also remained inside `AppTest.run` and was interrupted. No passing AppTest result is claimed.
- Next: capture and inspect the dashboard from a permitted browser session, add the real screenshot to `artifacts/figures/`, then update this checklist. After that, a repository URL can be added before any external publication or portfolio posting.
