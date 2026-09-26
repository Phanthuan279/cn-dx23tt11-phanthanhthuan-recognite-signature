"""Build the writer-disjoint split and the train/val/test pair CSVs for CEDAR.

Val and test pairs are generated ONCE and saved (not regenerated every epoch)
so evaluation is reproducible; only train pairs are meant to be resampled
per-epoch by the training loop (Phase 5/6).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sigverify.pairs.generator import generate_pairs, pairs_to_dataframe  # noqa: E402
from sigverify.pairs.splits import save_split, writer_disjoint_split  # noqa: E402
from sigverify.preprocessing.datasets import list_cedar_signatures  # noqa: E402
from sigverify.utils.config import load_config  # noqa: E402
from sigverify.utils.seed import set_seed  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/default.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    set_seed(config["seed"])

    df = list_cedar_signatures(config["data"]["cedar_dir"])
    writer_ids = sorted(df["writer_id"].unique().tolist())

    split = writer_disjoint_split(
        writer_ids,
        n_train=config["split"]["train_writers"],
        n_val=config["split"]["val_writers"],
        n_test=config["split"]["test_writers"],
        seed=config["seed"],
    )
    split_path = Path(config["data"]["splits_dir"]) / "cedar_writer_split.json"
    save_split(split, split_path)
    print(f"[build_pairs] Writer split saved to {split_path}: "
          f"{len(split['train'])} train / {len(split['val'])} val / {len(split['test'])} test writers")

    ratio = tuple(config["pairs"]["ratio_pos_hardneg_easyneg"])
    pairs_per_writer = config["pairs"]["pairs_per_writer"]

    for split_name in ("train", "val", "test"):
        pairs = generate_pairs(
            df, split[split_name],
            ratio=ratio, pairs_per_writer=pairs_per_writer, seed=config["seed"],
        )
        out_df = pairs_to_dataframe(pairs)
        out_path = Path(config["data"]["splits_dir"]) / f"{split_name}_pairs.csv"
        out_df.to_csv(out_path, index=False)
        print(f"[build_pairs] {split_name}: {len(out_df)} pairs -> {out_path} "
              f"({out_df['forgery_type'].value_counts().to_dict()})")


if __name__ == "__main__":
    main()
