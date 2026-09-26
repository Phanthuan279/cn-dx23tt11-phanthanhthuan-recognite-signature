"""Generate the 3 pair types used throughout the plan:

  - genuine_genuine : 2 genuine signatures of the SAME writer     -> label=1
  - skilled_forgery : 1 genuine + 1 forged signature, SAME writer -> label=0
  - random_forgery  : genuine signatures of TWO DIFFERENT writers -> label=0

"random forgery" == cross-writer genuine pairs; "skilled forgery" == the
dataset's own forged-signature directory. Both negative types are reported
separately downstream (src/sigverify/evaluation/metrics.py).
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

import pandas as pd


@dataclass(frozen=True)
class Pair:
    path_a: str
    path_b: str
    label: int  # 1 = same signer (genuine_genuine), 0 = different
    forgery_type: str  # "genuine_genuine" | "skilled_forgery" | "random_forgery"
    writer_id: int


def _writer_paths(df: pd.DataFrame, writer_id: int, label: str) -> List[str]:
    return df[(df.writer_id == writer_id) & (df.label == label)]["path"].tolist()


def generate_pairs(
    df_signatures: pd.DataFrame,
    writer_ids: Sequence[int],
    ratio: Sequence[int] = (2, 1, 1),
    pairs_per_writer: int = 40,
    seed: int = 42,
) -> List[Pair]:
    """Generate pairs for the given writer_ids only (a single split's writers).

    `ratio` is (pos, hard_neg, easy_neg); `pairs_per_writer` is the target
    number of genuine_genuine pairs per writer, and the other two counts are
    scaled from it by the ratio. Positive and hard-negative pairs are sampled
    (without replacement where possible) from that writer's own combinations;
    easy-negative pairs draw a genuine sample from a randomly chosen different
    writer within the same split (never across splits).
    """
    r_pos, r_hard, r_easy = ratio
    n_pos = pairs_per_writer
    n_hard = max(1, round(pairs_per_writer * r_hard / r_pos))
    n_easy = max(1, round(pairs_per_writer * r_easy / r_pos))

    rng = random.Random(seed)
    writer_ids = list(writer_ids)
    pairs: List[Pair] = []

    for writer in writer_ids:
        genuine = _writer_paths(df_signatures, writer, "genuine")
        forged = _writer_paths(df_signatures, writer, "forged")

        # genuine_genuine
        combos = list(itertools.combinations(genuine, 2))
        rng.shuffle(combos)
        for a, b in combos[:n_pos]:
            pairs.append(Pair(a, b, 1, "genuine_genuine", writer))

        # skilled_forgery
        combos = list(itertools.product(genuine, forged))
        rng.shuffle(combos)
        for a, b in combos[:n_hard]:
            pairs.append(Pair(a, b, 0, "skilled_forgery", writer))

        # random_forgery: genuine of `writer` vs genuine of a different writer, same split
        other_writers = [w for w in writer_ids if w != writer]
        for _ in range(min(n_easy, len(genuine) or 0)):
            if not other_writers or not genuine:
                break
            other = rng.choice(other_writers)
            other_genuine = _writer_paths(df_signatures, other, "genuine")
            if not other_genuine:
                continue
            a = rng.choice(genuine)
            b = rng.choice(other_genuine)
            pairs.append(Pair(a, b, 0, "random_forgery", writer))

    return pairs


def pairs_to_dataframe(pairs: List[Pair]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "pair_id": range(len(pairs)),
            "path_a": [p.path_a for p in pairs],
            "path_b": [p.path_b for p in pairs],
            "label": [p.label for p in pairs],
            "forgery_type": [p.forgery_type for p in pairs],
            "writer_id": [p.writer_id for p in pairs],
        }
    )


def summarize_ratio(pairs: List[Pair]) -> Dict[str, int]:
    df = pairs_to_dataframe(pairs)
    return df["forgery_type"].value_counts().to_dict()
