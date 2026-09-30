"""Two things, both reusing the Phase 2/3/5 infrastructure unchanged:

1. Ablation sweep: retrain Config A with exactly one setting changed at a
   time (configs/ablation_variants/*.yaml), on the SAME CEDAR writer-disjoint
   split, to isolate the effect of tight-crop, binarization, augmentation,
   and embedding L2-normalization.
2. Cross-dataset generalization: apply the already-trained CEDAR Config A
   model to BHSig260 ZERO-SHOT (no fine-tuning), reusing the exact tau
   frozen from CEDAR validation -- this is the writer-independence claim's
   actual test. The baseline SVM is run the same way for a fair comparison.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import joblib
import numpy as np
import pandas as pd
import torch

from sigverify.evaluation.metrics import (  # noqa: E402
    build_predictions_dataframe,
    evaluate_at_threshold,
    evaluate_by_forgery_type,
    roc_auc,
    select_threshold,
)
from sigverify.features.handcrafted import extract_feature  # noqa: E402
from sigverify.models.siamese_scratch import SiameseScratchCNN  # noqa: E402
from sigverify.pairs.generator import generate_pairs, pairs_to_dataframe  # noqa: E402
from sigverify.preprocessing.datasets import list_bhsig260_signatures  # noqa: E402
from sigverify.preprocessing.pipeline import preprocess_image  # noqa: E402
from sigverify.training.train_siamese import compute_pair_scores, train_one_config  # noqa: E402
from sigverify.utils.config import load_config, load_config_with_override  # noqa: E402
from sigverify.utils.seed import set_seed  # noqa: E402

ABLATION_VARIANTS = {
    "no_bbox_crop": "configs/ablation_variants/no_bbox_crop.yaml",
    "binarize_output": "configs/ablation_variants/binarize_output.yaml",
    "image_size": "configs/ablation_variants/image_size.yaml",
    "no_augmentation": "configs/ablation_variants/no_augmentation.yaml",
    "l2_normalize": "configs/ablation_variants/l2_normalize.yaml",
}

EER_TARGET_BHSIG260 = 0.20


def run_variant(
    name: str,
    config: dict,
    train_pairs: pd.DataFrame,
    val_pairs: pd.DataFrame,
    test_pairs: pd.DataFrame,
    device: torch.device,
    out_dir: Path,
) -> dict:
    target_size = tuple(config["image"]["size_scratch"])
    denoise_method = config["preprocessing"]["denoise"]
    binarize_output = config["preprocessing"]["binarize_output"]
    crop_to_bbox = config["preprocessing"]["crop_to_bbox"]
    augmentation_enabled = config["train"]["augmentation_enabled"]
    l2_normalize = config["model"]["l2_normalize"]
    # Ablation runs isolate ONE preprocessing/training variable, so they fix
    # margin at the middle of the sweep instead of re-sweeping it too.
    margin = config["train"]["margins"][len(config["train"]["margins"]) // 2]

    out_dir.mkdir(parents=True, exist_ok=True)
    model = SiameseScratchCNN(embedding_dim=config["model"]["embedding_dim"], l2_normalize=l2_normalize)
    _, history = train_one_config(
        model, train_pairs, val_pairs, target_size, "unit", margin,
        lr=config["train"]["lr_scratch"],
        max_epochs=config["train"]["max_epochs"],
        patience=config["train"]["early_stop_patience"],
        warmup_epochs=config["train"]["early_stop_warmup_epochs"],
        batch_size=config["train"]["batch_size"],
        device=device,
        denoise_method=denoise_method,
        binarize_output=binarize_output,
        crop_to_bbox=crop_to_bbox,
        augmentation_enabled=augmentation_enabled,
        checkpoint_path=out_dir / "checkpoint.pt",
    )

    val_scores, val_labels, _ = compute_pair_scores(
        model, val_pairs, target_size, "unit", denoise_method, binarize_output, device, crop_to_bbox=crop_to_bbox
    )
    tau = select_threshold(val_scores, val_labels, method="eer")

    test_scores, test_labels, test_forgery = compute_pair_scores(
        model, test_pairs, target_size, "unit", denoise_method, binarize_output, device, crop_to_bbox=crop_to_bbox
    )
    overall = evaluate_at_threshold(test_scores, test_labels, tau)
    by_type = evaluate_by_forgery_type(test_scores, test_labels, test_forgery, tau)

    metrics = {
        "variant": name,
        "margin": margin,
        "val_eer": min(h["val_eer"] for h in history) if history else None,
        "tau": tau,
        "overall": overall,
        "by_forgery_type": by_type,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    return metrics


def run_ablation_sweep(
    config_path: str, train_pairs, val_pairs, test_pairs, device, variants: list[str] | None = None
) -> dict:
    summary_path = Path("results/ablations/summary.json")
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}

    default_metrics_path = Path("results/config_a/metrics.json")
    if default_metrics_path.exists():
        summary["default"] = json.loads(default_metrics_path.read_text())
    else:
        print(
            "[run_ablations] WARNING: results/config_a/metrics.json not found -- "
            "run scripts/train_config_a.py first to get the 'default' comparison row."
        )

    selected = {name: ABLATION_VARIANTS[name] for name in variants} if variants else ABLATION_VARIANTS
    for name, override_path in selected.items():
        print(f"[run_ablations] === variant: {name} ===")
        config = load_config_with_override(config_path, override_path)
        out_dir = Path("results/ablations") / name
        summary[name] = run_variant(name, config, train_pairs, val_pairs, test_pairs, device, out_dir)

    Path("results/ablations").mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2))
    print("[run_ablations] Summary written to results/ablations/summary.json")
    return summary


def evaluate_siamese_zero_shot(base_config: dict, bhsig260_df: pd.DataFrame, device: torch.device) -> dict | None:
    model_path = Path("models_registry/config_a_best.pt")
    threshold_path = Path("models_registry/config_a_threshold.json")
    if not model_path.exists() or not threshold_path.exists():
        print(
            "[run_ablations] WARNING: trained Config A model/threshold not found -- "
            "run scripts/train_config_a.py first. Skipping Siamese cross-dataset generalization."
        )
        return None

    tau = json.loads(threshold_path.read_text())["tau"]
    model = SiameseScratchCNN(
        embedding_dim=base_config["model"]["embedding_dim"], l2_normalize=base_config["model"]["l2_normalize"]
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)

    target_size = tuple(base_config["image"]["size_scratch"])
    writer_ids = sorted(bhsig260_df["writer_id"].unique().tolist())
    pairs = generate_pairs(
        bhsig260_df, writer_ids,
        ratio=tuple(base_config["pairs"]["ratio_pos_hardneg_easyneg"]),
        pairs_per_writer=base_config["pairs"]["pairs_per_writer"],
        seed=base_config["seed"],
    )
    pairs_df = pairs_to_dataframe(pairs)

    scores, labels, forgery_types = compute_pair_scores(
        model, pairs_df, target_size, "unit",
        base_config["preprocessing"]["denoise"], base_config["preprocessing"]["binarize_output"], device,
        crop_to_bbox=base_config["preprocessing"]["crop_to_bbox"],
    )
    overall = evaluate_at_threshold(scores, labels, tau)
    _, _, overall["auc"] = roc_auc(scores, labels)
    by_type = evaluate_by_forgery_type(scores, labels, forgery_types, tau)

    result = {"tau_from_cedar": tau, "overall": overall, "by_forgery_type": by_type}
    Path("results/generalization_bhsig260_siamese_raw.json").write_text(json.dumps(result, indent=2))

    predictions_dir = Path("results/config_a")
    predictions_dir.mkdir(parents=True, exist_ok=True)
    build_predictions_dataframe(pairs_df, scores, tau).to_csv(predictions_dir / "predictions_bhsig260.csv", index=False)

    return result


def evaluate_baseline_zero_shot(base_config: dict, bhsig260_df: pd.DataFrame) -> dict | None:
    model_path = Path("models_registry/baseline_svm.joblib")
    metrics_path = Path("results/baseline/metrics.json")
    if not model_path.exists():
        print("[run_ablations] WARNING: baseline SVM not found -- run scripts/run_baseline.py first. Skipping.")
        return None

    svm = joblib.load(model_path)
    target_size = tuple(base_config["image"]["size_scratch"])
    feature_type = base_config["baseline"]["feature_type"]
    denoise_method = base_config["preprocessing"]["denoise"]
    binarize_output = base_config["preprocessing"]["binarize_output"]
    crop_to_bbox = base_config["preprocessing"]["crop_to_bbox"]

    writer_ids = sorted(bhsig260_df["writer_id"].unique().tolist())
    pairs = generate_pairs(
        bhsig260_df, writer_ids,
        ratio=tuple(base_config["pairs"]["ratio_pos_hardneg_easyneg"]),
        pairs_per_writer=base_config["pairs"]["pairs_per_writer"],
        seed=base_config["seed"],
    )
    pairs_df = pairs_to_dataframe(pairs)

    features = []
    for _, row in pairs_df.iterrows():
        img_a = preprocess_image(row["path_a"], target_size, "unit", denoise_method, binarize_output, crop_to_bbox)
        img_b = preprocess_image(row["path_b"], target_size, "unit", denoise_method, binarize_output, crop_to_bbox)
        features.append(np.abs(extract_feature(img_a, feature_type) - extract_feature(img_b, feature_type)))
    X = np.array(features)
    scores = -svm.decision_function(X)
    labels = pairs_df["label"].to_numpy()
    forgery_types = pairs_df["forgery_type"].to_numpy()

    tau = json.loads(metrics_path.read_text())["tau"] if metrics_path.exists() else select_threshold(scores, labels)
    overall = evaluate_at_threshold(scores, labels, tau)
    by_type = evaluate_by_forgery_type(scores, labels, forgery_types, tau)

    result = {"tau_from_cedar": tau, "overall": overall, "by_forgery_type": by_type}
    Path("results/generalization_bhsig260_baseline_raw.json").write_text(json.dumps(result, indent=2))
    return result


def _format_result(result: dict | None) -> str:
    if result is None:
        return "_(chưa chạy -- xem cảnh báo ở log)_"
    skilled = result["by_forgery_type"].get("skilled_forgery")
    random_ = result["by_forgery_type"].get("random_forgery")
    lines = []
    if skilled:
        eer_est = (skilled["far"] + skilled["frr"]) / 2
        verdict = "ĐẠT" if eer_est <= EER_TARGET_BHSIG260 else "CHƯA ĐẠT"
        lines.append(
            f"- Skilled forgery: FAR={skilled['far']:.4f}, FRR={skilled['frr']:.4f}, "
            f"AUC={skilled['auc']:.4f} -> {verdict} (mục tiêu EER≤20%)"
        )
    if random_:
        lines.append(f"- Random forgery: FAR={random_['far']:.4f}, FRR={random_['frr']:.4f}, AUC={random_['auc']:.4f}")
    return "\n".join(lines) if lines else "_(không có dữ liệu)_"


def write_generalization_report(siamese_result, baseline_result, out_path: Path) -> None:
    lines = [
        "# Kiểm tra tổng quát zero-shot trên BHSig260",
        "",
        "Mô hình Config A huấn luyện trên CEDAR được áp thẳng lên BHSig260 **không fine-tune lại**, "
        "dùng đúng ngưỡng τ đã đóng băng từ CEDAR validation. Đây là phép thử trực tiếp cho tuyên bố "
        "writer-independent của đồ án.",
        "",
        "## Siamese (Config A)",
        _format_result(siamese_result),
        "",
        "## Baseline (HOG/LBP + SVM)",
        _format_result(baseline_result),
    ]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n")
    print(f"[run_ablations] Generalization report written to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--skip-ablations", action="store_true")
    parser.add_argument("--skip-cross-dataset", action="store_true")
    parser.add_argument(
        "--variants",
        default=None,
        help=f"Comma-separated subset of {list(ABLATION_VARIANTS)} to run (default: all).",
    )
    args = parser.parse_args()
    variants = args.variants.split(",") if args.variants else None

    base_config = load_config(args.config)
    set_seed(base_config["seed"])
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if not args.skip_ablations:
        splits_dir = Path(base_config["data"]["splits_dir"])
        train_pairs = pd.read_csv(splits_dir / "train_pairs.csv")
        val_pairs = pd.read_csv(splits_dir / "val_pairs.csv")
        test_pairs = pd.read_csv(splits_dir / "test_pairs.csv")
        run_ablation_sweep(args.config, train_pairs, val_pairs, test_pairs, device, variants)

    if not args.skip_cross_dataset:
        try:
            bhsig260_df = list_bhsig260_signatures(base_config["data"]["bhsig260_dir"])
        except FileNotFoundError as e:
            print(f"[run_ablations] {e}")
            return

        siamese_result = evaluate_siamese_zero_shot(base_config, bhsig260_df, device)
        baseline_result = evaluate_baseline_zero_shot(base_config, bhsig260_df)
        write_generalization_report(siamese_result, baseline_result, Path("results/generalization_bhsig260.md"))


if __name__ == "__main__":
    main()
