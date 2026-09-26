"""Fetch or validate the CEDAR signature dataset under data/raw/cedar/.

Two paths, in order:
  1. Automatic: `kaggle datasets download` if a Kaggle API token is configured
     and --kaggle-slug is given (no slug is hard-coded here since the exact
     public mirror was not verified at planning time -- pass it explicitly).
  2. Manual fallback: if data/raw/cedar/ already has the expected
     full_org/ + full_forg/ layout (e.g. you unzipped a manually downloaded
     copy there yourself), just validate and report stats.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sigverify.preprocessing.datasets import list_cedar_signatures  # noqa: E402


def try_kaggle_download(slug: str, dest: Path) -> bool:
    dest.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", slug, "-p", str(dest)],
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[download_cedar] Kaggle download failed or unavailable: {e}")
        return False

    zips = list(dest.glob("*.zip"))
    if not zips:
        print("[download_cedar] Kaggle download reported success but no zip found.")
        return False
    with zipfile.ZipFile(zips[0]) as zf:
        zf.extractall(dest)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="data/raw/cedar")
    parser.add_argument(
        "--kaggle-slug",
        default=None,
        help="Kaggle dataset slug, e.g. 'someuser/cedar-signature'. "
        "Not hard-coded: verify the correct public mirror before running.",
    )
    parser.add_argument("--stats-out", default="results/eda/cedar_stats.json")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)

    if args.kaggle_slug:
        ok = try_kaggle_download(args.kaggle_slug, raw_dir)
        if not ok:
            print(
                "[download_cedar] Automatic download failed. Manual fallback: "
                f"download CEDAR yourself and place it under {raw_dir}/ with "
                "'full_org/' and 'full_forg/' subdirectories, then re-run this script "
                "without --kaggle-slug to just validate."
            )

    try:
        df = list_cedar_signatures(raw_dir)
    except FileNotFoundError as e:
        print(f"[download_cedar] {e}")
        sys.exit(1)

    n_writers = df["writer_id"].nunique()
    stats = {
        "n_writers": int(n_writers),
        "n_genuine": int((df["label"] == "genuine").sum()),
        "n_forged": int((df["label"] == "forged").sum()),
        "genuine_per_writer": df[df.label == "genuine"].groupby("writer_id").size().to_dict(),
        "forged_per_writer": df[df.label == "forged"].groupby("writer_id").size().to_dict(),
    }
    print(f"[download_cedar] {n_writers} writers, {stats['n_genuine']} genuine, {stats['n_forged']} forged.")

    out_path = Path(args.stats_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(stats, indent=2))
    print(f"[download_cedar] Stats written to {out_path}")


if __name__ == "__main__":
    main()
