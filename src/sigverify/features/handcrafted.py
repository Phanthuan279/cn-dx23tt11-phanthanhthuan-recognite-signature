"""Handcrafted feature extractors (HOG, LBP) for the baseline SVM classifier."""

from __future__ import annotations

import numpy as np
from skimage.feature import hog, local_binary_pattern


def extract_hog(
    img: np.ndarray,
    orientations: int = 9,
    pixels_per_cell: tuple[int, int] = (16, 16),
    cells_per_block: tuple[int, int] = (2, 2),
) -> np.ndarray:
    """Extract a HOG feature vector from a preprocessed grayscale image.

    Accepts either (H, W) or (H, W, 1) arrays (e.g. straight from
    preprocess_image with mode="unit").
    """
    if img.ndim == 3:
        img = img[..., 0]
    return hog(
        img,
        orientations=orientations,
        pixels_per_cell=pixels_per_cell,
        cells_per_block=cells_per_block,
        feature_vector=True,
    )


def extract_lbp(img: np.ndarray, n_points: int = 8, radius: int = 1, n_bins: int | None = None) -> np.ndarray:
    """Extract a normalized LBP histogram feature vector.

    Accepts either (H, W) or (H, W, 1) arrays.
    """
    if img.ndim == 3:
        img = img[..., 0]
    lbp = local_binary_pattern(img, n_points, radius, method="uniform")
    n_bins = n_bins or (n_points + 2)
    hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins), density=True)
    return hist.astype(np.float64)


def extract_feature(img: np.ndarray, feature_type: str = "hog") -> np.ndarray:
    if feature_type == "hog":
        return extract_hog(img)
    if feature_type == "lbp":
        return extract_lbp(img)
    raise ValueError(f"Unknown feature_type: {feature_type}")
