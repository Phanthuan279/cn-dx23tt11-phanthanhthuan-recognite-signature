import inspect

import numpy as np

from sigverify.evaluation.metrics import (
    compute_far_frr,
    evaluate_at_threshold,
    find_eer,
    roc_auc,
    select_threshold,
)


def test_eer_is_zero_for_perfectly_separated_scores():
    # genuine (label=1) all have low distance, impostor (label=0) all have high distance
    labels = np.array([1] * 50 + [0] * 50)
    scores = np.array([0.1] * 50 + [2.0] * 50)
    far, frr, thresholds = compute_far_frr(scores, labels)
    eer, tau = find_eer(far, frr, thresholds)
    assert eer < 0.01
    assert 0.1 < tau < 2.0


def test_eer_is_near_half_for_fully_overlapping_scores():
    rng = np.random.default_rng(0)
    # both classes drawn from the exact same distribution -> no separability
    scores = rng.normal(loc=1.0, scale=0.3, size=2000)
    labels = np.array([1, 0] * 1000)
    far, frr, thresholds = compute_far_frr(scores, labels)
    eer, _ = find_eer(far, frr, thresholds)
    assert 0.35 < eer < 0.65


def test_select_threshold_eer_and_evaluate_at_threshold_consistency():
    val_labels = np.array([1] * 40 + [0] * 40)
    val_scores = np.array([0.2] * 40 + [1.5] * 40)
    tau = select_threshold(val_scores, val_labels, method="eer")

    test_labels = np.array([1] * 10 + [0] * 10)
    test_scores = np.array([0.2] * 10 + [1.5] * 10)
    result = evaluate_at_threshold(test_scores, test_labels, tau)

    assert result["accuracy"] == 1.0
    assert result["far"] == 0.0
    assert result["frr"] == 0.0
    assert result["tau"] == tau


def test_evaluate_at_threshold_signature_has_no_validation_parameters():
    """Guards against threshold leakage: evaluate_at_threshold must not be able
    to accept validation data -- it only takes test scores/labels and a frozen tau.
    """
    params = list(inspect.signature(evaluate_at_threshold).parameters.keys())
    assert params == ["test_scores", "test_labels", "tau"]
    assert not any("val" in p for p in params)


def test_select_threshold_signature_has_no_test_parameters():
    params = list(inspect.signature(select_threshold).parameters.keys())
    assert not any(p.startswith("test") for p in params)


def test_roc_auc_perfect_separation():
    labels = np.array([1] * 20 + [0] * 20)
    scores = np.array([0.1] * 20 + [2.0] * 20)
    _, _, auc = roc_auc(scores, labels)
    assert auc == 1.0
