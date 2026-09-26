"""Writer-disjoint train/val/test split: no writer_id ever appears in more
than one of {train, val, test}, so no signer's handwriting style leaks
across the evaluation boundary.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Sequence


def writer_disjoint_split(
    writer_ids: Sequence[int],
    n_train: int = 40,
    n_val: int = 5,
    n_test: int = 10,
    seed: int = 42,
) -> Dict[str, List[int]]:
    """Shuffle writer_ids (seeded) and cut into disjoint train/val/test lists.

    If len(writer_ids) != n_train + n_val + n_test, the split is scaled to the
    actual pool size while keeping the requested train:val:test ratio, and a
    warning is printed (this can happen if a dataset mirror has a different
    writer count than CEDAR's canonical 55).
    """
    writer_ids = list(writer_ids)
    total_requested = n_train + n_val + n_test
    total_available = len(writer_ids)

    if total_available != total_requested:
        print(
            f"[writer_disjoint_split] WARNING: {total_available} writers available, "
            f"but {total_requested} were requested ({n_train}/{n_val}/{n_test}). "
            f"Scaling split sizes to the available pool while keeping the ratio."
        )
        scale = total_available / total_requested
        n_train = max(1, round(n_train * scale))
        n_val = max(1, round(n_val * scale))
        n_test = total_available - n_train - n_val

    rng = random.Random(seed)
    shuffled = writer_ids[:]
    rng.shuffle(shuffled)

    train = sorted(shuffled[:n_train])
    val = sorted(shuffled[n_train : n_train + n_val])
    test = sorted(shuffled[n_train + n_val : n_train + n_val + n_test])
    return {"train": train, "val": val, "test": test}


def save_split(split: Dict[str, List[int]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(split, indent=2))


def load_split(path: str | Path) -> Dict[str, List[int]]:
    return json.loads(Path(path).read_text())
