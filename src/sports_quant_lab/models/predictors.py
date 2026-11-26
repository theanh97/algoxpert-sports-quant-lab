"""Small, auditable pre-match baselines and outcome models."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize, minimize_scalar
from scipy.special import gammaln, softmax
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from sports_quant_lab.constants import OUTCOMES


def _align_probabilities(probabilities: np.ndarray, classes: np.ndarray) -> np.ndarray:
    aligned = np.zeros((len(probabilities), len(OUTCOMES)), dtype=float)
    for source_index, label in enumerate(classes):
        aligned[:, OUTCOMES.index(str(label))] = probabilities[:, source_index]
    return _normalize(aligned)


def _normalize(probabilities: np.ndarray) -> np.ndarray:
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-12, None)
    return p / p.sum(axis=1, keepdims=True)


def league_prior(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Training-only historical outcome frequency, the minimum viable benchmark."""
    counts = train.outcome.value_counts().reindex(OUTCOMES, fill_value=0).to_numpy(dtype=float)
    prior = (counts + 1.0) / (counts.sum() + len(OUTCOMES))
    return np.tile(prior, (len(test), 1))


def logistic_team_model(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    """Regularized multinomial logistic regression on pre-match team identities."""
    transformer = ColumnTransformer(
        [("teams", OneHotEncoder(handle_unknown="ignore"), ["home_team_id", "away_team_id"])],
        remainder="drop",
    )
    pipeline = Pipeline(
        [
            ("features", transformer),
            ("classifier", LogisticRegression(C=0.25, max_iter=800, solver="lbfgs")),
        ]
    )
    pipeline.fit(train[["home_team_id", "away_team_id"]], train.outcome)
    raw = pipeline.predict_proba(test[["home_team_id", "away_team_id"]])
    return _align_probabilities(raw, pipeline.named_steps["classifier"].classes_)


def elo_team_model(
    train: pd.DataFrame,
    test: pd.DataFrame,
    k_factor: float = 20.0,
    home_advantage: float = 65.0,
) -> np.ndarray:
    """Elo rating model updated only with the rows passed as training history."""
    ratings: dict[str, float] = {}
    for row in train.sort_values("date_time_utc").itertuples():
        home = ratings.get(row.home_team_id, 1500.0)
        away = ratings.get(row.away_team_id, 1500.0)
        expected_home = 1.0 / (1.0 + 10.0 ** (-(home - away + home_advantage) / 400.0))
        actual_home = 1.0 if row.home_score > row.away_score else 0.5 if row.home_score == row.away_score else 0.0
        margin = abs(row.home_score - row.away_score)
        multiplier = min(2.0, 1.0 + 0.25 * np.log1p(margin))
        delta = k_factor * multiplier * (actual_home - expected_home)
        ratings[row.home_team_id] = home + delta
        ratings[row.away_team_id] = away - delta

    draw_rate = float(train.outcome.eq("D").mean())
    draw_rate = float(np.clip(draw_rate, 0.12, 0.38))
    probs = []
    for row in test.itertuples():
        home = ratings.get(row.home_team_id, 1500.0)
        away = ratings.get(row.away_team_id, 1500.0)
        share = 1.0 / (1.0 + 10.0 ** (-(home - away + home_advantage) / 400.0))
        probs.append([(1 - draw_rate) * share, draw_rate, (1 - draw_rate) * (1 - share)])
    return _normalize(np.asarray(probs))


@dataclass
class DixonColesModel:
    """Regularized Dixon–Coles low-score model with team attack/defence effects."""

    ridge: float = 0.04
    maxiter: int = 600

    def fit(self, matches: pd.DataFrame) -> DixonColesModel:
        self.teams_ = sorted(set(matches.home_team_id) | set(matches.away_team_id))
        self.team_index_ = {team: i for i, team in enumerate(self.teams_)}
        home_ix = matches.home_team_id.map(self.team_index_).to_numpy(dtype=int)
        away_ix = matches.away_team_id.map(self.team_index_).to_numpy(dtype=int)
        home_goals = matches.home_score.to_numpy(dtype=float)
        away_goals = matches.away_score.to_numpy(dtype=float)
        n_teams = len(self.teams_)
        n_free = max(0, n_teams - 1)
        self.n_free_ = n_free
        avg_total = max(0.25, float((home_goals.sum() + away_goals.sum()) / (2 * len(matches))))
        initial = np.zeros(2 + 2 * n_free + 1, dtype=float)
        initial[0] = np.log(avg_total)
        initial[1] = 0.15
        initial[-1] = -0.03

        def unpack(params: np.ndarray) -> tuple[float, float, np.ndarray, np.ndarray, float]:
            base = params[0]
            home_adv = params[1]
            attack_free = params[2 : 2 + n_free]
            defence_free = params[2 + n_free : 2 + 2 * n_free]
            attack = np.r_[attack_free, -attack_free.sum()] if n_teams else np.zeros(0)
            defence = np.r_[defence_free, -defence_free.sum()] if n_teams else np.zeros(0)
            return base, home_adv, attack, defence, float(params[-1])

        def objective(params: np.ndarray) -> float:
            base, home_adv, attack, defence, rho = unpack(params)
            log_h = np.clip(base + home_adv + attack[home_ix] + defence[away_ix], -4, 4)
            log_a = np.clip(base + attack[away_ix] + defence[home_ix], -4, 4)
            lam_h = np.exp(log_h)
            lam_a = np.exp(log_a)
            tau = np.ones(len(matches), dtype=float)
            zero_zero = (home_goals == 0) & (away_goals == 0)
            zero_one = (home_goals == 0) & (away_goals == 1)
            one_zero = (home_goals == 1) & (away_goals == 0)
            one_one = (home_goals == 1) & (away_goals == 1)
            tau[zero_zero] = 1.0 - lam_h[zero_zero] * lam_a[zero_zero] * rho
            tau[zero_one] = 1.0 + lam_h[zero_one] * rho
            tau[one_zero] = 1.0 + lam_a[one_zero] * rho
            tau[one_one] = 1.0 - rho
            if np.any(tau <= 0):
                return 1e12 + float(np.square(np.minimum(tau, 0)).sum()) * 1e8
            loglik = (
                home_goals * log_h - lam_h - gammaln(home_goals + 1)
                + away_goals * log_a - lam_a - gammaln(away_goals + 1)
                + np.log(tau)
            )
            penalty = 0.5 * self.ridge * (np.square(attack).sum() + np.square(defence).sum())
            return float(-loglik.sum() + penalty)

        bounds = [(-1.5, 1.5), (-0.8, 0.8)] + [(-1.5, 1.5)] * (2 * n_free) + [(-0.2, 0.2)]
        result = minimize(
            objective,
            initial,
            method="L-BFGS-B",
            bounds=bounds,
            options={"maxiter": self.maxiter, "ftol": 1e-9},
        )
        if not result.success and not np.isfinite(result.fun):
            raise RuntimeError(f"Dixon-Coles optimization failed: {result.message}")
        self.params_ = result.x
        self.optimizer_success_ = bool(result.success)
        self.optimizer_message_ = str(result.message)
        self.objective_ = float(result.fun)
        self.rho_ = unpack(result.x)[-1]
        return self

    def goal_rates(self, matches: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        base, home_adv, attack, defence, _ = self._unpack_params()
        home_ix = matches.home_team_id.map(self.team_index_).fillna(-1).to_numpy(dtype=int)
        away_ix = matches.away_team_id.map(self.team_index_).fillna(-1).to_numpy(dtype=int)
        attack_home = np.where(home_ix >= 0, attack[np.maximum(home_ix, 0)], 0.0)
        attack_away = np.where(away_ix >= 0, attack[np.maximum(away_ix, 0)], 0.0)
        defence_home = np.where(home_ix >= 0, defence[np.maximum(home_ix, 0)], 0.0)
        defence_away = np.where(away_ix >= 0, defence[np.maximum(away_ix, 0)], 0.0)
        lam_h = np.exp(np.clip(base + home_adv + attack_home + defence_away, -4, 4))
        lam_a = np.exp(np.clip(base + attack_away + defence_home, -4, 4))
        return lam_h, lam_a

    def _unpack_params(self) -> tuple[float, float, np.ndarray, np.ndarray, float]:
        n_free = self.n_free_
        n_teams = len(self.teams_)
        attack_free = self.params_[2 : 2 + n_free]
        defence_free = self.params_[2 + n_free : 2 + 2 * n_free]
        attack = np.r_[attack_free, -attack_free.sum()] if n_teams else np.zeros(0)
        defence = np.r_[defence_free, -defence_free.sum()] if n_teams else np.zeros(0)
        return float(self.params_[0]), float(self.params_[1]), attack, defence, float(self.params_[-1])

    def predict_score_matrices(self, matches: pd.DataFrame, max_goals: int = 10) -> np.ndarray:
        lam_h, lam_a = self.goal_rates(matches)
        goals = np.arange(max_goals + 1)
        matrices = []
        _, _, _, _, rho = self._unpack_params()
        for home_rate, away_rate in zip(lam_h, lam_a):
            home_p = np.exp(goals * np.log(home_rate) - home_rate - gammaln(goals + 1))
            away_p = np.exp(goals * np.log(away_rate) - away_rate - gammaln(goals + 1))
            matrix = np.outer(home_p, away_p)
            matrix[0, 0] *= max(1e-9, 1.0 - home_rate * away_rate * rho)
            matrix[0, 1] *= max(1e-9, 1.0 + home_rate * rho)
            matrix[1, 0] *= max(1e-9, 1.0 + away_rate * rho)
            matrix[1, 1] *= max(1e-9, 1.0 - rho)
            matrix /= matrix.sum()
            matrices.append(matrix)
        return np.asarray(matrices)

    def predict_proba(self, matches: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        matrices = self.predict_score_matrices(matches)
        outcomes = np.column_stack(
            [np.tril(matrices, -1).sum(axis=(1, 2)), np.trace(matrices, axis1=1, axis2=2), np.triu(matrices, 1).sum(axis=(1, 2))]
        )
        # Matrix rows are home goals and columns away goals: lower triangle is home wins.
        home_rate, away_rate = self.goal_rates(matches)
        return _normalize(outcomes), home_rate, away_rate, matrices


@dataclass
class TemperatureScaler:
    """Single-parameter multiclass temperature scaling fit on prior-season OOF data."""

    def fit(self, probabilities: np.ndarray, outcomes: pd.Series | np.ndarray) -> TemperatureScaler:
        y = np.asarray([OUTCOMES.index(str(label)) for label in outcomes], dtype=int)
        logits = np.log(np.clip(_normalize(probabilities), 1e-12, 1.0))

        def loss(log_temperature: float) -> float:
            scaled = softmax(logits / np.exp(log_temperature), axis=1)
            return float(-np.log(np.clip(scaled[np.arange(len(y)), y], 1e-12, 1)).mean())

        result = minimize_scalar(loss, bounds=(-2.5, 2.5), method="bounded", options={"xatol": 1e-6})
        self.temperature_ = float(np.exp(result.x))
        self.training_log_loss_ = float(result.fun)
        return self

    def transform(self, probabilities: np.ndarray) -> np.ndarray:
        logits = np.log(np.clip(_normalize(probabilities), 1e-12, 1.0))
        return _normalize(softmax(logits / self.temperature_, axis=1))

