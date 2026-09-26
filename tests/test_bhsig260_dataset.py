import tempfile
from pathlib import Path

import pytest

from sigverify.preprocessing.datasets import list_bhsig260_signatures


def _make_fake_bhsig260(root: Path) -> None:
    bengali = root / "Bengali" / "001"
    hindi = root / "Hindi" / "001"
    bengali.mkdir(parents=True)
    hindi.mkdir(parents=True)

    for i in range(1, 4):
        (bengali / f"B-S-1-G-{i:02d}.tif").touch()
    for i in range(1, 3):
        (bengali / f"B-S-1-F-{i:02d}.tif").touch()
    for i in range(1, 4):
        (hindi / f"H-S-1-G-{i:02d}.tif").touch()
    for i in range(1, 3):
        (hindi / f"H-S-1-F-{i:02d}.tif").touch()


def test_list_bhsig260_signatures_parses_both_languages_with_disjoint_writer_ids():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_fake_bhsig260(root)
        df = list_bhsig260_signatures(root)

        assert set(df["language"].unique()) == {"bengali", "hindi"}
        # writer 1 in each language must map to DIFFERENT global writer_id values
        bengali_writer_ids = set(df[df.language == "bengali"]["writer_id"])
        hindi_writer_ids = set(df[df.language == "hindi"]["writer_id"])
        assert bengali_writer_ids.isdisjoint(hindi_writer_ids)

        assert (df["label"] == "genuine").sum() == 6
        assert (df["label"] == "forged").sum() == 4


def test_list_bhsig260_signatures_raises_clear_error_on_missing_layout():
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(FileNotFoundError):
            list_bhsig260_signatures(Path(tmp))
