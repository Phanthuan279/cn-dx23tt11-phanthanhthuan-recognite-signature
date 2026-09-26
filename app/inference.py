"""Pure inference logic for the demo app -- deliberately independent of any
UI framework so app/demo_app.py (Streamlit) could be swapped for a Gradio
app without touching this file.

PRIVACY: every function here takes image bytes and returns numpy/torch
values in memory. Nothing in this module writes an uploaded image to disk,
logs its path, or sends it anywhere. Signature images are personal
biometric data.
"""

from __future__ import annotations

import io
import json
from pathlib import Path
from typing import Tuple

import numpy as np
import torch
from PIL import Image

from sigverify.models.losses import pairwise_distance
from sigverify.models.siamese_scratch import SiameseScratchCNN
from sigverify.models.siamese_transfer import SiameseTransferCNN
from sigverify.preprocessing.pipeline import preprocess_image
from sigverify.utils.config import load_config

MODELS_REGISTRY = Path("models_registry")
RESULTS_DIR = Path("results")


class ModelNotReadyError(RuntimeError):
    """Raised when a model's trained weights/threshold/FAR-FRR curve are not
    on disk yet (e.g. training hasn't been run on Colab/Kaggle). The demo
    app must fail loudly here rather than run with random, untrained weights.
    """


def load_model(config_name: str, config_path: str = "configs/default.yaml") -> Tuple[torch.nn.Module, dict, dict]:
    """Load a trained model + its frozen threshold + its FAR/FRR curve.

    Returns (model, threshold_info, far_frr_curve). `model` is on CPU in eval
    mode. Raises ModelNotReadyError with an actionable message if the
    expected artefacts from scripts/train_config_a.py / train_config_b.py
    are not present.
    """
    model_path = MODELS_REGISTRY / f"{config_name}_best.pt"
    threshold_path = MODELS_REGISTRY / f"{config_name}_threshold.json"
    curve_path = RESULTS_DIR / config_name / "far_frr_curve.json"

    # Check for the trained artefacts before touching the config file at all,
    # so a "not trained yet" error is reported even if configs/default.yaml
    # happens to be missing too (e.g. this function is called from a
    # directory that isn't the project root).
    missing = [p for p in (model_path, threshold_path, curve_path) if not p.exists()]
    if missing:
        missing_str = ", ".join(str(p) for p in missing)
        train_script = "train_config_a.py" if config_name == "config_a" else "train_config_b.py"
        raise ModelNotReadyError(
            f"Missing trained artefacts for '{config_name}': {missing_str}. "
            f"Run scripts/{train_script} (on Colab/Kaggle, with a GPU) first."
        )

    config = load_config(config_path)

    if config_name == "config_a":
        model = SiameseScratchCNN(
            embedding_dim=config["model"]["embedding_dim"], l2_normalize=config["model"]["l2_normalize"]
        )
    elif config_name == "config_b":
        model = SiameseTransferCNN(
            embedding_dim=config["model"]["embedding_dim"],
            backbone=config["model"]["transfer_backbone"],
            pretrained=False,  # loading our own fine-tuned weights next, not ImageNet ones
        )
    else:
        raise ValueError(f"Unknown config_name: {config_name}")

    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    threshold_info = json.loads(threshold_path.read_text())
    far_frr_curve = json.loads(curve_path.read_text())
    return model, threshold_info, far_frr_curve


def _bytes_to_grayscale_array(image_bytes: bytes) -> np.ndarray:
    """Decode uploaded image bytes to a grayscale numpy array, entirely in memory."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        return np.array(img.convert("L"))


def preprocess_and_embed(
    model: torch.nn.Module,
    image_bytes: bytes,
    target_size: Tuple[int, int],
    mode: str,
    denoise_method: str = "gaussian",
    binarize_output: bool = False,
    crop_to_bbox: bool = True,
) -> Tuple[np.ndarray, torch.Tensor]:
    """Preprocess an uploaded image (bytes, in memory) and compute its embedding.

    Returns (preprocessed_image_for_display, embedding). The preprocessed
    array is squeezed to 2D grayscale for display even in "imagenet" mode.
    """
    gray_array = _bytes_to_grayscale_array(image_bytes)
    preprocessed = preprocess_image(gray_array, target_size, mode, denoise_method, binarize_output, crop_to_bbox)

    tensor = torch.from_numpy(np.ascontiguousarray(preprocessed.transpose(2, 0, 1))).float().unsqueeze(0)
    with torch.no_grad():
        embedding = model(tensor)[0]

    display_image = preprocessed[..., 0] if preprocessed.shape[-1] == 1 else preprocessed
    return display_image, embedding


def compare(embedding_a: torch.Tensor, embedding_b: torch.Tensor) -> float:
    """Euclidean distance between two embeddings -- lower means more likely genuine."""
    d = pairwise_distance(embedding_a.unsqueeze(0), embedding_b.unsqueeze(0))
    return float(d.item())


def decision(distance: float, tau: float) -> str:
    return "Thật" if distance < tau else "Giả"


def lookup_far_frr(tau: float, far_frr_curve: dict) -> Tuple[float, float]:
    """Look up the (FAR, FRR) at the threshold in far_frr_curve nearest to `tau`."""
    thresholds = np.asarray(far_frr_curve["thresholds"])
    idx = int(np.argmin(np.abs(thresholds - tau)))
    return float(far_frr_curve["far"][idx]), float(far_frr_curve["frr"][idx])
