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


# BHSig260 filenames follow the "<lang-prefix>-S-<writer>-<G|F>-<sample>.<ext>"
# convention of the commonly distributed mirror (B- for Bengali, H- for Hindi).
# [UNVERIFIED] the exact mirror layout was not confirmed at planning time --
# if a real download uses a different convention, this pattern (and/or the
# per-language subdirectory names below) will need a small update; the
# FileNotFoundError below is designed to surface that mismatch immediately
# rather than silently returning an empty/partial table.
_BHSIG260_RE = re.compile(r"[BH]-S-(\d+)-([GF])-(\d+)\.\w+$", re.IGNORECASE)
_BHSIG260_LANGUAGE_DIRS = {"bengali": "Bengali", "hindi": "Hindi"}
_BHSIG260_WRITER_ID_OFFSET = {"bengali": 0, "hindi": 100_000}


def list_bhsig260_signatures(raw_dir: str | Path, languages: tuple[str, ...] = ("bengali", "hindi")) -> pd.DataFrame:
    """List every BHSig260 signature image as (writer_id, sample_id, label, path, language).

    Bengali and Hindi are different signers, so Hindi writer_ids are offset by
    100000 to guarantee global uniqueness across the combined table (a plain
    "writer 1" from each language would otherwise collide and corrupt the
    writer-disjoint split logic from src/sigverify/pairs/splits.py).
    """
    raw_dir = Path(raw_dir)
    rows = []

    for language in languages:
        lang_dir = raw_dir / _BHSIG260_LANGUAGE_DIRS[language]
        if not lang_dir.is_dir():
            continue
        offset = _BHSIG260_WRITER_ID_OFFSET[language]
        for path in sorted(lang_dir.rglob("*")):
            if not path.is_file():
                continue
            m = _BHSIG260_RE.search(path.name)
            if not m:
                continue
            writer_num, label_code, sample_id = int(m.group(1)), m.group(2).upper(), int(m.group(3))
            rows.append(
                {
                    "writer_id": writer_num + offset,
                    "sample_id": sample_id,
                    "label": "genuine" if label_code == "G" else "forged",
                    "path": str(path),
                    "language": language,
                }
            )

    if not rows:
        raise FileNotFoundError(
            f"No BHSig260-style filenames matched under {raw_dir} for languages {languages}. "
            f"Expected '<raw_dir>/Bengali/.../B-S-<writer>-<G|F>-<sample>.<ext>' and/or "
            f"'<raw_dir>/Hindi/.../H-S-<writer>-<G|F>-<sample>.<ext>'. If your downloaded mirror "
            f"uses a different layout, update _BHSIG260_RE / _BHSIG260_LANGUAGE_DIRS above."
        )
    return pd.DataFrame(rows).sort_values(["writer_id", "label", "sample_id"]).reset_index(drop=True)
