"""Train Config B (transfer learning): stage 1 (frozen backbone, embedding
head only) then stage 2 (backbone's last block unfrozen at a lower lr),
repeated per margin, evaluated with the same frozen-threshold protocol as
Config A. Requires a GPU in practice (Colab/Kaggle) for a full CEDAR run.
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
from sigverify.models.siamese_transfer import SiameseTransferCNN  # noqa: E402
from sigverify.training.train_siamese import compute_pair_scores, train_one_config  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402
from sigverify.utils.seed import set_seed  # noqa: E402


def train_margin(config, train_pairs, val_pairs, margin, target_size, denoise_method, binarize_output, device):
    embedding_dim = config["model"]["embedding_dim"]
    backbone = config["model"]["transfer_backbone"]

    model = SiameseTransferCNN(embedding_dim=embedding_dim, backbone=backbone, pretrained=True)
    model.to(device)

    # Stage 1: frozen backbone, embedding head only
    model.freeze_backbone()
    _, stage1_history = train_one_config(
        model, train_pairs, val_pairs, target_size, "imagenet", margin,
        lr=config["train"]["lr_finetune_head"],
        max_epochs=config["train"]["finetune_stage1_epochs"],
        patience=config["train"]["finetune_stage1_epochs"] + 1,  # no early stop during stage 1
        warmup_epochs=0,
        batch_size=config["train"]["batch_size"],
        device=device,
        denoise_method=denoise_method,
        binarize_output=binarize_output,
    )

    # Stage 2: unfreeze last block, two learning rates
    model.unfreeze_last_block()
    optimizer = torch.optim.Adam(
        model.param_groups(
            lr_backbone=config["train"]["lr_finetune_backbone"],
            lr_head=config["train"]["lr_finetune_head"],
        )
    )
    best_state, stage2_history = train_one_config(
        model, train_pairs, val_pairs, target_size, "imagenet", margin,
        lr=config["train"]["lr_finetune_head"],  # unused: optimizer overrides it
        max_epochs=config["train"]["max_epochs"],
        patience=config["train"]["early_stop_patience"],
        warmup_epochs=config["train"]["early_stop_warmup_epochs"],
        batch_size=config["train"]["batch_size"],
        device=device,
        denoise_method=denoise_method,
        binarize_output=binarize_output,
        optimizer=optimizer,
    )
    val_eer = min(h["val_eer"] for h in stage2_history) if stage2_history else float("inf")
    return best_state, {"stage1": stage1_history, "stage2": stage2_history}, val_eer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out-dir", default="results/config_b")
    parser.add_argument("--model-out", default="models_registry/config_b_best.pt")
    parser.add_argument("--threshold-out", default="models_registry/config_b_threshold.json")
    args = parser.parse_args()

    config = load_config(args.config)
    set_seed(config["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[train_config_b] device={device}, backbone={config['model']['transfer_backbone']}")

    splits_dir = Path(config["data"]["splits_dir"])
    train_pairs = pd.read_csv(splits_dir / "train_pairs.csv")
    val_pairs = pd.read_csv(splits_dir / "val_pairs.csv")
    test_pairs = pd.read_csv(splits_dir / "test_pairs.csv")

    target_size = tuple(config["image"]["size_transfer"])
    denoise_method = config["preprocessing"]["denoise"]
    binarize_output = config["preprocessing"]["binarize_output"]

    margin_sweep = {}
    best_margin, best_val_eer, best_state = None, float("inf"), None

    for margin in config["train"]["margins"]:
        print(f"[train_config_b] === margin={margin} ===")
        state, history, val_eer = train_margin(
            config, train_pairs, val_pairs, margin, target_size, denoise_method, binarize_output, device
        )
        margin_sweep[str(margin)] = {"val_eer": val_eer, "history": history}
        if val_eer < best_val_eer:
            best_val_eer, best_margin, best_state = val_eer, margin, state

    print(f"[train_config_b] Best margin={best_margin} (val_eer={best_val_eer:.4f})")

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

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    metrics = {
        "backbone": config["model"]["transfer_backbone"],
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
    ax.set_title(f"Config B ({config['model']['transfer_backbone']}, margin={best_margin}) ROC")
    ax.legend()
    fig.savefig(out_dir / "roc.png", dpi=120)

    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, model_path)
    print(f"[train_config_b] Model saved to {model_path}")

    threshold_path = Path(args.threshold_out)
    threshold_path.parent.mkdir(parents=True, exist_ok=True)
    threshold_path.write_text(json.dumps({"tau": tau, "margin": best_margin, "val_eer": best_val_eer}, indent=2))


if __name__ == "__main__":
    main()
