"""Train Config A (from-scratch Siamese CNN): sweep margins {0.5, 1.0, 2.0},
pick the best by validation EER, evaluate the winner on test (skilled vs.
random forgery reported separately), and save every artefact the plan and
the demo app need.

Meant to be run where a GPU is available (Google Colab / Kaggle) with the
real CEDAR pairs already built via scripts/build_pairs.py -- see
notebooks/colab_train_siamese.ipynb for the end-to-end entrypoint.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt
import pandas as pd
import torch

from sigverify.evaluation.metrics import (  # noqa: E402
    compute_far_frr,
    evaluate_at_threshold,
    evaluate_by_forgery_type,
    roc_auc,
    select_threshold,
)
from sigverify.models.siamese_scratch import SiameseScratchCNN  # noqa: E402
from sigverify.training.train_siamese import compute_pair_scores, train_one_config  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402
from sigverify.utils.seed import set_seed  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out-dir", default="results/config_a")
    parser.add_argument("--model-out", default="models_registry/config_a_best.pt")
    parser.add_argument("--threshold-out", default="models_registry/config_a_threshold.json")
    args = parser.parse_args()

    config = load_config(args.config)
    set_seed(config["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[train_config_a] device={device}")

    splits_dir = Path(config["data"]["splits_dir"])
    train_pairs = pd.read_csv(splits_dir / "train_pairs.csv")
    val_pairs = pd.read_csv(splits_dir / "val_pairs.csv")
    test_pairs = pd.read_csv(splits_dir / "test_pairs.csv")

    target_size = tuple(config["image"]["size_scratch"])
    denoise_method = config["preprocessing"]["denoise"]
    binarize_output = config["preprocessing"]["binarize_output"]
    l2_normalize = config["model"]["l2_normalize"]
    embedding_dim = config["model"]["embedding_dim"]

    margin_sweep = {}
    best_margin, best_val_eer, best_state, best_history = None, float("inf"), None, None

    for margin in config["train"]["margins"]:
        print(f"[train_config_a] === margin={margin} ===")
        model = SiameseScratchCNN(embedding_dim=embedding_dim, l2_normalize=l2_normalize)
        state, history = train_one_config(
            model,
            train_pairs,
            val_pairs,
            target_size=target_size,
            mode="unit",
            margin=margin,
            lr=config["train"]["lr_scratch"],
            max_epochs=config["train"]["max_epochs"],
            patience=config["train"]["early_stop_patience"],
            warmup_epochs=config["train"]["early_stop_warmup_epochs"],
            batch_size=config["train"]["batch_size"],
            device=device,
            denoise_method=denoise_method,
            binarize_output=binarize_output,
        )
        margin_val_eer = min(h["val_eer"] for h in history)
        margin_sweep[str(margin)] = {"val_eer": margin_val_eer, "history": history}

        if margin_val_eer < best_val_eer:
            best_val_eer, best_margin, best_state, best_history = margin_val_eer, margin, state, history

    print(f"[train_config_a] Best margin={best_margin} (val_eer={best_val_eer:.4f})")

    model = SiameseScratchCNN(embedding_dim=embedding_dim, l2_normalize=l2_normalize)
    model.load_state_dict(best_state)
    model.to(device)

    val_scores, val_labels, _ = compute_pair_scores(
        model, val_pairs, target_size, "unit", denoise_method, binarize_output, device
    )
    tau = select_threshold(val_scores, val_labels, method="eer")

    test_scores, test_labels, test_forgery_types = compute_pair_scores(
        model, test_pairs, target_size, "unit", denoise_method, binarize_output, device
    )
    overall = evaluate_at_threshold(test_scores, test_labels, tau)
    _, _, overall["auc"] = roc_auc(test_scores, test_labels)
    by_type = evaluate_by_forgery_type(test_scores, test_labels, test_forgery_types, tau)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "best_margin": best_margin,
        "val_eer": best_val_eer,
        "tau": tau,
        "overall": overall,
        "by_forgery_type": by_type,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out_dir / "margin_sweep.json").write_text(json.dumps(margin_sweep, indent=2))
    print(json.dumps(metrics, indent=2))

    far, frr, thresholds = compute_far_frr(val_scores, val_labels)
    (out_dir / "far_frr_curve.json").write_text(
        json.dumps({"far": far.tolist(), "frr": frr.tolist(), "thresholds": thresholds.tolist()}, indent=2)
    )

    fig, ax = plt.subplots()
    for forgery_type in ("skilled_forgery", "random_forgery"):
        mask = (test_forgery_types == forgery_type) | (test_labels == 1)
        fpr, tpr, auc = roc_auc(test_scores[mask], test_labels[mask])
        ax.plot(fpr, tpr, label=f"{forgery_type} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"Config A (margin={best_margin}) ROC")
    ax.legend()
    fig.savefig(out_dir / "roc.png", dpi=120)

    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, model_path)
    print(f"[train_config_a] Model saved to {model_path}")

    threshold_path = Path(args.threshold_out)
    threshold_path.parent.mkdir(parents=True, exist_ok=True)
    threshold_path.write_text(json.dumps({"tau": tau, "margin": best_margin, "val_eer": best_val_eer}, indent=2))
    print(f"[train_config_a] Threshold saved to {threshold_path}")


if __name__ == "__main__":
    main()
