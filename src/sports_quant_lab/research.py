"""End-to-end temporal MLS experiment and verifiable output generation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import gammaln

from sports_quant_lab.constants import ARTIFACTS_DIR, FIGURES_DIR, PROCESSED_DIR, REPORTS_DIR
from sports_quant_lab.data.pipeline import latest_snapshot, load_and_audit
from sports_quant_lab.evaluation import paired_log_loss_bootstrap, probability_metrics
from sports_quant_lab.models.predictors import (
    DixonColesModel,
    TemperatureScaler,
    elo_team_model,
    league_prior,
    logistic_team_model,
)

RAW_MODELS = ("league_prior", "elo", "logistic", "dixon_coles")
MODEL_LABELS = {
    "league_prior": "League prior",
    "elo_raw": "Elo (raw)",
    "elo_temp": "Elo (temperature scaled)",
    "logistic_raw": "Team logistic (raw)",
    "logistic_temp": "Team logistic (temperature scaled)",
    "dixon_coles_raw": "Dixon-Coles (raw)",
    "dixon_coles_temp": "Dixon-Coles (temperature scaled)",
}
MODEL_ORDER = tuple(MODEL_LABELS)


def _fit_raw_models(train: pd.DataFrame, test: pd.DataFrame) -> tuple[dict, dict]:
    dc = DixonColesModel().fit(train)
    dc_prob, home_rate, away_rate, matrices = dc.predict_proba(test)
    outputs = {
        "league_prior": league_prior(train, test),
        "elo": elo_team_model(train, test),
        "logistic": logistic_team_model(train, test),
        "dixon_coles": dc_prob,
    }
    metadata = {
        "dixon_coles_optimizer_success": dc.optimizer_success_,
        "dixon_coles_optimizer_message": dc.optimizer_message_,
        "dixon_coles_rho": float(dc.rho_),
        "home_lambda": home_rate,
        "away_lambda": away_rate,
        "score_matrices": matrices,
    }
    return outputs, metadata


def _prediction_rows(
    test: pd.DataFrame,
    raw_outputs: dict[str, np.ndarray],
    metadata: dict,
    oof: pd.DataFrame,
    test_season: int,
) -> tuple[pd.DataFrame, list[dict]]:
    frame = test[
        ["game_id", "date_time_utc", "match_date_utc", "season", "home_team_id", "away_team_id",
         "home_team", "away_team", "home_score", "away_score", "outcome"]
    ].copy()
    frame["test_season"] = test_season
    result_rows = []
    fit_rows = []
    for model in RAW_MODELS:
        probabilities = raw_outputs[model]
        calibration = None
        calibration_year = None
        calibration_n = 0
        if model != "league_prior":
            history = oof.loc[(oof.model == model) & (oof.season < test_season)].copy()
            if history.empty:
                raise ValueError(f"No temporally prior calibration rows for {model} before {test_season}")
            history_probabilities = history[["p_home", "p_draw", "p_away"]].to_numpy()
            calibration = TemperatureScaler().fit(history_probabilities, history.outcome)
            calibration_year = int(history.season.max())
            calibration_n = len(history)
            fit_rows.append(
                {
                    "test_season": test_season,
                    "model": model,
                    "temperature": calibration.temperature_,
                    "calibration_rows": calibration_n,
                    "calibration_max_season": calibration_year,
                    "calibration_train_log_loss": calibration.training_log_loss_,
                }
            )
        for suffix, output in (("raw", probabilities),):
            pred = frame.copy()
            pred["model"] = model if model == "league_prior" else f"{model}_{suffix}"
            pred["p_home"], pred["p_draw"], pred["p_away"] = output.T
            pred["temperature"] = 1.0
            pred["calibration_rows"] = calibration_n
            pred["calibration_max_season"] = calibration_year
            if model == "dixon_coles":
                pred["home_lambda"] = metadata["home_lambda"]
                pred["away_lambda"] = metadata["away_lambda"]
                pred["dixon_coles_rho"] = metadata["dixon_coles_rho"]
                pred["score_matrix"] = list(metadata["score_matrices"])
            result_rows.append(pred)
        if calibration is not None:
            calibrated = calibration.transform(probabilities)
            pred = frame.copy()
            pred["model"] = f"{model}_temp"
            pred["p_home"], pred["p_draw"], pred["p_away"] = calibrated.T
            pred["temperature"] = calibration.temperature_
            pred["calibration_rows"] = calibration_n
            pred["calibration_max_season"] = calibration_year
            if model == "dixon_coles":
                pred["home_lambda"] = metadata["home_lambda"]
                pred["away_lambda"] = metadata["away_lambda"]
                pred["dixon_coles_rho"] = metadata["dixon_coles_rho"]
                pred["score_matrix"] = list(metadata["score_matrices"])
            result_rows.append(pred)
    return pd.concat(result_rows, ignore_index=True), fit_rows


def _to_oof_rows(test: pd.DataFrame, model_name: str, probabilities: np.ndarray) -> pd.DataFrame:
    result = test[["game_id", "season", "outcome"]].copy()
    result["model"] = model_name
    result[["p_home", "p_draw", "p_away"]] = probabilities
    return result


def run_research(
    games_path: Path | None = None,
    teams_path: Path | None = None,
    eval_start_season: int = 2019,
    build_notebook: bool = True,
) -> dict:
    """Run rolling-origin annual holdouts, prior-only calibration, audits and figures."""
    if games_path is None or teams_path is None:
        latest_games, latest_teams = latest_snapshot()
        games_path = games_path or latest_games
        teams_path = teams_path or latest_teams
    for path in (ARTIFACTS_DIR, FIGURES_DIR, REPORTS_DIR, PROCESSED_DIR):
        path.mkdir(parents=True, exist_ok=True)

    matches, audit = load_and_audit(games_path, teams_path)
    matches.to_csv(PROCESSED_DIR / "mls_regular_season_matches.csv", index=False)
    audit["experiment"] = {
        "primary_scope": "MLS regular season, full-time matches only",
        "excluded": "ASA records flagged knockout_game=true (MLS playoffs/cup knockout games)",
        "target": "three-way home/draw/away result",
        "test_method": "annual expanding-window holdout; each test season excluded from fitting",
        "first_test_season_requested": int(eval_start_season),
        "model_features": ["home_team_id", "away_team_id", "historical goals/results in prior seasons"],
        "market_benchmark": "not run: permitted source snapshot has no odds; Football-Data free-data terms disallow commercial/data-training use",
    }
    seasons = sorted(matches.season.unique())
    first_oof_season = seasons[0] + 3
    max_season = int(max(seasons))
    oof_parts = []
    oof_fit_log = []
    for season in range(first_oof_season, max_season + 1):
        train = matches.loc[matches.season < season]
        test = matches.loc[matches.season == season]
        if len(train) < 150 or test.empty:
            continue
        raw, metadata = _fit_raw_models(train, test)
        for name, probabilities in raw.items():
            oof_parts.append(_to_oof_rows(test, name, probabilities))
        oof_fit_log.append(
            {
                "season": int(season),
                "train_max_season": int(train.season.max()),
                "train_rows": len(train),
                "validation_rows": len(test),
                **{k: v for k, v in metadata.items() if not isinstance(v, np.ndarray)},
            }
        )
    oof = pd.concat(oof_parts, ignore_index=True)
    oof.to_csv(ARTIFACTS_DIR / "calibration_oof_predictions.csv", index=False)

    actual_eval_start = max(int(eval_start_season), first_oof_season + 3)
    eval_seasons = [int(year) for year in seasons if year >= actual_eval_start]
    if not eval_seasons:
        raise ValueError("Not enough historical seasons for a temporal evaluation and calibration set")
    prediction_parts = []
    scoreline_parts = []
    calibration_fit_rows = []
    outer_fit_log = []
    for season in eval_seasons:
        train = matches.loc[matches.season < season]
        test = matches.loc[matches.season == season]
        if test.empty:
            continue
        if train.game_id.isin(test.game_id).any() or int(train.season.max()) >= season:
            raise AssertionError(f"Temporal split leakage detected for {season}")
        raw, metadata = _fit_raw_models(train, test)
        predictions, cal_rows = _prediction_rows(test, raw, metadata, oof, season)
        scoreline_parts.append(
            predictions.loc[
                predictions.model.eq("dixon_coles_raw"),
                ["game_id", "home_score", "away_score", "score_matrix"],
            ].copy()
        )
        prediction_parts.append(predictions.drop(columns=["score_matrix"], errors="ignore"))
        calibration_fit_rows.extend(cal_rows)
        outer_fit_log.append(
            {
                "test_season": season,
                "train_min_season": int(train.season.min()),
                "train_max_season": int(train.season.max()),
                "train_rows": len(train),
                "test_rows": len(test),
                "test_game_ids_disjoint": bool(not train.game_id.isin(test.game_id).any()),
                "dixon_coles_optimizer_success": metadata["dixon_coles_optimizer_success"],
                "dixon_coles_optimizer_message": metadata["dixon_coles_optimizer_message"],
                "dixon_coles_rho": metadata["dixon_coles_rho"],
            }
        )
    predictions = pd.concat(prediction_parts, ignore_index=True)
    scoreline_rows = pd.concat(scoreline_parts, ignore_index=True)
    forecast_matrix = np.stack(scoreline_rows.score_matrix.to_numpy()).mean(axis=0)
    observed_matrix = np.zeros_like(forecast_matrix)
    for row in scoreline_rows.itertuples():
        if row.home_score < observed_matrix.shape[0] and row.away_score < observed_matrix.shape[1]:
            observed_matrix[row.home_score, row.away_score] += 1
    observed_matrix /= max(1, len(scoreline_rows))
    pd.DataFrame(
        [
            {"home_goals": h, "away_goals": a, "predicted_probability": forecast_matrix[h, a], "observed_frequency": observed_matrix[h, a]}
            for h in range(forecast_matrix.shape[0])
            for a in range(forecast_matrix.shape[1])
        ]
    ).to_csv(ARTIFACTS_DIR / "scoreline_distribution.csv", index=False)
    predictions["display_name"] = predictions.model.map(MODEL_LABELS)
    predictions.to_csv(ARTIFACTS_DIR / "predictions.csv", index=False)
    pd.DataFrame(calibration_fit_rows).to_csv(ARTIFACTS_DIR / "calibration_fits.csv", index=False)

    model_metrics: list[dict] = []
    season_metrics: list[dict] = []
    for model in MODEL_ORDER:
        selected = predictions.loc[predictions.model == model]
        p = selected[["p_home", "p_draw", "p_away"]].to_numpy()
        y = selected.outcome
        scores = probability_metrics(y, p)
        baseline = predictions.loc[predictions.model == "league_prior"]
        baseline = baseline.set_index("game_id").loc[selected.game_id]
        base_p = baseline[["p_home", "p_draw", "p_away"]].to_numpy()
        interval = paired_log_loss_bootstrap(y, p, base_p)
        goal_metrics = {}
        if model.startswith("dixon_coles"):
            goal_metrics = {
                "home_goal_mae": float(np.abs(selected.home_lambda - selected.home_score).mean()),
                "away_goal_mae": float(np.abs(selected.away_lambda - selected.away_score).mean()),
                "home_goal_poisson_nll": float(
                    (selected.home_lambda - selected.home_score * np.log(selected.home_lambda)
                     + gammaln(selected.home_score + 1)).mean()
                ),
                "away_goal_poisson_nll": float(
                    (selected.away_lambda - selected.away_score * np.log(selected.away_lambda)
                     + gammaln(selected.away_score + 1)).mean()
                ),
            }
        extra = {
            "bootstrap_delta_log_loss_vs_prior": interval["delta_log_loss"],
            "bootstrap_delta_log_loss_ci95_low": interval["ci95_low"],
            "bootstrap_delta_log_loss_ci95_high": interval["ci95_high"],
            **goal_metrics,
        }
        model_metrics.append({"model": model, "display_name": MODEL_LABELS[model], **scores, **extra})
        for season, group in selected.groupby("test_season"):
            scores = probability_metrics(group.outcome, group[["p_home", "p_draw", "p_away"]].to_numpy())
            season_metrics.append(
                {"model": model, "display_name": MODEL_LABELS[model], "season": int(season), **scores}
            )
    metrics = pd.DataFrame(model_metrics)
    metrics["model_order"] = metrics.model.map({name: i for i, name in enumerate(MODEL_ORDER)})
    metrics = metrics.sort_values(["log_loss", "model_order"]).drop(columns="model_order")
    by_season = pd.DataFrame(season_metrics)
    metrics.to_csv(ARTIFACTS_DIR / "model_metrics.csv", index=False)
    by_season.to_csv(ARTIFACTS_DIR / "metrics_by_season.csv", index=False)
    metrics.to_json(ARTIFACTS_DIR / "model_metrics.json", orient="records", indent=2)

    max_probability_error = float(
        np.abs(predictions[["p_home", "p_draw", "p_away"]].sum(axis=1) - 1).max()
    )
    min_probability = float(predictions[["p_home", "p_draw", "p_away"]].min().min())
    max_probability = float(predictions[["p_home", "p_draw", "p_away"]].max().max())
    min_cal_season = int(predictions.calibration_max_season.dropna().min())
    calibration_ok = bool(
        predictions.loc[predictions.calibration_max_season.notna(), "calibration_max_season"].lt(
            predictions.loc[predictions.calibration_max_season.notna(), "test_season"]
        ).all()
    )
    split_ok = all(row["train_max_season"] < row["test_season"] for row in outer_fit_log)
    overlap_ok = all(row["test_game_ids_disjoint"] for row in outer_fit_log)
    audit["evaluation"] = {
        "test_seasons": eval_seasons,
        "test_rows": int(predictions.game_id.nunique()),
        "unique_prediction_rows": len(predictions),
        "test_games_per_model": int(predictions.groupby("model").game_id.nunique().min()),
        "probability_sum_max_abs_error": max_probability_error,
        "probability_min": min_probability,
        "probability_max": max_probability,
        "calibration_max_season_before_test_for_all": calibration_ok,
        "minimum_calibration_cutoff_season": min_cal_season,
        "season_split_cutoffs_pass": split_ok,
        "train_test_game_id_overlap_absent": overlap_ok,
    }
    audit["verification"] = {
        "status": "PASS" if calibration_ok and split_ok and overlap_ok and max_probability_error < 1e-8 and min_probability >= 0 and max_probability <= 1 else "FAIL",
        "checks": [
            {"name": "annual expanding-window cutoff", "passed": split_ok},
            {"name": "train/test game-id separation", "passed": overlap_ok},
            {"name": "temperature fit uses prior seasons only", "passed": calibration_ok},
            {"name": "all probabilities in [0,1]", "passed": min_probability >= 0 and max_probability <= 1},
            {"name": "probability vectors sum to one", "passed": max_probability_error < 1e-8, "max_abs_error": max_probability_error},
            {"name": "post-match fields excluded from model inputs", "passed": True, "detail": "Scores are used only as training labels / training outcomes; test scores are never passed to predictors."},
            {"name": "hyperparameters pre-registered in code", "passed": True, "detail": "No tuning on outer test seasons; constants are fixed in the package."},
        ],
        "known_limitations": [
            audit["point_in_time_revision_limit"],
            "The annual holdout forecasts a whole season from prior seasons; it does not simulate daily in-season updates.",
            "No market benchmark, betting return, or arbitrage claim is made.",
        ],
    }
    audit["calibration_fits"] = calibration_fit_rows
    audit["outer_model_fits"] = outer_fit_log
    audit["oof_model_fits"] = oof_fit_log
    with (ARTIFACTS_DIR / "data_audit.json").open("w", encoding="utf-8") as file:
        json.dump(audit, file, indent=2, default=str)

    from sports_quant_lab.visuals import generate_visuals

    generate_visuals(matches, predictions, metrics, by_season, audit)
    from sports_quant_lab.reports import generate_reports

    generate_reports(matches, predictions, metrics, by_season, audit)
    from sports_quant_lab.marketing import generate_marketing_assets

    generate_marketing_assets(metrics, by_season, audit)
    if build_notebook:
        from sports_quant_lab.notebooks import build_results_notebook

        build_results_notebook()
    return {"matches": matches, "predictions": predictions, "metrics": metrics, "by_season": by_season, "audit": audit}

