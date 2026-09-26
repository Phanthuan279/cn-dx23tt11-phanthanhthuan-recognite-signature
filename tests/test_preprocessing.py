import numpy as np
import pytest
from PIL import Image, ImageDraw

from sigverify.preprocessing.pipeline import (
    center_pad_resize,
    normalize,
    otsu_mask,
    preprocess_image,
    tight_bbox,
)


def _synthetic_signature(canvas_size=(400, 300), stroke_box=(250, 20, 380, 90)) -> np.ndarray:
    """Draw a few dark strokes in one corner of a large white canvas."""
    img = Image.new("L", canvas_size, color=255)
    draw = ImageDraw.Draw(img)
    x0, y0, x1, y1 = stroke_box
    draw.line([(x0, y0), (x1, y1)], fill=0, width=4)
    draw.line([(x0, y1), (x1, y0)], fill=0, width=4)
    return np.array(img)


def test_otsu_and_bbox_locate_strokes():
    img = _synthetic_signature()
    mask = otsu_mask(img)
    x0, y0, x1, y1 = tight_bbox(mask)
    # bbox should be much smaller than the full 400x300 canvas
    assert (x1 - x0) < 200
    assert (y1 - y0) < 150
    # bbox should be near the stroke region we drew (250-380, 20-90)
    assert x0 > 200
    assert x1 < 400


def test_center_pad_resize_output_shape():
    img = np.zeros((50, 120), dtype=np.uint8)
    out = center_pad_resize(img, (220, 150))
    assert out.shape == (150, 220)


def test_normalize_unit_mode_range():
    img = np.array([[0, 128, 255]], dtype=np.uint8)
    out = normalize(img, mode="unit")
    assert out.shape == (1, 3, 1)
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_normalize_imagenet_mode_channels():
    img = np.zeros((10, 10), dtype=np.uint8)
    out = normalize(img, mode="imagenet")
    assert out.shape == (10, 10, 3)


@pytest.mark.parametrize("binarize_output", [False, True])
def test_preprocess_image_output_size(binarize_output):
    img = _synthetic_signature()
    target_size = (220, 150)
    out = preprocess_image(img, target_size, mode="unit", binarize_output=binarize_output)
    assert out.shape == (150, 220, 1)
    assert out.dtype == np.float32
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_preprocess_image_imagenet_mode_three_channels():
    img = _synthetic_signature()
    out = preprocess_image(img, (224, 224), mode="imagenet")
    assert out.shape == (224, 224, 3)


def test_preprocess_image_crop_to_bbox_false_uses_full_canvas():
    """Phase 7 ablation variant: skip the tight Otsu crop and resize the whole
    original canvas instead. Output shape is unaffected either way, but the
    stroke should occupy proportionally less of the frame than with cropping.
    """
    img = _synthetic_signature()
    target_size = (220, 150)

    cropped = preprocess_image(img, target_size, mode="unit", crop_to_bbox=True)
    full_canvas = preprocess_image(img, target_size, mode="unit", crop_to_bbox=False)

    assert cropped.shape == full_canvas.shape == (150, 220, 1)
    # tight crop makes ink pixels denser in the frame -> lower mean (darker) overall
    assert cropped.mean() < full_canvas.mean()
