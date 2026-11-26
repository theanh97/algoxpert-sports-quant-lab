# Reddit draft (EN)

I built a reproducible MLS 1X2 probability study: 5,732 regular-season results from ASA (CC BY-SA 4.0), tested on seasons 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. It compares a league prior, Elo, team-ID logistic regression, and regularized Dixon-Coles. Temperature scaling sees temporal OOF forecasts from earlier seasons only.

League prior recorded the lowest aggregate held-out log loss in this run: 1.0609 over 3,641 matches in test seasons 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Its paired match-bootstrap difference versus the league-prior baseline was +0.0000 (95% interval +0.0000 to +0.0000). All 6 fitted variants had higher aggregate log loss than the league prior. Paired 95% intervals exclude zero for Dixon-Coles (raw), Team logistic (raw).  This is a historical sample result, not a claim of durable future edge, market outperformance, or betting profitability.

The release includes source snapshots and hashes, an audit, per-season metrics, calibration and scoreline charts, a results notebook with saved outputs, dashboard, tests, and PDFs. I did not add odds: ASA has no market prices, and the public free-data terms for Football-Data do not fit this commercial training project. No ROI claim.

The important caveat is that ASA returns current records and `last_updated_utc`, not archived versions. The time split is explicit, but historical revision cannot be fully ruled out. I would value feedback on calibration, handling team expansion/relocation, or a market-data source with clear commercial rights.

[Repository link to add after publication]
