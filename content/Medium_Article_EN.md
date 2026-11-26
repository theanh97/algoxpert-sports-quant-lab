# A reproducible MLS forecasting benchmark starts with probability

Sports forecasting demos often lead with a hit rate. That number is easy to read, but it does not show whether a model's 70% forecasts happen about 70% of the time or whether future information leaked into testing.

AlgoXpert Sports Quant Lab makes those checks part of the research release.

## Data and boundaries

The case study uses 5,732 MLS regular-season results from American Soccer Analysis, with source coverage from 2013 through 2026. The API states that returned data are CC BY-SA 4.0, so the repository includes attribution and preserves share-alike for the data. The primary experiment excludes 266 records flagged as knockout games.

The snapshot contains scores and team identifiers, but no timestamped pre-match odds. Football-Data is not substituted: its current free-data terms restrict use to private individuals and exclude commercial use and automated data-training products. There is no market benchmark or betting-return claim.

## A time-respecting comparison

Each test season is held out as a whole. Models train only on earlier seasons: a league-frequency prior, Elo ratings, regularized team-identity logistic regression, and a Dixon-Coles goal model. Temperature scaling is fit on temporal out-of-fold forecasts from prior seasons. We report log loss, multiclass Brier score, ranked probability score, accuracy, calibration diagnostics, and paired bootstrap intervals against the league prior.

## What this run found

League prior recorded the lowest aggregate held-out log loss in this run: 1.0609 over 3,641 matches in test seasons 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Its paired match-bootstrap difference versus the league-prior baseline was +0.0000 (95% interval +0.0000 to +0.0000). All 6 fitted variants had higher aggregate log loss than the league prior. Paired 95% intervals exclude zero for Dixon-Coles (raw), Team logistic (raw).  This is a historical sample result, not a claim of durable future edge, market outperformance, or betting profitability.

That is a sample result, not a forecast of future performance. Per-season charts and calibration plots make variation visible alongside the aggregate score.

## What remains uncertain

ASA exposes `last_updated_utc` but no archived point-in-time versions. The split proves only earlier-season rows enter each fold; it cannot prove every historical record was unchanged at the original cutoff. Annual holdouts also do not simulate in-season updates, lineups, injuries, travel, or roster changes.

The release includes raw snapshots and hashes, an audit, Python package, results notebook with saved outputs, Streamlit dashboard, CI, figures, and PDF reports. Reproduce with `python -m pip install -e .[dev]`, `sports-quant run`, and `pytest`.

The goal is a result another analyst can inspect, challenge, and rerun.
