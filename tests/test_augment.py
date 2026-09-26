import inspect
import random

import numpy as np

from sigverify.training import augment
from sigverify.training.augment import add_gaussian_noise, augment_image, random_affine_jitter, random_rotation


def test_no_flip_calls_anywhere_in_augment_module():
    """Static guard: horizontal flip is a hard domain constraint (a signature
    has a fixed writing direction), so no flip API should ever be called here,
    not just absent from the current augment_image implementation.
    """
    source = inspect.getsource(augment)
    forbidden = ["cv2.flip", "np.flip", "fliplr", "flipud", "FLIP_LEFT_RIGHT", "FLIP_TOP_BOTTOM", ".flip("]
    for token in forbidden:
        assert token not in source, f"Forbidden flip operation found in augment.py: {token}"


def test_augment_image_preserves_left_right_orientation():
    """A horizontal flip would swap which side is darker; augmentation (small
    rotation/translation/noise only) must never do that.
    """
    img = np.ones((100, 100, 1), dtype=np.float32)
    img[:, 5:30, 0] = 0.0  # dark stroke on the LEFT side only

    rng = random.Random(0)
    for _ in range(20):
        out = augment_image(img, rng, max_rotation_deg=5.0, max_translate_frac=0.05, p_each=1.0)
        left_mean = out[:, :50].mean()
        right_mean = out[:, 50:].mean()
        assert left_mean < right_mean


def test_augment_image_output_shape_and_range():
    img = np.random.RandomState(0).rand(64, 64, 1).astype(np.float32)
    rng = random.Random(1)
    out = augment_image(img, rng, p_each=1.0)
    assert out.shape == img.shape
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_random_rotation_keeps_shape():
    img = np.zeros((50, 80, 1), dtype=np.float32)
    out = random_rotation(img, random.Random(2), max_deg=5.0)
    assert out.shape == img.shape


def test_random_affine_jitter_keeps_shape():
    img = np.zeros((50, 80, 1), dtype=np.float32)
    out = random_affine_jitter(img, random.Random(3))
    assert out.shape == img.shape


def test_add_gaussian_noise_stays_in_unit_range():
    img = np.full((10, 10, 1), 0.5, dtype=np.float32)
    out = add_gaussian_noise(img, random.Random(4), std=0.1)
    assert out.min() >= 0.0 and out.max() <= 1.0
