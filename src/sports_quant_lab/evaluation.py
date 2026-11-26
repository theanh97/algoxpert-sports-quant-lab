"""Proper scores, reliability diagnostics, and paired uncertainty estimates."""

from __future__ import annotations

from itertools import pairwise

import numpy as np
import pandas as pd

from sports_quant_lab.constants import OUTCOMES


def probability_metrics(y_true: pd.Series | np.ndarray, probabilities: np.ndarray) -> dict[str, float]:
    y = np.asarray([OUTCOMES.index(str(label)) for label in y_true], dtype=int)
    p = np.clip(np.asarray(probabilities, dtype=float), 1e-12, 1.0)
    p = p / p.sum(axis=1, keepdims=True)
    one_hot = np.eye(len(OUTCOMES))[y]
    winner = p.argmax(axis=1)
    confidence = p.max(axis=1)
    correct = (winner == y).astype(float)
    ece = 0.0
    bins = np.linspace(0, 1, 11)
    for low, high in pairwise(bins):
        mask = (confidence >= low) & (confidence < high if high < 1 else confidence <= high)
        if mask.any():
            ece += float(mask.mean() * abs(correct[mask].mean() - confidence[mask].mean()))
    # Ranked score uses ordered away/draw/home classes, separate from the probability column order.
    ordered = p[:, [2, 1, 0]]
    ordered_y = np.eye(3)[np.where(y == 0, 2, np.where(y == 2, 0, 1))]
    rps = np.square(np.cumsum(ordered, axis=1)[:, :-1] - np.cumsum(ordered_y, axis=1)[:, :-1]).sum(axis=1).mean() / 2
    class_ece_values = []
    for class_index in range(3):
        class_p = p[:, class_index]
        class_y = one_hot[:, class_index]
        value = 0.0
        for low, high in pairwise(bins):
            mask = (class_p >= low) & (class_p < high if high < 1 else class_p <= high)
            if mask.any():
                value += float(mask.mean() * abs(class_y[mask].mean() - class_p[mask].mean()))
        class_ece_values.append(value)
    return {
        "n_matches": len(y),
        "accuracy": float(np.mean(winner == y)),
        "log_loss": float(-np.log(np.clip(p[np.arange(len(y)), y], 1e-12, 1)).mean()),
        "brier": float(np.square(p - one_hot).sum(axis=1).mean()),
        "ranked_probability_score": float(rps),
        "top_label_ece_10": float(ece),
        "classwise_ece_10": float(np.mean(class_ece_values)),
    }


def paired_log_loss_bootstrap(
    y_true: pd.Series | np.ndarray,
    candidate: np.ndarray,
    reference: np.ndarray,
    iterations: int = 2000,
    seed: int = 20261126,
) -> dict[str, float]:
    """Paired match bootstrap of candidate minus reference log loss; negative is better."""
    y = np.asarray([OUTCOMES.index(str(label)) for label in y_true], dtype=int)
    candidate_loss = -np.log(np.clip(candidate[np.arange(len(y)), y], 1e-12, 1))
    reference_loss = -np.log(np.clip(reference[np.arange(len(y)), y], 1e-12, 1))
    delta = candidate_loss - reference_loss
    rng = np.random.default_rng(seed)
    draws = np.empty(iterations, dtype=float)
    for i in range(iterations):
        draws[i] = rng.choice(delta, size=len(delta), replace=True).mean()
    low, high = np.quantile(draws, [0.025, 0.975])
    return {"delta_log_loss": float(delta.mean()), "ci95_low": float(low), "ci95_high": float(high)}


def calibration_table(
    y_true: pd.Series | np.ndarray, probabilities: np.ndarray, n_bins: int = 10
) -> pd.DataFrame:
    y = np.asarray([OUTCOMES.index(str(label)) for label in y_true], dtype=int)
    edges = np.linspace(0, 1, n_bins + 1)
    rows: list[dict] = []
    p = np.asarray(probabilities, dtype=float)
    for class_index, label in enumerate(OUTCOMES):
        for i, (low, high) in enumerate(pairwise(edges)):
            mask = (p[:, class_index] >= low) & (
                p[:, class_index] < high if i < n_bins - 1 else p[:, class_index] <= high
            )
            if mask.any():
                rows.append(
                    {
                        "class": label,
                        "bin": i,
                        "mean_probability": float(p[mask, class_index].mean()),
                        "observed_frequency": float((y[mask] == class_index).mean()),
                        "count": int(mask.sum()),
                    }
                )
    return pd.DataFrame(rows)

