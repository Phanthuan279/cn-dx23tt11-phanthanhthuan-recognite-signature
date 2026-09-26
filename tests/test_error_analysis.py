import pandas as pd

from sigverify.evaluation.metrics import build_predictions_dataframe
from sigverify.pairs.generator import Pair, pairs_to_dataframe


def test_build_predictions_dataframe_adds_score_tau_and_prediction():
    pairs = [
        Pair("a1.png", "a2.png", 1, "genuine_genuine", 1),
        Pair("a1.png", "f1.png", 0, "skilled_forgery", 1),
    ]
    pairs_df = pairs_to_dataframe(pairs)
    scores = [0.2, 0.8]
    tau = 0.5

    predictions_df = build_predictions_dataframe(pairs_df, scores, tau)

    assert list(predictions_df["score"]) == [0.2, 0.8]
    assert (predictions_df["tau_used"] == 0.5).all()
    # score < tau -> prediction=1 (genuine); score >= tau -> prediction=0
    assert list(predictions_df["prediction"]) == [1, 0]


def _predictions_df() -> pd.DataFrame:
    # Row 0: label=1 (genuine), score=0.9 >= tau=0.5 -> prediction=0 -> FALSE REJECT
    # Row 1: label=0 skilled, score=0.1 < tau=0.5 -> prediction=1 -> FALSE ACCEPT (skilled)
    # Row 2: label=0 random, score=0.05 < tau=0.5 -> prediction=1 -> FALSE ACCEPT (random)
    # Row 3: label=1 (genuine), score=0.2 < tau=0.5 -> prediction=1 -> CORRECT
    # Row 4: label=0 skilled, score=0.6 >= tau=0.5 -> prediction=0 -> CORRECT
    return pd.DataFrame(
        {
            "pair_id": [0, 1, 2, 3, 4],
            "path_a": ["a"] * 5,
            "path_b": ["b"] * 5,
            "label": [1, 0, 0, 1, 0],
            "forgery_type": ["genuine_genuine", "skilled_forgery", "random_forgery", "genuine_genuine", "skilled_forgery"],
            "score": [0.9, 0.1, 0.05, 0.2, 0.6],
            "tau_used": [0.5] * 5,
            "prediction": [0, 1, 1, 1, 0],
        }
    )


def test_find_top_errors_selects_only_misclassified_pairs():
    from scripts.error_analysis import find_top_errors  # local import: adds scripts/ to sys.path via conftest

    errors = find_top_errors(_predictions_df(), top_k=20)
    assert len(errors) == 3
    assert set(errors["pair_id"]) == {0, 1, 2}


def test_find_top_errors_labels_false_accept_and_false_reject_correctly():
    from scripts.error_analysis import find_top_errors

    errors = find_top_errors(_predictions_df(), top_k=20)
    error_by_pair = errors.set_index("pair_id")["error_type"].to_dict()
    assert error_by_pair[0] == "false_reject"
    assert error_by_pair[1] == "false_accept"
    assert error_by_pair[2] == "false_accept"


def test_find_top_errors_respects_top_k_per_group():
    rows = []
    for i in range(30):
        rows.append(
            {
                "pair_id": i,
                "path_a": "a",
                "path_b": "b",
                "label": 0,
                "forgery_type": "random_forgery",
                "score": 0.1 + i * 0.001,  # all false accepts, increasing severity
                "tau_used": 0.5,
                "prediction": 1,
            }
        )
    df = pd.DataFrame(rows)

    from scripts.error_analysis import find_top_errors

    top5 = find_top_errors(df, top_k=5)
    assert len(top5) == 5
    # the 5 kept should be the ones with the LARGEST |score - tau| (i.e. smallest score here)
    assert set(top5["pair_id"]) == {0, 1, 2, 3, 4}


def test_find_top_errors_empty_when_no_mistakes():
    df = _predictions_df()
    df["prediction"] = df["label"]  # make everything "correct"

    from scripts.error_analysis import find_top_errors

    errors = find_top_errors(df, top_k=20)
    assert len(errors) == 0
