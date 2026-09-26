import numpy as np

from sigverify.features.handcrafted import extract_hog, extract_lbp


def _checkerboard(size=(150, 220)) -> np.ndarray:
    h, w = size
    img = np.indices((h, w)).sum(axis=0) % 2
    return (img * 255).astype(np.uint8)


def test_extract_hog_returns_stable_1d_vector():
    img = _checkerboard()
    f1 = extract_hog(img)
    f2 = extract_hog(img)
    assert f1.ndim == 1
    assert f1.shape == f2.shape
    np.testing.assert_array_equal(f1, f2)


def test_extract_hog_accepts_hw1_shape():
    img = _checkerboard()[..., np.newaxis]
    f = extract_hog(img)
    assert f.ndim == 1
    assert f.shape[0] > 0


def test_extract_lbp_returns_stable_normalized_histogram():
    img = _checkerboard()
    f1 = extract_lbp(img)
    f2 = extract_lbp(img)
    assert f1.shape == (10,)  # n_points=8 -> 8+2 uniform bins by default
    np.testing.assert_allclose(f1, f2)
    assert np.isclose(f1.sum(), 1.0, atol=1e-6)


def test_extract_lbp_accepts_hw1_shape():
    img = _checkerboard()[..., np.newaxis]
    f = extract_lbp(img)
    assert f.ndim == 1
