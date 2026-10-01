"""Load and split the real MNIST dataset (via sklearn's fetch_openml)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

DATA_CACHE = Path(__file__).resolve().parents[2] / "data"


def load_mnist() -> tuple[np.ndarray, np.ndarray]:
    """Return (X, y): X is (70000, 784) pixel values in [0, 255] (float),
    y is (70000,) digit labels as strings "0".."9". Cached on disk by
    sklearn after the first call (no internet needed afterwards).
    """
    X, y = fetch_openml(
        "mnist_784", version=1, return_X_y=True, as_frame=False, parser="auto",
        data_home=str(DATA_CACHE),
    )
    return X, y


def split_mnist(X: np.ndarray, y: np.ndarray, seed: int = 42):
    """Stratified split of the full 70000-sample MNIST matching the dataset's
    canonical 60000/10000 train/test sizes, with a validation set carved out
    of the training portion: 54000 train / 6000 val / 10000 test.
    """
    X_trainval, X_test, y_trainval, y_test = train_test_split(
        X, y, test_size=10000, random_state=seed, stratify=y
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_trainval, y_trainval, test_size=6000, random_state=seed, stratify=y_trainval
    )
    return X_train, X_val, X_test, y_train, y_val, y_test
