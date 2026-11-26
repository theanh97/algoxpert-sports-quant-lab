import numpy as np
import pandas as pd

from sports_quant_lab.models.predictors import (
    DixonColesModel,
    TemperatureScaler,
    elo_team_model,
    league_prior,
    logistic_team_model,
)


def sample_matches():
    rows = []
    teams = ["A", "B", "C", "D"]
    results = [(1, 0), (0, 0), (0, 2), (2, 1), (1, 1), (0, 1), (3, 0), (1, 2)]
    for i in range(32):
        home = teams[i % 4]
        away = teams[(i + 1 + (i // 4) % 3) % 4]
        if home == away:
            away = teams[(teams.index(home) + 1) % 4]
        hg, ag = results[i % len(results)]
        rows.append(
            {
                "game_id": str(i),
                "date_time_utc": pd.Timestamp("2020-01-01", tz="UTC") + pd.Timedelta(days=i),
                "season": 2018 + i // 12,
                "home_team_id": home,
                "away_team_id": away,
                "home_score": hg,
                "away_score": ag,
                "outcome": "H" if hg > ag else "A" if hg < ag else "D",
            }
        )
    return pd.DataFrame(rows)


def test_baseline_elo_and_logistic_return_probabilities():
    data = sample_matches()
    train, test = data.iloc[:24], data.iloc[24:]
    for probabilities in (
        league_prior(train, test),
        elo_team_model(train, test),
        logistic_team_model(train, test),
    ):
        assert probabilities.shape == (len(test), 3)
        assert np.all(probabilities >= 0)
        np.testing.assert_allclose(probabilities.sum(axis=1), 1.0, atol=1e-10)


def test_dixon_coles_returns_score_and_outcome_distributions():
    data = sample_matches()
    train, test = data.iloc[:24], data.iloc[24:]
    model = DixonColesModel(maxiter=300).fit(train)
    probabilities, home_rate, away_rate, matrices = model.predict_proba(test)
    assert probabilities.shape == (len(test), 3)
    assert matrices.shape == (len(test), 11, 11)
    np.testing.assert_allclose(probabilities.sum(axis=1), 1.0, atol=1e-10)
    np.testing.assert_allclose(matrices.sum(axis=(1, 2)), 1.0, atol=1e-10)
    assert (home_rate > 0).all() and (away_rate > 0).all()


def test_temperature_scaler_preserves_probability_simplex():
    data = sample_matches()
    train = data.iloc[:24]
    raw = logistic_team_model(train, data.iloc[24:])
    scaler = TemperatureScaler().fit(raw, data.iloc[24:].outcome)
    calibrated = scaler.transform(raw)
    assert scaler.temperature_ > 0
    assert np.all(calibrated >= 0)
    np.testing.assert_allclose(calibrated.sum(axis=1), 1.0, atol=1e-10)

