"""Five-step preprocessing pipeline shared by the baseline, both Siamese
configurations and the demo app.

Otsu binarization is used ONLY to locate the signature's bounding box; the
final model input is the (denoised) grayscale image cropped to that box, not
a flat binary mask, so that stroke-thickness information is preserved. Set
``binarize_output=True`` to use the binary mask as the final input instead
(this is one of the Phase 7 ablation variants, not the default).
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import cv2
import numpy as np

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

ImageInput = Union[str, Path, np.ndarray]


def load_grayscale(image: ImageInput) -> np.ndarray:
    """Load an image as a 2D uint8 grayscale array, from a path or an array."""
    if isinstance(image, (str, Path)):
        img = cv2.imread(str(image), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Could not read image: {image}")
        return img
    arr = np.asarray(image)
    if arr.ndim == 3:
        arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY if arr.shape[2] == 3 else cv2.COLOR_BGRA2GRAY)
    return arr.astype(np.uint8)


def ensure_dark_ink_on_white(img: np.ndarray) -> np.ndarray:
    """Invert the image if it appears to have a dark background (light ink).

    Assumes a normal signature scan has a light/white background and dark
    ink. Checks the mean intensity of a thin border around the image: a dark
    border implies an inverted scan.
    """
    border = np.concatenate(
        [img[0, :], img[-1, :], img[:, 0], img[:, -1]]
    )
    if border.mean() < 127:
        return 255 - img
    return img


def denoise(img: np.ndarray, method: str = "gaussian") -> np.ndarray:
    """Apply a small Gaussian or median blur to reduce scan noise."""
    if method == "gaussian":
        return cv2.GaussianBlur(img, (3, 3), 0)
    if method == "median":
        return cv2.medianBlur(img, 3)
    raise ValueError(f"Unknown denoise method: {method}")


def otsu_mask(img: np.ndarray) -> np.ndarray:
    """Binarize with Otsu's threshold. Ink pixels (dark) become 255 (foreground)."""
    _, mask = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return mask


def tight_bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    """Return (x0, y0, x1, y1) tightly bounding the foreground (ink) pixels.

    Falls back to the full image if no foreground pixel is found (blank scan).
    """
    ys, xs = np.where(mask > 0)
    if len(xs) == 0 or len(ys) == 0:
        h, w = mask.shape
        return 0, 0, w, h
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    return x0, y0, x1, y1


def center_pad_resize(img: np.ndarray, target_size: tuple[int, int]) -> np.ndarray:
    """Resize keeping aspect ratio, then center on a white canvas of target_size.

    target_size is (width, height).
    """
    target_w, target_h = target_size
    h, w = img.shape[:2]
    scale = min(target_w / w, target_h / h)
    new_w, new_h = max(1, round(w * scale)), max(1, round(h * scale))
    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.full((target_h, target_w), 255, dtype=np.uint8)
    x_off = (target_w - new_w) // 2
    y_off = (target_h - new_h) // 2
    canvas[y_off : y_off + new_h, x_off : x_off + new_w] = resized
    return canvas


def normalize(img: np.ndarray, mode: str = "unit") -> np.ndarray:
    """Normalize pixel values. mode="unit" -> [0,1] float32, 1 channel.
    mode="imagenet" -> 3-channel, ImageNet mean/std normalized, for transfer learning.
    """
    if mode == "unit":
        return (img.astype(np.float32) / 255.0)[..., np.newaxis]
    if mode == "imagenet":
        rgb = np.repeat(img[..., np.newaxis], 3, axis=2).astype(np.float32) / 255.0
        return (rgb - IMAGENET_MEAN) / IMAGENET_STD
    raise ValueError(f"Unknown normalize mode: {mode}")


def preprocess_image(
    image: ImageInput,
    target_size: tuple[int, int],
    mode: str = "unit",
    denoise_method: str = "gaussian",
    binarize_output: bool = False,
) -> np.ndarray:
    """Run the full 5-step preprocessing pipeline.

    1. grayscale  2. denoise  3. Otsu (bbox only)  4. tight crop  5. center+pad+resize+normalize

    Returns a float32 array: (H, W, 1) for mode="unit", (H, W, 3) for mode="imagenet".
    """
    gray = load_grayscale(image)
    gray = ensure_dark_ink_on_white(gray)
    denoised = denoise(gray, denoise_method)

    mask = otsu_mask(denoised)
    x0, y0, x1, y1 = tight_bbox(mask)

    source = mask if binarize_output else denoised
    # invert back the mask (255=ink) to look like a grayscale image (dark ink, white bg)
    if binarize_output:
        source = 255 - source
    cropped = source[y0:y1, x0:x1]

    resized = center_pad_resize(cropped, target_size)
    return normalize(resized, mode)
