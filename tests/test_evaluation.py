import numpy as np

from sports_quant_lab.evaluation import (
    calibration_table,
    paired_log_loss_bootstrap,
    probability_metrics,
)


def test_probability_metrics_valid_distribution():
    y = np.array(["H", "D", "A", "H"])
    p = np.array([[0.7, 0.2, 0.1], [0.2, 0.6, 0.2], [0.1, 0.2, 0.7], [0.6, 0.3, 0.1]])
    result = probability_metrics(y, p)
    assert result["n_matches"] == 4
    assert result["accuracy"] == 1.0
    assert 0 <= result["brier"] <= 2
    assert 0 <= result["top_label_ece_10"] <= 1


def test_calibration_table_and_bootstrap_are_reproducible():
    y = np.array(["H", "D", "A", "H", "D", "A"])
    p = np.full((6, 3), 1 / 3)
    table = calibration_table(y, p, n_bins=5)
    assert set(table["class"]) == {"H", "D", "A"}
    interval_a = paired_log_loss_bootstrap(y, p, p, iterations=100, seed=7)
    interval_b = paired_log_loss_bootstrap(y, p, p, iterations=100, seed=7)
    assert interval_a == interval_b
    assert interval_a["delta_log_loss"] == 0

