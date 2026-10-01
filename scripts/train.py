"""Train and compare KNN vs SVM on the real MNIST dataset (Yêu cầu triển
khai: "Huấn luyện và so sánh hiệu quả của mô hình học máy KNN và SVM trên
tập dữ liệu MNIST"). Saves trained models to models/ and real metrics
(accuracy, per-class report, confusion matrix, timing) to results/.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib  # noqa: E402

from digitrec.data import load_mnist, split_mnist  # noqa: E402
from digitrec.evaluate import evaluate_model, plot_confusion_matrix  # noqa: E402
from digitrec.models import build_knn, build_svm  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE / "models"
RESULTS_DIR = BASE / "results"


def main() -> None:
    MODELS_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    print("[train] loading real MNIST (70000 samples)...", flush=True)
    X, y = load_mnist()
    X = X.astype("float32") / 255.0  # pixel values 0-255 -> 0-1
    X_train, X_val, X_test, y_train, y_val, y_test = split_mnist(X, y)
    print(f"[train] split: train={len(X_train)} val={len(X_val)} test={len(X_test)}", flush=True)

    summary = {}

    for name, builder in (("knn", build_knn), ("svm", build_svm)):
        print(f"[train] === {name} ===", flush=True)
        model = builder()
        t0 = time.time()
        model.fit(X_train, y_train)
        fit_time = time.time() - t0
        print(f"[train] {name} fit in {fit_time:.1f}s", flush=True)

        val_metrics = evaluate_model(model, X_val, y_val)
        test_metrics = evaluate_model(model, X_test, y_test)
        print(f"[train] {name} val_acc={val_metrics['accuracy']:.4f} test_acc={test_metrics['accuracy']:.4f}", flush=True)

        joblib.dump(model, MODELS_DIR / f"{name}_mnist.joblib")
        plot_confusion_matrix(
            test_metrics["confusion_matrix"], f"Ma trận nhầm lẫn - {name.upper()} (test)",
            str(RESULTS_DIR / f"confusion_matrix_{name}.png"),
        )

        summary[name] = {
            "fit_time_seconds": fit_time,
            "val_accuracy": val_metrics["accuracy"],
            "test_accuracy": test_metrics["accuracy"],
            "test_classification_report": test_metrics["report"],
        }
        (RESULTS_DIR / f"{name}_metrics.json").write_text(json.dumps(summary[name], indent=2))

    (RESULTS_DIR / "comparison_summary.json").write_text(json.dumps(summary, indent=2))
    print("[train] Summary written to results/comparison_summary.json")
    print(json.dumps(
        {k: {"test_accuracy": v["test_accuracy"], "fit_time_seconds": v["fit_time_seconds"]} for k, v in summary.items()},
        indent=2,
    ))


if __name__ == "__main__":
    main()
