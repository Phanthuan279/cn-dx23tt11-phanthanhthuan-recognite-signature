"""Fetch or validate the BHSig260 signature dataset under data/raw/bhsig260/.

Same two-path approach as scripts/download_cedar.py: an optional automatic
Kaggle download (slug not hard-coded -- verify the mirror first), or a manual
fallback that just validates a layout you placed there yourself.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sigverify.preprocessing.datasets import list_bhsig260_signatures  # noqa: E402


def try_kaggle_download(slug: str, dest: Path) -> bool:
    dest.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["kaggle", "datasets", "download", "-d", slug, "-p", str(dest)], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"[download_bhsig260] Kaggle download failed or unavailable: {e}")
        return False

    zips = list(dest.glob("*.zip"))
    if not zips:
        print("[download_bhsig260] Kaggle download reported success but no zip found.")
        return False
    with zipfile.ZipFile(zips[0]) as zf:
        zf.extractall(dest)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", default="data/raw/bhsig260")
    parser.add_argument(
        "--kaggle-slug",
        default=None,
        help="Kaggle dataset slug for BHSig260. Not hard-coded: verify the correct public mirror first.",
    )
    parser.add_argument("--stats-out", default="results/eda/bhsig260_stats.json")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)

    if args.kaggle_slug:
        ok = try_kaggle_download(args.kaggle_slug, raw_dir)
        if not ok:
            print(
                "[download_bhsig260] Automatic download failed. Manual fallback: download "
                f"BHSig260 yourself and place it under {raw_dir}/ with 'Bengali/' and 'Hindi/' "
                "subdirectories, then re-run this script without --kaggle-slug to just validate."
            )

    try:
        df = list_bhsig260_signatures(raw_dir)
    except FileNotFoundError as e:
        print(f"[download_bhsig260] {e}")
        sys.exit(1)

    stats = {}
    for language, group in df.groupby("language"):
        stats[language] = {
            "n_writers": int(group["writer_id"].nunique()),
            "n_genuine": int((group["label"] == "genuine").sum()),
            "n_forged": int((group["label"] == "forged").sum()),
        }
    print(f"[download_bhsig260] {json.dumps(stats, indent=2)}")

    out_path = Path(args.stats_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(stats, indent=2))
    print(f"[download_bhsig260] Stats written to {out_path}")


if __name__ == "__main__":
    main()
