"""T6: train Config A's architecture with triplet loss instead of contrastive
loss, at the same margin used by the Phase 7 ablation variants (the middle of
the margin sweep, 1.0), and evaluate with the exact same protocol as
scripts/train_config_a.py so the two losses are directly comparable.

Triplets are built from the already writer-disjoint train/val pairs via
sigverify.pairs.generator.build_triplets_from_pairs -- no new images/pairs.
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
    build_predictions_dataframe,
    compute_far_frr,
    evaluate_at_threshold,
    evaluate_by_forgery_type,
    roc_auc,
    select_threshold,
)
from sigverify.models.siamese_scratch import SiameseScratchCNN  # noqa: E402
from sigverify.pairs.generator import build_triplets_from_pairs  # noqa: E402
from sigverify.training.train_siamese import compute_pair_scores  # noqa: E402
from sigverify.training.train_triplet import train_triplet_config  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402
from sigverify.utils.seed import set_seed  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out-dir", default="results/triplet")
    parser.add_argument("--model-out", default="models_registry/triplet_best.pt")
    args = parser.parse_args()

    config = load_config(args.config)
    set_seed(config["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[train_triplet] device={device}")

    splits_dir = Path(config["data"]["splits_dir"])
    train_pairs = pd.read_csv(splits_dir / "train_pairs.csv")
    val_pairs = pd.read_csv(splits_dir / "val_pairs.csv")
    test_pairs = pd.read_csv(splits_dir / "test_pairs.csv")
    train_triplets = build_triplets_from_pairs(train_pairs, seed=config["seed"])
    print(f"[train_triplet] {len(train_triplets)} triplets built from {len(train_pairs)} train pairs")

    target_size = tuple(config["image"]["size_scratch"])
    denoise_method = config["preprocessing"]["denoise"]
    binarize_output = config["preprocessing"]["binarize_output"]
    l2_normalize = config["model"]["l2_normalize"]
    embedding_dim = config["model"]["embedding_dim"]
    # Same convention as the Phase 7 ablation variants: fix margin at the
    # sweep's middle value instead of re-sweeping it for this comparison.
    margin = config["train"]["margins"][len(config["train"]["margins"]) // 2]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    model = SiameseScratchCNN(embedding_dim=embedding_dim, l2_normalize=l2_normalize)
    best_state, history = train_triplet_config(
        model,
        train_triplets,
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
        checkpoint_path=out_dir / "checkpoint.pt",
    )
    val_eer = min(h["val_eer"] for h in history) if history else None

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

    metrics = {
        "loss": "triplet",
        "margin": margin,
        "val_eer": val_eer,
        "tau": tau,
        "overall": overall,
        "by_forgery_type": by_type,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (out_dir / "history.json").write_text(json.dumps(history, indent=2))
    print(json.dumps(metrics, indent=2))

    far, frr, thresholds = compute_far_frr(val_scores, val_labels)
    (out_dir / "far_frr_curve.json").write_text(
        json.dumps({"far": far.tolist(), "frr": frr.tolist(), "thresholds": thresholds.tolist()}, indent=2)
    )

    predictions_df = build_predictions_dataframe(test_pairs, test_scores, tau)
    predictions_df.to_csv(out_dir / "predictions_test.csv", index=False)

    fig, ax = plt.subplots()
    for forgery_type in ("skilled_forgery", "random_forgery"):
        mask = (test_forgery_types == forgery_type) | (test_labels == 1)
        fpr, tpr, auc = roc_auc(test_scores[mask], test_labels[mask])
        ax.plot(fpr, tpr, label=f"{forgery_type} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"Triplet loss (margin={margin}) ROC")
    ax.legend()
    fig.savefig(out_dir / "roc.png", dpi=120)

    torch.save(best_state, model_path)
    print(f"[train_triplet] Model saved to {model_path}")


if __name__ == "__main__":
    main()
