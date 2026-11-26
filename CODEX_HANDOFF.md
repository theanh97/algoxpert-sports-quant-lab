# CODEX_HANDOFF.md - AlgoXpert Sports Quant Lab v1.0

## Implementation status
Implemented the MLS quantitative-modeling branch from the supplied brief: Python package, ASA data fetch and audit, four model families, prior-only temperature scaling, annual walk-forward evaluation, tests/CI, dashboard, results notebook with saved outputs, technical and portfolio PDFs, visual evidence, and English/Vietnamese content drafts.

## Acceptance evidence
- Real data: 5,732 regular-season matches; source snapshot and SHA-256 hashes are included.
- Model outputs and metrics: `artifacts/predictions.csv`, `artifacts/model_metrics.csv`, and `artifacts/metrics_by_season.csv`.
- Verification: `PASS`; detailed checks at `artifacts/data_audit.json`.
- Visual and commercial assets: `artifacts/figures/`, `artifacts/reports/`, `content/`, and `website/index.html`.
- Market benchmark/ROI: not claimed because the permitted ASA data has no market prices. Football-Data free-data terms are unsuitable for commercial automated training use.
- Publication: not performed.

## System map
`data/pipeline.py` handles ASA snapshots and audit; `models/predictors.py` implements prior/Elo/logistic/Dixon-Coles/temperature scaling; `research.py` creates temporal folds; `evaluation.py` scores probabilities; `visuals.py`, `reports.py`, and `marketing.py` generate the evidence and assets; `dashboard.py` reads run artifacts.

## Reproduce
`python -m pip install -e .[dev]` -> `sports-quant run` -> `pytest` -> `ruff check src tests` -> `streamlit run dashboard.py`.

## Limits
ASA does not expose archived point-in-time versions; historical source revision cannot be ruled out. Whole-season forecasts do not simulate in-season updates. Odds, execution, Redis, and public deployment remain outside this release.
