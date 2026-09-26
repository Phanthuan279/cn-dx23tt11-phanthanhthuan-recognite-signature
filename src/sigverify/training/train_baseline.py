"""HOG/LBP + SVM(RBF) baseline: the mandatory comparison point for both
Siamese configurations.

SVM decision_function gives higher = more genuine, but the shared evaluation
framework (src/sigverify/evaluation/metrics.py) expects DISTANCE scores
(lower = more genuine) -- so scores are negated once, right after fitting,
and never again.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.svm import SVC

from sigverify.features.handcrafted import extract_feature
from sigverify.preprocessing.pipeline import preprocess_image


def build_feature_matrix(
    pairs_df: pd.DataFrame,
    feature_type: str,
    target_size: Tuple[int, int],
    denoise_method: str = "gaussian",
    binarize_output: bool = False,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Turn a pairs dataframe into (X, y, forgery_type) for the SVM.

    X[i] = |feature(img_a) - feature(img_b)| for pair i.
    """
    features = []
    for _, row in pairs_df.iterrows():
        img_a = preprocess_image(row["path_a"], target_size, "unit", denoise_method, binarize_output)
        img_b = preprocess_image(row["path_b"], target_size, "unit", denoise_method, binarize_output)
        f_a = extract_feature(img_a, feature_type)
        f_b = extract_feature(img_b, feature_type)
        features.append(np.abs(f_a - f_b))

    X = np.array(features)
    y = pairs_df["label"].to_numpy()
    forgery_type = pairs_df["forgery_type"].to_numpy()
    return X, y, forgery_type


def fit_svm(X_train: np.ndarray, y_train: np.ndarray, param_grid: dict, cv_folds: int = 5) -> SVC:
    """Grid-search an RBF SVM using cross-validation INSIDE the training set only."""
    cv = StratifiedKFold(n_splits=min(cv_folds, np.bincount(y_train).min()), shuffle=True, random_state=0)
    search = GridSearchCV(SVC(kernel="rbf"), param_grid, cv=cv, n_jobs=-1)
    search.fit(X_train, y_train)
    return search.best_estimator_


def scores_from_svm(svm: SVC, X: np.ndarray) -> np.ndarray:
    """Distance-like score: higher decision_function (more genuine) -> lower distance."""
    return -svm.decision_function(X)
