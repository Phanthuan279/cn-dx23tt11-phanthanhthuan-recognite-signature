"""Two additional real experiments supporting Chapter 4's robustness and
qualitative-error analysis:
1. Stratified 5-fold cross-validation of KNN (k=5) on a 10,000-sample subset
   of the training set, to check the stability (variance across folds) of
   the accuracy estimate. Uses a subset rather than the full 54,000-sample
   training set for the same speed reason documented for the SVM C/gamma
   subset sweeps in scripts/extra_experiments.py.
2. A gallery of real misclassified test images for both KNN and SVM, drawn
   from the actually-trained models (models/*.joblib) predicting on the real
   MNIST test set.

Preprocessing must match scripts/train.py exactly (pixel values scaled to
[0, 1] before the train/val/test split), since the saved models were fit on
that scale; a sanity check against results/comparison_summary.json's stored
accuracies guards against a silent preprocessing mismatch.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "src"))

from digitrec.data import load_mnist, split_mnist  # noqa: E402

RESULTS = BASE / "results"
MODELS = BASE / "models"
OUT = BASE / "thesis" / "abs" / "formulas"


def run_kfold():
    print("Loading MNIST and splitting (same preprocessing as scripts/train.py)...")
    X, y = load_mnist()
    X = X.astype("float32") / 255.0
    X_train, X_val, X_test, y_train, y_val, y_test = split_mnist(X, y)

    rng = np.random.RandomState(42)
    idx = rng.choice(len(X_train), 10000, replace=False)
    X_sub, y_sub = X_train[idx], y_train[idx]

    print("Running stratified 5-fold CV for KNN (k=5) on 10,000-sample subset...")
    knn = KNeighborsClassifier(n_neighbors=5, n_jobs=-1)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    t0 = time.time()
    scores = cross_val_score(knn, X_sub, y_sub, cv=skf, n_jobs=None)
    t1 = time.time()
    print(f"  fold scores: {scores}")
    print(f"  mean={scores.mean():.4f} std={scores.std():.4f} time={t1-t0:.1f}s")

    out = {
        "subset_size": 10000,
        "n_splits": 5,
        "fold_accuracies": scores.tolist(),
        "mean_accuracy": float(scores.mean()),
        "std_accuracy": float(scores.std()),
        "total_time_seconds": t1 - t0,
    }
    with open(RESULTS / "kfold_cv.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Saved {RESULTS / 'kfold_cv.json'}")

    fig, ax = plt.subplots(figsize=(7, 4.2))
    folds = [f"Fold {i+1}" for i in range(5)]
    ax.bar(folds, scores, color="#2a4d7a", width=0.55)
    ax.axhline(scores.mean(), color="#c0392b", linestyle="--", linewidth=1.4,
               label=f"Trung bình = {scores.mean():.4f}")
    ax.set_ylabel("Độ chính xác")
    ax.set_ylim(min(scores) - 0.01, max(scores) + 0.01)
    ax.set_title("Độ chính xác KNN (k=5) qua 5 fold\n(stratified 5-fold CV, tập con 10.000 mẫu)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUT / "chart_kfold_cv.png", dpi=200, facecolor="white")
    plt.close(fig)
    print("wrote chart_kfold_cv.png")

    return X_test, y_test


def run_error_gallery(X_test, y_test):
    print("Loading trained models for misclassified-sample gallery...")
    knn = joblib.load(MODELS / "knn_mnist.joblib")
    svm = joblib.load(MODELS / "svm_mnist.joblib")

    knn_pred = knn.predict(X_test)
    svm_pred = svm.predict(X_test)

    with open(RESULTS / "comparison_summary.json", encoding="utf-8") as f:
        comp = json.load(f)
    knn_acc = (knn_pred == y_test).mean()
    svm_acc = (svm_pred == y_test).mean()
    print(f"sanity check -- recomputed knn_acc={knn_acc:.4f} "
          f"(stored={comp['knn']['test_accuracy']:.4f}), "
          f"recomputed svm_acc={svm_acc:.4f} "
          f"(stored={comp['svm']['test_accuracy']:.4f})")
    assert abs(knn_acc - comp["knn"]["test_accuracy"]) < 0.002, "KNN accuracy mismatch -- preprocessing bug"
    assert abs(svm_acc - comp["svm"]["test_accuracy"]) < 0.002, "SVM accuracy mismatch -- preprocessing bug"

    knn_wrong = np.where(knn_pred != y_test)[0]
    svm_wrong = np.where(svm_pred != y_test)[0]
    both_wrong = np.intersect1d(knn_wrong, svm_wrong)
    print(f"KNN errors: {len(knn_wrong)}, SVM errors: {len(svm_wrong)}, "
          f"both wrong (same sample): {len(both_wrong)}")

    rng = np.random.RandomState(7)

    def gallery(indices, pred, fname, title):
        chosen = rng.choice(indices, size=min(12, len(indices)), replace=False)
        fig, axes = plt.subplots(3, 4, figsize=(8, 6.2))
        for ax, i in zip(axes.flat, chosen):
            img = X_test[i].reshape(28, 28)
            ax.imshow(img, cmap="gray")
            ax.set_title(f"Thật: {y_test[i]} | Dự đoán: {pred[i]}", fontsize=10)
            ax.axis("off")
        fig.suptitle(title, fontsize=12)
        plt.tight_layout()
        plt.savefig(OUT / fname, dpi=200, facecolor="white")
        plt.close(fig)
        print(f"wrote {fname}")
        return chosen.tolist()

    knn_chosen = gallery(knn_wrong, knn_pred, "error_gallery_knn.png",
                          "12 ảnh KNN dự đoán sai thật (tập test MNIST)")
    svm_chosen = gallery(svm_wrong, svm_pred, "error_gallery_svm.png",
                          "12 ảnh SVM dự đoán sai thật (tập test MNIST)")

    out = {
        "knn_total_errors": int(len(knn_wrong)),
        "svm_total_errors": int(len(svm_wrong)),
        "both_wrong_same_sample": int(len(both_wrong)),
        "knn_gallery_indices": knn_chosen,
        "svm_gallery_indices": svm_chosen,
    }
    with open(RESULTS / "error_gallery.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Saved {RESULTS / 'error_gallery.json'}")


if __name__ == "__main__":
    X_test, y_test = run_kfold()
    run_error_gallery(X_test, y_test)
