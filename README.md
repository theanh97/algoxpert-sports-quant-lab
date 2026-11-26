# AlgoXpert Sports Quant Lab

**AlgoXpert Research Initiative | MLS case study | Reproducible probability research**

**Public repository:** [github.com/theanh97/algoxpert-sports-quant-lab](https://github.com/theanh97/algoxpert-sports-quant-lab) (`main`)

This research release compares transparent three-way match probability models, checks calibration, and makes data lineage, temporal splits, uncertainty, and limitations inspectable. It is not a betting product.

## Current evidence
- ASA snapshot retrieved: **2026-11-26** (American Soccer Analysis, CC BY-SA 4.0)
- Source coverage: **5,732 regular-season matches**, seasons 2013-2026
- Test seasons: **2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026** (annual expanding-window holdouts)
- Lowest aggregate held-out log loss: **League prior, 1.0609** over 3,641 matches
- Paired bootstrap delta vs league prior: **+0.0000** (95% interval +0.0000 to +0.0000)
- Verification gates: **PASS**

This is a historical sample result, not a claim of a durable future edge. ASA does not provide point-in-time historical versions, and the report states that limit. No odds benchmark, market outperformance, betting ROI, or arbitrage claim is included.

## Models and validation
- League outcome-frequency prior
- Elo ratings with fixed home advantage
- Regularized multinomial logistic regression over pre-match home/away team IDs
- Regularized Dixon-Coles goal model with a low-score correction
- Raw and prior-season out-of-fold temperature-scaled forecasts

Each complete test season is excluded from fitting. Calibration uses only temporally prior out-of-fold predictions. Scores include log loss, multiclass Brier score, ranked probability score, accuracy, calibration error, goal MAE/NLL, and paired match-bootstrap intervals.

## Reproduce locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
sports-quant run
pytest
ruff check src tests
streamlit run dashboard.py
```

Refresh data (internet required) with `sports-quant fetch --league mls`; then run `sports-quant run`. The checked-in raw snapshot keeps this study reproducible offline. Use `sports-quant audit` to inspect the source counts and hashes.

## Evidence files
- `artifacts/model_metrics.csv`, `artifacts/metrics_by_season.csv`, `artifacts/predictions.csv`
- `artifacts/data_audit.json`, `artifacts/calibration_oof_predictions.csv`, `artifacts/scoreline_distribution.csv`
- `artifacts/figures/` (cover, architecture, benchmark, calibration, scoreline, walk-forward, coverage, verification, collage)
- `artifacts/reports/technical_research_report.pdf`, `upwork_portfolio_case_study.pdf`, `verification_report.pdf`
- `notebooks/01_mls_walk_forward.ipynb` (result notebook with saved outputs)
- `content/` (English/Vietnamese LinkedIn, Medium, Reddit, outreach, and demo storyboard)
- `website/index.html` (local SEO case study)

## Data and license
The raw files are American Soccer Analysis API data under **CC BY-SA 4.0**. Attribute ASA and preserve share-alike for the data and adaptations. The project code is MIT licensed; see `data/README.md` and `LICENSE`. Football-Data is not used because its current public free-data terms exclude commercial and automated training-product use.

## Limitations
- Current ASA records include `last_updated_utc`, but no point-in-time history. Historical source revisions cannot be ruled out.
- Whole-season forecasts do not simulate in-season updates and use no lineup, injury, travel, player-level, or market data.
- Better scores in this sample do not show future profit or market inefficiency.

## References
- ASA API: https://app.americansocceranalysis.com/api/v1/openapi.json
- Dixon and Coles (1997), DOI: https://doi.org/10.1111/1467-9876.00065
- scikit-learn probability calibration: https://scikit-learn.org/stable/modules/calibration.html
- Football-Data terms (reviewed, not used): https://football-data.co.uk/data.php

Draft marketing assets are not published. Editorially review all copy before posting.
