import pandas as pd

from sigverify.pairs.generator import build_triplets_from_pairs, generate_pairs, pairs_to_dataframe
from sigverify.pairs.splits import writer_disjoint_split


def test_writer_disjoint_split_no_overlap_and_full_coverage():
    writer_ids = list(range(1, 56))  # 55 writers, like CEDAR
    split = writer_disjoint_split(writer_ids, n_train=40, n_val=5, n_test=10, seed=42)

    train, val, test = set(split["train"]), set(split["val"]), set(split["test"])
    assert len(train) == 40
    assert len(val) == 5
    assert len(test) == 10
    assert train.isdisjoint(val)
    assert train.isdisjoint(test)
    assert val.isdisjoint(test)
    assert train | val | test == set(writer_ids)


def test_writer_disjoint_split_scales_when_pool_size_differs():
    writer_ids = list(range(1, 21))  # only 20 writers available
    split = writer_disjoint_split(writer_ids, n_train=40, n_val=5, n_test=10, seed=1)
    total = len(split["train"]) + len(split["val"]) + len(split["test"])
    assert total == 20
    assert set(split["train"]).isdisjoint(split["val"])
    assert set(split["train"]).isdisjoint(split["test"])
    assert set(split["val"]).isdisjoint(split["test"])


def _synthetic_signatures_df(n_writers=6, n_genuine=6, n_forged=6) -> pd.DataFrame:
    rows = []
    for w in range(1, n_writers + 1):
        for s in range(1, n_genuine + 1):
            rows.append({"writer_id": w, "sample_id": s, "label": "genuine", "path": f"w{w}_g{s}.png"})
        for s in range(1, n_forged + 1):
            rows.append({"writer_id": w, "sample_id": s, "label": "forged", "path": f"w{w}_f{s}.png"})
    return pd.DataFrame(rows)


def test_generate_pairs_ratio_and_types():
    df = _synthetic_signatures_df()
    writer_ids = df["writer_id"].unique().tolist()

    pairs = generate_pairs(df, writer_ids, ratio=(2, 1, 1), pairs_per_writer=4, seed=7)
    out = pairs_to_dataframe(pairs)

    assert set(out["forgery_type"].unique()) <= {"genuine_genuine", "skilled_forgery", "random_forgery"}
    counts = out["forgery_type"].value_counts()
    # genuine_genuine should roughly be twice hard/easy negative counts (ratio 2:1:1)
    assert counts["genuine_genuine"] >= counts.get("skilled_forgery", 0)
    assert counts["genuine_genuine"] >= counts.get("random_forgery", 0)

    # label convention: genuine_genuine=1 (same), the two negative types=0 (different)
    assert (out.loc[out.forgery_type == "genuine_genuine", "label"] == 1).all()
    assert (out.loc[out.forgery_type == "skilled_forgery", "label"] == 0).all()
    assert (out.loc[out.forgery_type == "random_forgery", "label"] == 0).all()


def test_generate_pairs_random_forgery_never_crosses_split():
    """random_forgery pairs a writer with an OTHER writer -- but generate_pairs
    is only ever given writer_ids from a single split, so it can never reach
    across train/val/test even though the function itself doesn't know about splits.
    """
    df = _synthetic_signatures_df(n_writers=10)
    val_writers = [1, 2, 3]  # simulate a "val" split slice
    pairs = generate_pairs(df, val_writers, ratio=(2, 1, 1), pairs_per_writer=4, seed=3)
    out = pairs_to_dataframe(pairs)

    random_forgery = out[out.forgery_type == "random_forgery"]
    involved_writers = set()
    for _, row in random_forgery.iterrows():
        a_writer = int(row["path_a"].split("_")[0][1:])
        b_writer = int(row["path_b"].split("_")[0][1:])
        involved_writers.update([a_writer, b_writer])
    assert involved_writers <= set(val_writers)


def test_build_triplets_from_pairs_uses_only_real_rows_no_new_data():
    df = _synthetic_signatures_df(n_writers=6)
    writer_ids = df["writer_id"].unique().tolist()
    pairs = generate_pairs(df, writer_ids, ratio=(2, 1, 1), pairs_per_writer=4, seed=7)
    pairs_df = pairs_to_dataframe(pairs)

    triplets = build_triplets_from_pairs(pairs_df, seed=1)

    n_positive_pairs = (pairs_df.forgery_type == "genuine_genuine").sum()
    assert len(triplets) == n_positive_pairs  # one triplet per genuine_genuine row

    # every anchor/positive/negative path must come from the real pairs_df --
    # nothing fabricated
    real_paths = set(pairs_df["path_a"]) | set(pairs_df["path_b"])
    assert set(triplets["anchor"]) <= real_paths
    assert set(triplets["positive"]) <= real_paths
    assert set(triplets["negative"]) <= real_paths
    assert set(triplets["negative_type"].unique()) <= {"skilled_forgery", "random_forgery"}

    # anchor/positive must be genuine_genuine pairs of the SAME writer as the negative
    genuine = pairs_df[pairs_df.forgery_type == "genuine_genuine"].set_index(["path_a", "path_b"])
    for row in triplets.itertuples(index=False):
        assert (row.anchor, row.positive) in genuine.index
        assert genuine.loc[(row.anchor, row.positive), "writer_id"] == row.writer_id


def test_build_triplets_from_pairs_skips_writers_without_negatives():
    pairs_df = pd.DataFrame(
        [
            {"path_a": "a1.png", "path_b": "a2.png", "label": 1, "forgery_type": "genuine_genuine", "writer_id": 1},
        ]
    )
    triplets = build_triplets_from_pairs(pairs_df, seed=1)
    assert triplets.empty
