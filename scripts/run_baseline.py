"""Train and evaluate the HOG/LBP + SVM baseline, using the exact same
pairs/splits/metrics framework as the Siamese configurations so the
comparison is apples-to-apples.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib
import matplotlib.pyplot as plt
import pandas as pd

from sigverify.evaluation.metrics import (  # noqa: E402
    evaluate_at_threshold,
    evaluate_by_forgery_type,
    roc_auc,
    select_threshold,
)
from sigverify.training.train_baseline import build_feature_matrix, fit_svm, scores_from_svm  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402
from sigverify.utils.seed import set_seed  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out-dir", default="results/baseline")
    parser.add_argument("--model-out", default="models_registry/baseline_svm.joblib")
    args = parser.parse_args()

    config = load_config(args.config)
    set_seed(config["seed"])

    splits_dir = Path(config["data"]["splits_dir"])
    train_pairs = pd.read_csv(splits_dir / "train_pairs.csv")
    val_pairs = pd.read_csv(splits_dir / "val_pairs.csv")
    test_pairs = pd.read_csv(splits_dir / "test_pairs.csv")

    target_size = tuple(config["image"]["size_scratch"])
    feature_type = config["baseline"]["feature_type"]
    denoise_method = config["preprocessing"]["denoise"]
    binarize_output = config["preprocessing"]["binarize_output"]

    print(f"[run_baseline] Extracting {feature_type} features for train/val/test...")
    X_train, y_train, _ = build_feature_matrix(train_pairs, feature_type, target_size, denoise_method, binarize_output)
    X_val, y_val, _ = build_feature_matrix(val_pairs, feature_type, target_size, denoise_method, binarize_output)
    X_test, y_test, forgery_test = build_feature_matrix(test_pairs, feature_type, target_size, denoise_method, binarize_output)

    print("[run_baseline] Grid-searching SVM (RBF) on train only...")
    svm = fit_svm(X_train, y_train, config["baseline"]["svm_param_grid"])

    val_scores = scores_from_svm(svm, X_val)
    test_scores = scores_from_svm(svm, X_test)

    tau = select_threshold(val_scores, y_val, method="eer")
    overall = evaluate_at_threshold(test_scores, y_test, tau)
    _, _, overall["auc"] = roc_auc(test_scores, y_test)
    by_type = evaluate_by_forgery_type(test_scores, y_test, forgery_test, tau)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = {"feature_type": feature_type, "tau": tau, "overall": overall, "by_forgery_type": by_type}
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"[run_baseline] Metrics written to {out_dir / 'metrics.json'}")
    print(json.dumps(metrics, indent=2))

    fig, ax = plt.subplots()
    for forgery_type in ("skilled_forgery", "random_forgery"):
        mask = (forgery_test == forgery_type) | (y_test == 1)
        fpr, tpr, auc = roc_auc(test_scores[mask], y_test[mask])
        ax.plot(fpr, tpr, label=f"{forgery_type} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"Baseline ({feature_type} + SVM) ROC")
    ax.legend()
    fig.savefig(out_dir / "roc.png", dpi=120)
    print(f"[run_baseline] ROC plot saved to {out_dir / 'roc.png'}")

    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(svm, model_path)
    print(f"[run_baseline] Model saved to {model_path}")


if __name__ == "__main__":
    main()
