"""Recovery utility: finalize Config B evaluation from an already-saved
best-margin checkpoint, without re-running the margin sweep.

Used when a full train_config_b.py sweep was interrupted (e.g. container
restart) after at least one margin had already been checkpointed via
models_registry/config_b_best_checkpoint.pt + results/config_b/margin_sweep.json.
Not part of the normal pipeline -- scripts/train_config_b.py is still the
correct way to run a fresh sweep.
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
from sigverify.models.siamese_transfer import SiameseTransferCNN  # noqa: E402
from sigverify.training.train_siamese import compute_pair_scores  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--checkpoint", default="models_registry/config_b_best_checkpoint.pt")
    parser.add_argument("--margin-sweep", default="results/config_b/margin_sweep.json")
    parser.add_argument("--best-margin", type=float, required=True)
    parser.add_argument("--out-dir", default="results/config_b")
    parser.add_argument("--model-out", default="models_registry/config_b_best.pt")
    parser.add_argument("--threshold-out", default="models_registry/config_b_threshold.json")
    args = parser.parse_args()

    config = load_config(args.config)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    splits_dir = Path(config["data"]["splits_dir"])
    val_pairs = pd.read_csv(splits_dir / "val_pairs.csv")
    test_pairs = pd.read_csv(splits_dir / "test_pairs.csv")

    target_size = tuple(config["image"]["size_transfer"])
    denoise_method = config["preprocessing"]["denoise"]
    binarize_output = config["preprocessing"]["binarize_output"]

    best_state = torch.load(args.checkpoint, map_location=device)
    model = SiameseTransferCNN(
        embedding_dim=config["model"]["embedding_dim"],
        backbone=config["model"]["transfer_backbone"],
        pretrained=False,
    )
    model.load_state_dict(best_state)
    model.to(device)

    val_scores, val_labels, _ = compute_pair_scores(
        model, val_pairs, target_size, "imagenet", denoise_method, binarize_output, device
    )
    tau = select_threshold(val_scores, val_labels, method="eer")

    test_scores, test_labels, test_forgery_types = compute_pair_scores(
        model, test_pairs, target_size, "imagenet", denoise_method, binarize_output, device
    )
    overall = evaluate_at_threshold(test_scores, test_labels, tau)
    _, _, overall["auc"] = roc_auc(test_scores, test_labels)
    by_type = evaluate_by_forgery_type(test_scores, test_labels, test_forgery_types, tau)

    margin_sweep = json.loads(Path(args.margin_sweep).read_text())
    best_val_eer = margin_sweep[str(args.best_margin)]["val_eer"]

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "backbone": config["model"]["transfer_backbone"],
        "best_margin": args.best_margin,
        "val_eer": best_val_eer,
        "tau": tau,
        "overall": overall,
        "by_forgery_type": by_type,
        "note": "Finalized from a checkpoint after the margin sweep was interrupted "
        "(container restart) partway through the last margin; see margin_sweep.json "
        "for exactly which margins completed.",
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))

    far, frr, thresholds = compute_far_frr(val_scores, val_labels)
    (out_dir / "far_frr_curve.json").write_text(
        json.dumps({"far": far.tolist(), "frr": frr.tolist(), "thresholds": thresholds.tolist()}, indent=2)
    )

    predictions_df = build_predictions_dataframe(test_pairs, test_scores, tau)
    predictions_df.to_csv(out_dir / "predictions_test.csv", index=False)
    print(f"[finalize_config_b] Per-pair predictions saved to {out_dir / 'predictions_test.csv'}")

    fig, ax = plt.subplots()
    for forgery_type in ("skilled_forgery", "random_forgery"):
        mask = (test_forgery_types == forgery_type) | (test_labels == 1)
        fpr, tpr, auc = roc_auc(test_scores[mask], test_labels[mask])
        ax.plot(fpr, tpr, label=f"{forgery_type} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.3)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(f"Config B ({config['model']['transfer_backbone']}, margin={args.best_margin}) ROC")
    ax.legend()
    fig.savefig(out_dir / "roc.png", dpi=120)

    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, model_path)
    print(f"[finalize_config_b] Model saved to {model_path}")

    threshold_path = Path(args.threshold_out)
    threshold_path.parent.mkdir(parents=True, exist_ok=True)
    threshold_path.write_text(json.dumps({"tau": tau, "margin": args.best_margin, "val_eer": best_val_eer}, indent=2))
    print(f"[finalize_config_b] Threshold saved to {threshold_path}")


if __name__ == "__main__":
    main()
