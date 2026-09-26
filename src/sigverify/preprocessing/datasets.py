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


def _find_dir(raw_dir: Path, name: str) -> Path | None:
    """Find a directory named `name` directly under raw_dir, or anywhere
    beneath it (mirrors sometimes nest the real payload one level deeper,
    e.g. Kaggle's shreelakshmigp/cedardataset puts it under 'signatures/').
    """
    direct = raw_dir / name
    if direct.is_dir():
        return direct
    return next((p for p in raw_dir.rglob(name) if p.is_dir()), None)


def list_cedar_signatures(raw_dir: str | Path) -> pd.DataFrame:
    """List every CEDAR signature image as (writer_id, sample_id, label, path).

    Expects the conventional CEDAR layout (searched for at any depth under
    raw_dir, since Kaggle mirrors commonly nest it under a 'signatures/'
    folder):
        .../full_org/original_<writer>_<sample>.png   (label="genuine")
        .../full_forg/forgeries_<writer>_<sample>.png (label="forged")

    Raises FileNotFoundError with a clear message if the expected
    subdirectories are missing, so a mismatched mirror layout is caught early
    instead of silently returning an empty/partial table.
    """
    raw_dir = Path(raw_dir)
    org_dir = _find_dir(raw_dir, "full_org")
    forg_dir = _find_dir(raw_dir, "full_forg")
    if org_dir is None or forg_dir is None:
        raise FileNotFoundError(
            f"Expected CEDAR layout not found under {raw_dir}: "
            f"needs 'full_org/' and 'full_forg/' subdirectories (at any depth). "
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
# convention (B- for Bengali, H- for Hindi), confirmed against the
# nth2165/bhsig260-hindi-bengali Kaggle mirror. That mirror's top-level
# language folders are named "BHSig100_Bengali" / "BHSig160_Hindi" (100 and
# 160 being the per-language writer counts that sum to 260), with genuine and
# forged samples split into further "Genuine"/"Forged" subdirectories -- the
# language-folder lookup below matches by substring so it tolerates that
# "BHSig<N>_" prefix (and other mirrors that might drop it), and rglob("*")
# already recurses through the Genuine/Forged split without needing to know
# about it explicitly.
_BHSIG260_RE = re.compile(r"[BH]-S-(\d+)-([GF])-(\d+)\.\w+$", re.IGNORECASE)
_BHSIG260_WRITER_ID_OFFSET = {"bengali": 0, "hindi": 100_000}


def _find_language_dir(raw_dir: Path, language: str) -> Path | None:
    """Find the top-level directory for a BHSig260 language by substring match
    (case-insensitive), tolerating prefixes like "BHSig100_Bengali".
    """
    if not raw_dir.is_dir():
        return None
    for child in raw_dir.iterdir():
        if child.is_dir() and language.lower() in child.name.lower():
            return child
    return None


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
        lang_dir = _find_language_dir(raw_dir, language)
        if lang_dir is None:
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
            f"Expected a directory whose name contains 'bengali' and/or 'hindi' (any depth under "
            f"{raw_dir}), containing files like 'B-S-<writer>-<G|F>-<sample>.<ext>' / "
            f"'H-S-<writer>-<G|F>-<sample>.<ext>'. If your downloaded mirror uses a different "
            f"naming convention, update _BHSIG260_RE above."
        )
    return pd.DataFrame(rows).sort_values(["writer_id", "label", "sample_id"]).reset_index(drop=True)
