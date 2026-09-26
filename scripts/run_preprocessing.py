"""Visualize the preprocessing pipeline on a handful of CEDAR samples:
saves an original-vs-preprocessed grid to results/eda/preprocessing_samples.png.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib.pyplot as plt

from sigverify.preprocessing.datasets import list_cedar_signatures  # noqa: E402
from sigverify.preprocessing.pipeline import load_grayscale, preprocess_image  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--n-samples", type=int, default=6)
    parser.add_argument("--out", default="results/eda/preprocessing_samples.png")
    args = parser.parse_args()

    config = load_config(args.config)
    df = list_cedar_signatures(config["data"]["cedar_dir"])

    random.seed(config["seed"])
    sample_rows = df.sample(n=min(args.n_samples, len(df)), random_state=config["seed"])

    target_size = tuple(config["image"]["size_scratch"])
    fig, axes = plt.subplots(len(sample_rows), 2, figsize=(6, 3 * len(sample_rows)))
    if len(sample_rows) == 1:
        axes = [axes]

    for ax_row, (_, row) in zip(axes, sample_rows.iterrows()):
        original = load_grayscale(row["path"])
        processed = preprocess_image(
            row["path"],
            target_size,
            mode="unit",
            denoise_method=config["preprocessing"]["denoise"],
            binarize_output=config["preprocessing"]["binarize_output"],
        ).squeeze(-1)

        ax_row[0].imshow(original, cmap="gray")
        ax_row[0].set_title(f"Gốc (writer {row['writer_id']}, {row['label']})")
        ax_row[0].axis("off")
        ax_row[1].imshow(processed, cmap="gray", vmin=0, vmax=1)
        ax_row[1].set_title("Đã tiền xử lý")
        ax_row[1].axis("off")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    print(f"[run_preprocessing] Saved {out_path}")


if __name__ == "__main__":
    main()
