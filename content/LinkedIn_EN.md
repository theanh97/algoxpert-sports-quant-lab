# LinkedIn post (EN)

A prediction model is only interesting when its probabilities survive a time-respecting test.

League prior recorded the lowest aggregate held-out log loss in this run: 1.0609 over 3,641 matches in test seasons 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026. Its paired match-bootstrap difference versus the league-prior baseline was +0.0000 (95% interval +0.0000 to +0.0000). All 6 fitted variants had higher aggregate log loss than the league prior. Paired 95% intervals exclude zero for Dixon-Coles (raw), Team logistic (raw).  This is a historical sample result, not a claim of durable future edge, market outperformance, or betting profitability.

AlgoXpert Sports Quant Lab is an MLS research release built on 5,732 regular-season results from American Soccer Analysis (2013-2026 source coverage). It compares a league prior, Elo, team-identity logistic regression, and a Dixon-Coles goal model. Temperature scaling uses prior-season out-of-fold forecasts. The run checks temporal cutoffs, game-ID separation, probability bounds, and calibration.

The source snapshot has results but no timestamped market prices. The API also lacks archived point-in-time revisions. I make no market-edge, ROI, or arbitrage claim.

Code, audit, dashboard, notebook, reports, and charts: [repository link to add after publication].

#SportsAnalytics #QuantResearch #ProbabilityCalibration #MLS
