"""FAR / FRR / EER / Accuracy / ROC-AUC, shared by the baseline and every
Siamese configuration.

Convention: `scores` are DISTANCES (lower = more likely genuine/same-signer).
This lets every model (SVM decision_function, Siamese embedding distance)
plug into the same functions as long as the caller flips the sign where
needed (see src/sigverify/training/train_baseline.py).

Threshold-selection safety: `select_threshold` only ever sees validation
data, and `evaluate_at_threshold` only ever accepts a precomputed `tau` plus
test data -- it has no way to fit a threshold itself, which is what prevents
threshold leakage from test into the reported numbers.
"""

from __future__ import annotations

from typing import Sequence, Tuple

import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve


def compute_far_frr(
    scores: Sequence[float], labels: Sequence[int], n_thresholds: int = 200
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sweep thresholds over the observed score range and compute FAR/FRR at each.

    FAR(t) = fraction of impostor pairs (label=0) with score < t (wrongly accepted)
    FRR(t) = fraction of genuine pairs (label=1) with score >= t (wrongly rejected)
    """
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)

    lo, hi = float(scores.min()), float(scores.max())
    if lo == hi:
        hi = lo + 1e-6
    thresholds = np.linspace(lo, hi, n_thresholds)

    neg_scores = scores[labels == 0]
    pos_scores = scores[labels == 1]

    far = np.array([(neg_scores < t).mean() if len(neg_scores) else 0.0 for t in thresholds])
    frr = np.array([(pos_scores >= t).mean() if len(pos_scores) else 0.0 for t in thresholds])
    return far, frr, thresholds


def find_eer(far: np.ndarray, frr: np.ndarray, thresholds: np.ndarray) -> Tuple[float, float]:
    """Find the Equal Error Rate point, linearly interpolating between the two
    grid points where FAR-FRR changes sign (they rarely cross exactly on-grid).
    """
    diff = far - frr
    sign_changes = np.where(np.diff(np.sign(diff)) != 0)[0]

    if len(sign_changes) == 0:
        i = int(np.argmin(np.abs(diff)))
        eer = float((far[i] + frr[i]) / 2)
        return eer, float(thresholds[i])

    i = int(sign_changes[0])
    d0, d1 = diff[i], diff[i + 1]
    x0, x1 = thresholds[i], thresholds[i + 1]
    far0, far1 = far[i], far[i + 1]

    if d1 == d0:
        return float(far0), float(x0)

    frac = -d0 / (d1 - d0)
    tau_star = x0 + frac * (x1 - x0)
    eer = far0 + frac * (far1 - far0)
    return float(eer), float(tau_star)


def select_threshold(
    val_scores: Sequence[float], val_labels: Sequence[int], method: str = "eer", n_thresholds: int = 200
) -> float:
    """Choose a threshold tau using ONLY validation scores/labels. Never call
    this with test data -- evaluate_at_threshold enforces the reverse.
    """
    far, frr, thresholds = compute_far_frr(val_scores, val_labels, n_thresholds)

    if method == "eer":
        _, tau = find_eer(far, frr, thresholds)
        return tau

    if method == "max_accuracy":
        val_scores = np.asarray(val_scores, dtype=np.float64)
        val_labels = np.asarray(val_labels, dtype=np.int64)
        accuracies = [
            float(((val_scores < t).astype(int) == val_labels).mean()) for t in thresholds
        ]
        return float(thresholds[int(np.argmax(accuracies))])

    raise ValueError(f"Unknown threshold selection method: {method}")


def evaluate_at_threshold(test_scores: Sequence[float], test_labels: Sequence[int], tau: float) -> dict:
    """Evaluate a FROZEN threshold `tau` (chosen beforehand on validation) against
    test data. Deliberately takes no validation arguments -- a threshold refit
    here would leak test information into what is reported as the test score.
    """
    test_scores = np.asarray(test_scores, dtype=np.float64)
    test_labels = np.asarray(test_labels, dtype=np.int64)

    preds = (test_scores < tau).astype(int)
    accuracy = float((preds == test_labels).mean())

    neg = test_scores[test_labels == 0]
    pos = test_scores[test_labels == 1]
    far = float((neg < tau).mean()) if len(neg) else 0.0
    frr = float((pos >= tau).mean()) if len(pos) else 0.0

    return {"accuracy": accuracy, "far": far, "frr": frr, "tau": float(tau), "n_pairs": int(len(test_labels))}


def roc_auc(scores: Sequence[float], labels: Sequence[int]) -> Tuple[np.ndarray, np.ndarray, float]:
    """ROC curve + AUC. Scores are distances, so they're negated before
    handing to sklearn (which expects higher score = more positive).
    """
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(labels, dtype=np.int64)
    y_score = -scores
    fpr, tpr, _ = roc_curve(labels, y_score)
    auc = float(roc_auc_score(labels, y_score))
    return fpr, tpr, auc
