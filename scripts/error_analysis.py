"""Find and visualize the pairs the model got wrong (false accepts and false
rejects, split by skilled/random forgery), for the thesis error-analysis
section. Reads the predictions_*.csv files that train_config_a.py /
train_config_b.py / run_ablations.py save via
sigverify.evaluation.metrics.build_predictions_dataframe.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt
import pandas as pd

from sigverify.preprocessing.pipeline import load_grayscale, preprocess_image  # noqa: E402


def _error_type(row: pd.Series) -> str | None:
    if row["label"] == 1 and row["prediction"] == 0:
        return "false_reject"
    if row["label"] == 0 and row["prediction"] == 1:
        return "false_accept"
    return None


def find_top_errors(predictions_df: pd.DataFrame, top_k: int = 20) -> pd.DataFrame:
    """Return the top_k most severe misclassified pairs per (forgery_type,
    error_type) group, sorted by |score - tau_used| descending (the clearest,
    most surprising mistakes first).
    """
    df = predictions_df.copy()
    df["error_type"] = df.apply(_error_type, axis=1)
    errors = df[df["error_type"].notna()].copy()
    if errors.empty:
        return errors.assign(severity=[])

    errors["severity"] = (errors["score"] - errors["tau_used"]).abs()

    # Iterate groups explicitly rather than groupby(...).apply(...): pandas'
    # apply can silently drop the grouping columns from the result when the
    # applied function returns a same-shaped frame, which would delete the
    # forgery_type/error_type columns callers need downstream.
    top_per_group = [
        group.nlargest(min(top_k, len(group)), "severity")
        for _, group in errors.groupby(["forgery_type", "error_type"])
    ]
    return pd.concat(top_per_group, ignore_index=True)


def render_case(case_row: pd.Series, target_size: tuple[int, int], mode: str, out_path: Path) -> None:
    """Save a 2x2 grid: original A, original B, preprocessed A, preprocessed B,
    annotated with D, tau, true label and prediction.
    """
    original_a = load_grayscale(case_row["path_a"])
    original_b = load_grayscale(case_row["path_b"])
    processed_a = preprocess_image(case_row["path_a"], target_size, mode).squeeze()
    processed_b = preprocess_image(case_row["path_b"], target_size, mode).squeeze()
    if processed_a.ndim == 3:  # imagenet mode -> take one channel for display
        processed_a, processed_b = processed_a[..., 0], processed_b[..., 0]

    fig, axes = plt.subplots(2, 2, figsize=(6, 6))
    axes[0, 0].imshow(original_a, cmap="gray")
    axes[0, 0].set_title("Gốc A")
    axes[0, 1].imshow(original_b, cmap="gray")
    axes[0, 1].set_title("Gốc B")
    axes[1, 0].imshow(processed_a, cmap="gray")
    axes[1, 0].set_title("Đã xử lý A")
    axes[1, 1].imshow(processed_b, cmap="gray")
    axes[1, 1].set_title("Đã xử lý B")
    for ax in axes.ravel():
        ax.axis("off")

    label_str = "Thật (cùng người)" if case_row["label"] == 1 else "Giả/khác người"
    pred_str = "Thật" if case_row["prediction"] == 1 else "Giả"
    fig.suptitle(
        f"{case_row['forgery_type']} | nhãn={label_str} | dự đoán={pred_str}\n"
        f"D={case_row['score']:.4f}, τ={case_row['tau_used']:.4f}"
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, help="Path to a predictions_*.csv file")
    parser.add_argument("--dataset-name", default="cedar_test", help="Subfolder name under results/error_analysis/")
    parser.add_argument("--target-width", type=int, default=220)
    parser.add_argument("--target-height", type=int, default=150)
    parser.add_argument("--mode", default="unit", choices=["unit", "imagenet"])
    parser.add_argument("--top-k", type=int, default=20)
    args = parser.parse_args()

    predictions_df = pd.read_csv(args.predictions)
    top_errors = find_top_errors(predictions_df, top_k=args.top_k)

    if top_errors.empty:
        print(f"[error_analysis] No misclassified pairs found in {args.predictions} -- nothing to render.")
        return

    out_dir = Path("results/error_analysis") / args.dataset_name
    target_size = (args.target_width, args.target_height)
    for i, (_, row) in enumerate(top_errors.iterrows()):
        case_id = f"{row['forgery_type']}_{row['error_type']}_{i:03d}"
        render_case(row, target_size, args.mode, out_dir / f"{case_id}.png")

    print(f"[error_analysis] Rendered {len(top_errors)} error cases to {out_dir}")
    print(top_errors.groupby(["forgery_type", "error_type"]).size())


if __name__ == "__main__":
    main()
