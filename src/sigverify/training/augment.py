"""Train-only data augmentation: small rotation, translation/scale jitter, and
light Gaussian noise. Applied AFTER preprocess_image (i.e. to the normalized
float array), each transform independently at random, so a given call may
apply zero, one, two or all three.

Deliberately provides NO horizontal (or vertical) flip: a signature has a
fixed writing direction, and flipping it would create a physically impossible
sample. tests/test_augment.py statically scans this module's source for any
flip-related API call so the constraint can never silently regress.
"""

from __future__ import annotations

import random

import cv2
import numpy as np


def _warp_affine_preserve_channels(img: np.ndarray, matrix: np.ndarray, border_value: float) -> np.ndarray:
    """cv2.warpAffine silently drops a trailing (H, W, 1) channel axis; restore it."""
    had_channel_axis = img.ndim == 3
    h, w = img.shape[:2]
    warped = cv2.warpAffine(img, matrix, (w, h), borderValue=border_value, flags=cv2.INTER_LINEAR)
    if had_channel_axis and warped.ndim == 2:
        warped = warped[..., np.newaxis]
    return warped


def random_rotation(img: np.ndarray, rng: random.Random, max_deg: float = 5.0, border_value: float = 1.0) -> np.ndarray:
    h, w = img.shape[:2]
    angle = rng.uniform(-max_deg, max_deg)
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return _warp_affine_preserve_channels(img, matrix, border_value)


def random_affine_jitter(
    img: np.ndarray,
    rng: random.Random,
    max_translate_frac: float = 0.05,
    scale_range: tuple[float, float] = (0.95, 1.05),
    border_value: float = 1.0,
) -> np.ndarray:
    h, w = img.shape[:2]
    scale = rng.uniform(*scale_range)
    tx = rng.uniform(-max_translate_frac, max_translate_frac) * w
    ty = rng.uniform(-max_translate_frac, max_translate_frac) * h
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), 0.0, scale)
    matrix[0, 2] += tx
    matrix[1, 2] += ty
    return _warp_affine_preserve_channels(img, matrix, border_value)


def add_gaussian_noise(img: np.ndarray, rng: random.Random, std: float = 0.02) -> np.ndarray:
    noise = np.array([rng.gauss(0, std) for _ in range(img.size)], dtype=np.float32).reshape(img.shape)
    return np.clip(img + noise, 0.0, 1.0)


def augment_image(
    img: np.ndarray,
    rng: random.Random,
    max_rotation_deg: float = 5.0,
    max_translate_frac: float = 0.05,
    scale_range: tuple[float, float] = (0.95, 1.05),
    noise_std: float = 0.02,
    p_each: float = 0.5,
    border_value: float = 1.0,
) -> np.ndarray:
    """Apply rotation, affine jitter and noise, each independently with
    probability `p_each`. Never flips the image.
    """
    out = img
    if rng.random() < p_each:
        out = random_rotation(out, rng, max_rotation_deg, border_value)
    if rng.random() < p_each:
        out = random_affine_jitter(out, rng, max_translate_frac, scale_range, border_value)
    if rng.random() < p_each:
        out = add_gaussian_noise(out, rng, noise_std)
    return out
