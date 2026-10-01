"""KNN and SVM model builders for the digit recognition comparison."""

from __future__ import annotations

from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


def build_knn(n_neighbors: int = 5) -> KNeighborsClassifier:
    return KNeighborsClassifier(n_neighbors=n_neighbors, n_jobs=-1)


def build_svm(C: float = 5.0, gamma: str = "scale") -> SVC:
    # probability=True would add internal 5-fold Platt-scaling CV (~5x slower
    # to fit) just to get calibrated probabilities; decision_function() (used
    # for the demo's confidence display) is free and good enough for that.
    return SVC(kernel="rbf", C=C, gamma=gamma)
