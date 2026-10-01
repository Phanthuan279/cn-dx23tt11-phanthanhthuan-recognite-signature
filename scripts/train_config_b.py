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
    build_predictions_dataframe,
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


def train_margin(
    config, train_pairs, val_pairs, margin, target_size, denoise_method, binarize_output, device,
    checkpoint_dir=None,
):
    embedding_dim = config["model"]["embedding_dim"]
    backbone = config["model"]["transfer_backbone"]

    model = SiameseTransferCNN(embedding_dim=embedding_dim, backbone=backbone, pretrained=True)
    model.to(device)

    stage1_ckpt = Path(checkpoint_dir) / f"margin_{margin}_stage1.pt" if checkpoint_dir else None
    stage1_done = Path(checkpoint_dir) / f"margin_{margin}_stage1_done.pt" if checkpoint_dir else None
    stage2_ckpt = Path(checkpoint_dir) / f"margin_{margin}_stage2.pt" if checkpoint_dir else None

    # Stage 1: frozen backbone, embedding head only. finetune_stage1_epochs is
    # small and fixed (no early stop), so once it genuinely finishes it's cached
    # to stage1_done -- this environment's container can die right at the
    # stage1->stage2 boundary (stage2's first epoch is heavier and may not fit
    # in the same execution window), and without this cache every re-invocation
    # would redo all of stage1 from scratch before ever making it into stage2.
    if stage1_done is not None and stage1_done.exists():
        print(f"[train_config_b] Stage 1 already done for margin={margin}, reusing cached weights", flush=True)
        model.load_state_dict(torch.load(stage1_done, map_location=device))
        stage1_history = []
    else:
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
            checkpoint_path=stage1_ckpt,
        )
        if stage1_done is not None:
            torch.save(model.state_dict(), stage1_done)

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
        checkpoint_path=stage2_ckpt,
    )
    if stage1_done is not None:
        stage1_done.unlink(missing_ok=True)
    val_eer = min(h["val_eer"] for h in stage2_history) if stage2_history else float("inf")
    return best_state, {"stage1": stage1_history, "stage2": stage2_history}, val_eer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out-dir", default="results/config_b")
    parser.add_argument("--model-out", default="models_registry/config_b_best.pt")
    parser.add_argument("--threshold-out", default="models_registry/config_b_threshold.json")
    parser.add_argument(
        "--only-margin",
        type=float,
        default=None,
        help=(
            "Train exactly one margin and merge it into an existing margin_sweep.json "
            "(e.g. to finish a sweep interrupted partway through), instead of resweeping "
            "every margin in the config from scratch."
        ),
    )
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

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    model_path = Path(args.model_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    margin_sweep_path = out_dir / "margin_sweep.json"
    checkpoint_dir = out_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    margin_sweep = {}
    best_margin, best_val_eer, best_state = None, float("inf"), None

    margins_to_run = config["train"]["margins"]
    if args.only_margin is not None:
        # Resume mode: reuse whichever margins already finished (their history is
        # already trustworthy real data -- no need to retrain them), and only run
        # the one that's missing. The previously-saved best model is loaded as the
        # current champion so it can still win the final comparison below.
        if margin_sweep_path.exists():
            margin_sweep = json.loads(margin_sweep_path.read_text())
        for m_str, entry in margin_sweep.items():
            if entry["val_eer"] < best_val_eer:
                best_val_eer, best_margin = entry["val_eer"], float(m_str)
        if best_margin is not None and model_path.exists():
            best_state = torch.load(model_path, map_location=device)
        margins_to_run = [args.only_margin]

    for margin in margins_to_run:
        print(f"[train_config_b] === margin={margin} ===", flush=True)
        # Reseed before each margin (see the same fix in train_config_a.py):
        # otherwise margin N>1 inherits whatever random state margin N-1's
        # training left behind, confounding the comparison between margins.
        set_seed(config["seed"])
        state, history, val_eer = train_margin(
            config, train_pairs, val_pairs, margin, target_size, denoise_method, binarize_output, device,
            checkpoint_dir=checkpoint_dir,
        )
        margin_sweep[str(margin)] = {"val_eer": val_eer, "history": history}
        margin_sweep_path.write_text(json.dumps(margin_sweep, indent=2))

        if val_eer < best_val_eer:
            best_val_eer, best_margin, best_state = val_eer, margin, state
            torch.save(best_state, model_path.with_name(model_path.stem + "_checkpoint" + model_path.suffix))
            print(
                f"[train_config_b] Checkpoint: margin={margin} is best so far "
                f"(val_eer={val_eer:.4f}), saved to {model_path.stem}_checkpoint{model_path.suffix}",
                flush=True,
            )

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

    predictions_df = build_predictions_dataframe(test_pairs, test_scores, tau)
    predictions_df.to_csv(out_dir / "predictions_test.csv", index=False)
    print(f"[train_config_b] Per-pair predictions saved to {out_dir / 'predictions_test.csv'}")

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

    torch.save(best_state, model_path)
    print(f"[train_config_b] Model saved to {model_path}")

    threshold_path = Path(args.threshold_out)
    threshold_path.parent.mkdir(parents=True, exist_ok=True)
    threshold_path.write_text(json.dumps({"tau": tau, "margin": best_margin, "val_eer": best_val_eer}, indent=2))


if __name__ == "__main__":
    main()
