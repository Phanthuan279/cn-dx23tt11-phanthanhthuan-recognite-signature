"""Dataset indexing: turn a raw dataset directory into a flat table of
(writer_id, sample_id, label, path) rows, used by pair generation (Phase 3)
and cross-dataset generalization (Phase 7).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

_CEDAR_GENUINE_RE = re.compile(r"original_(\d+)_(\d+)\.png$", re.IGNORECASE)
_CEDAR_FORGED_RE = re.compile(r"forgeries_(\d+)_(\d+)\.png$", re.IGNORECASE)


def list_cedar_signatures(raw_dir: str | Path) -> pd.DataFrame:
    """List every CEDAR signature image as (writer_id, sample_id, label, path).

    Expects the conventional CEDAR layout:
        <raw_dir>/full_org/original_<writer>_<sample>.png   (label="genuine")
        <raw_dir>/full_forg/forgeries_<writer>_<sample>.png (label="forged")

    Raises FileNotFoundError with a clear message if the expected
    subdirectories are missing, so a mismatched mirror layout is caught early
    instead of silently returning an empty/partial table.
    """
    raw_dir = Path(raw_dir)
    org_dir = raw_dir / "full_org"
    forg_dir = raw_dir / "full_forg"
    if not org_dir.is_dir() or not forg_dir.is_dir():
        raise FileNotFoundError(
            f"Expected CEDAR layout not found under {raw_dir}: "
            f"needs 'full_org/' and 'full_forg/' subdirectories. "
            f"See scripts/download_cedar.py for how to fetch/place the dataset."
        )

    rows = []
    for path in sorted(org_dir.glob("*.png")):
        m = _CEDAR_GENUINE_RE.search(path.name)
        if not m:
            continue
        writer_id, sample_id = int(m.group(1)), int(m.group(2))
        rows.append(
            {"writer_id": writer_id, "sample_id": sample_id, "label": "genuine", "path": str(path)}
        )
    for path in sorted(forg_dir.glob("*.png")):
        m = _CEDAR_FORGED_RE.search(path.name)
        if not m:
            continue
        writer_id, sample_id = int(m.group(1)), int(m.group(2))
        rows.append(
            {"writer_id": writer_id, "sample_id": sample_id, "label": "forged", "path": str(path)}
        )

    if not rows:
        raise FileNotFoundError(
            f"No CEDAR-style filenames matched under {raw_dir}. "
            f"Expected 'original_<writer>_<sample>.png' / 'forgeries_<writer>_<sample>.png'."
        )
    return pd.DataFrame(rows).sort_values(["writer_id", "label", "sample_id"]).reset_index(drop=True)
