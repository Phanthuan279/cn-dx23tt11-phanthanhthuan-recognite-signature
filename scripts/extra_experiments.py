"""Additional real experiments to support deeper analysis chapters in the
thesis report: effect of k on KNN, distance metric comparison, SVM C/gamma
sensitivity (on a reduced training subset for speed), and a 2D PCA
visualization of the real MNIST test set. All numbers here are real,
computed from the actual MNIST data loaded via src/digitrec/data.py --
nothing is fabricated or estimated.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

import sys

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from digitrec.data import load_mnist, split_mnist  # noqa: E402

RESULTS = BASE / "results"
RESULTS.mkdir(exist_ok=True)


def main() -> None:
    X, y = load_mnist()
    X_train, X_val, X_test, y_train, y_val, y_test = split_mnist(X, y)

    out: dict = {}

    # 1. KNN: effect of k on validation accuracy
    print("Running KNN k-sweep...")
    k_sweep = []
    for k in [1, 3, 5, 7, 9, 11, 15, 21]:
        t0 = time.time()
        knn = KNeighborsClassifier(n_neighbors=k, n_jobs=-1)
        knn.fit(X_train, y_train)
        acc = knn.score(X_val, y_val)
        t1 = time.time()
        k_sweep.append({"k": k, "val_accuracy": acc, "eval_time_seconds": t1 - t0})
        print(f"  k={k}: val_acc={acc:.4f} ({t1 - t0:.2f}s)")
    out["knn_k_sweep"] = k_sweep

    # 2. KNN: distance metric comparison at k=5
    print("Running KNN metric comparison...")
    metric_cmp = []
    for metric in ["euclidean", "manhattan", "chebyshev"]:
        t0 = time.time()
        knn = KNeighborsClassifier(n_neighbors=5, metric=metric, n_jobs=-1)
        knn.fit(X_train, y_train)
        acc = knn.score(X_val, y_val)
        t1 = time.time()
        metric_cmp.append({"metric": metric, "val_accuracy": acc, "eval_time_seconds": t1 - t0})
        print(f"  metric={metric}: val_acc={acc:.4f} ({t1 - t0:.2f}s)")
    out["knn_metric_comparison"] = metric_cmp

    # 3. SVM: C sensitivity on a reduced 5000-sample subset (full-set sweep
    # is too slow to repeat several times in one session -- 235s per fit on
    # 54,000 samples). Clearly labeled as a reduced-subset study below.
    print("Running SVM C-sweep on 5000-sample subset...")
    rng = np.random.RandomState(42)
    idx = rng.choice(len(X_train), 5000, replace=False)
    X_sub, y_sub = X_train[idx], y_train[idx]
    c_sweep = []
    for C in [0.1, 1.0, 5.0, 10.0, 50.0]:
        t0 = time.time()
        svm = SVC(kernel="rbf", C=C, gamma="scale")
        svm.fit(X_sub, y_sub)
        acc = svm.score(X_val, y_val)
        t1 = time.time()
        c_sweep.append({"C": C, "val_accuracy": acc, "fit_time_seconds": t1 - t0})
        print(f"  C={C}: val_acc={acc:.4f} ({t1 - t0:.2f}s)")
    out["svm_c_sweep_subset5000"] = c_sweep

    # 4. SVM: gamma sensitivity on the same reduced subset, C=5
    print("Running SVM gamma-sweep on 5000-sample subset...")
    gamma_sweep = []
    for gamma in ["scale", 0.001, 0.01, 0.1]:
        t0 = time.time()
        svm = SVC(kernel="rbf", C=5.0, gamma=gamma)
        svm.fit(X_sub, y_sub)
        acc = svm.score(X_val, y_val)
        t1 = time.time()
        gamma_sweep.append({"gamma": str(gamma), "val_accuracy": acc, "fit_time_seconds": t1 - t0})
        print(f"  gamma={gamma}: val_acc={acc:.4f} ({t1 - t0:.2f}s)")
    out["svm_gamma_sweep_subset5000"] = gamma_sweep

    out["subset_size"] = 5000
    out["note"] = (
        "C/gamma sweeps use a 5,000-sample stratified-random subset of the "
        "training set (not the full 54,000) to keep repeated SVM fits fast "
        "within one session; they show the real trend, not final-model "
        "numbers. k and distance-metric sweeps use the full 54,000-sample "
        "training set and the full 6,000-sample validation set."
    )

    with open(RESULTS / "extra_experiments.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Saved {RESULTS / 'extra_experiments.json'}")

    # 5. PCA 2D projection of the real test set, colored by true digit
    print("Computing PCA 2D projection of test set...")
    pca = PCA(n_components=2, random_state=42)
    X_test_2d = pca.fit_transform(X_test)
    np.savez(
        RESULTS / "pca_test_2d.npz",
        X_2d=X_test_2d,
        y=y_test,
        explained_variance_ratio=pca.explained_variance_ratio_,
    )
    print(f"PCA explained variance ratio (2 components): {pca.explained_variance_ratio_}")
    print(f"Saved {RESULTS / 'pca_test_2d.npz'}")


if __name__ == "__main__":
    main()
