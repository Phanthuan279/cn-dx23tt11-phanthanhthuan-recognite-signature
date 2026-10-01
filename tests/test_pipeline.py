"""Fast unit tests on synthetic data -- no MNIST download needed."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from digitrec.evaluate import evaluate_model, plot_confusion_matrix  # noqa: E402
from digitrec.models import build_knn, build_svm  # noqa: E402


def _synthetic_digits(n_per_class=20, seed=0):
    """10 well-separated Gaussian blobs in 784-d, standing in for 10 digit
    classes, so KNN/SVM can be fit and evaluated without network access.
    """
    rng = np.random.RandomState(seed)
    X, y = [], []
    for digit in range(10):
        center = rng.uniform(0, 1, size=784)
        X.append(rng.normal(loc=center, scale=0.02, size=(n_per_class, 784)))
        y.extend([str(digit)] * n_per_class)
    X = np.clip(np.vstack(X), 0, 1).astype("float32")
    return X, np.array(y)


def test_knn_fits_and_predicts_known_classes():
    X, y = _synthetic_digits()
    model = build_knn(n_neighbors=3)
    model.fit(X, y)
    preds = model.predict(X)
    assert set(preds) <= set(str(d) for d in range(10))
    assert (preds == y).mean() > 0.9  # well-separated blobs should be easy


def test_svm_fits_and_predicts_known_classes():
    X, y = _synthetic_digits()
    model = build_svm()
    model.fit(X, y)
    preds = model.predict(X)
    assert set(preds) <= set(str(d) for d in range(10))
    assert (preds == y).mean() > 0.9


def test_evaluate_model_reports_accuracy_and_confusion_matrix():
    X, y = _synthetic_digits()
    model = build_knn(n_neighbors=3)
    model.fit(X, y)
    metrics = evaluate_model(model, X, y)
    assert 0.0 <= metrics["accuracy"] <= 1.0
    cm = metrics["confusion_matrix"]
    assert len(cm) == 10 and all(len(row) == 10 for row in cm)


def test_plot_confusion_matrix_writes_a_file(tmp_path):
    cm = [[5 if i == j else 0 for j in range(10)] for i in range(10)]
    out_path = tmp_path / "cm.png"
    plot_confusion_matrix(cm, "test", str(out_path))
    assert out_path.exists() and out_path.stat().st_size > 0


def test_app_runs_without_exceptions():
    """Regression test: app.py previously imported streamlit-drawable-canvas,
    which crashes at import time on this Streamlit version (incompatible
    component API) while the bare server process still starts fine -- a
    server-liveness check alone would miss this. AppTest actually executes
    the script the way a real browser session would.
    """
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=30)
    at.run()
    assert not at.exception
