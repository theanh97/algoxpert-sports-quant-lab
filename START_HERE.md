# Start Here - AlgoXpert Sports Quant Lab

The MLS quantitative-modeling branch is implemented with real ASA data, a source audit, temporal model comparisons, prior-season calibration, dashboard, results notebook with saved outputs, CI, figures, and PDFs. Current verification status: **PASS**.

## First run
1. Install Python 3.10+.
2. Create/activate a virtual environment.
3. `python -m pip install -e .[dev]`
4. `sports-quant run` to recreate metrics, charts, reports, and marketing copy.
5. `pytest` and `ruff check src tests`.
6. `streamlit run dashboard.py` to explore the dashboard.

Refresh data separately with `sports-quant fetch --league mls`; it requires internet. The checked-in raw snapshot is available offline.

Start with `README.md`, `CODEX_HANDOFF.md`, `MARKETING_BRIEF.md`, `artifacts/reports/technical_research_report.pdf`, and `artifacts/reports/upwork_portfolio_case_study.pdf`.

This release excludes arbitrage execution, Redis, live data, odds, and publishing. ASA has no archived point-in-time versions; the reports state this limit.
