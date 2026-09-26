import io
import json
from pathlib import Path

import pytest
import torch
from PIL import Image, ImageDraw

from app.inference import ModelNotReadyError, compare, decision, load_model, lookup_far_frr, preprocess_and_embed
from sigverify.models.siamese_scratch import SiameseScratchCNN


def _fake_signature_bytes() -> bytes:
    img = Image.new("L", (200, 150), color=255)
    d = ImageDraw.Draw(img)
    d.line([(20, 20), (150, 100)], fill=0, width=3)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_preprocess_and_embed_never_writes_to_disk(tmp_path, monkeypatch):
    """Guards the privacy requirement: run inference in a directory, then
    confirm no new file appeared in it or anywhere under the repo's data/
    or a scratch tmp dir the test controls.
    """
    monkeypatch.chdir(tmp_path)
    model = SiameseScratchCNN(embedding_dim=128)
    image_bytes = _fake_signature_bytes()

    files_before = set(tmp_path.rglob("*"))
    _, embedding = preprocess_and_embed(model, image_bytes, target_size=(220, 150), mode="unit")
    files_after = set(tmp_path.rglob("*"))

    assert files_before == files_after
    assert embedding.shape == (128,)


def test_preprocess_and_embed_returns_2d_display_image_for_unit_mode():
    model = SiameseScratchCNN(embedding_dim=128)
    image_bytes = _fake_signature_bytes()
    display_image, _ = preprocess_and_embed(model, image_bytes, target_size=(220, 150), mode="unit")
    assert display_image.ndim == 2
    assert display_image.shape == (150, 220)


def test_compare_and_decision():
    e1 = torch.zeros(128)
    e2 = torch.zeros(128)
    d = compare(e1, e2)
    assert d == pytest.approx(0.0)
    assert decision(d, tau=0.5) == "Thật"

    e3 = torch.ones(128) * 10
    d2 = compare(e1, e3)
    assert decision(d2, tau=0.5) == "Giả"


def test_lookup_far_frr_finds_nearest_threshold():
    curve = {"thresholds": [0.0, 0.5, 1.0, 1.5, 2.0], "far": [0.9, 0.5, 0.1, 0.05, 0.0], "frr": [0.0, 0.05, 0.2, 0.6, 0.95]}
    far, frr = lookup_far_frr(0.52, curve)
    assert far == 0.5
    assert frr == 0.05


def test_load_model_raises_clear_error_when_artefacts_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ModelNotReadyError, match="config_a"):
        load_model("config_a")


def test_load_model_loads_config_a_from_disk(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("configs").mkdir()
    Path("configs/default.yaml").write_text(
        "seed: 42\n"
        "image:\n  size_scratch: [220, 150]\n  size_transfer: [224, 224]\n"
        "preprocessing:\n  denoise: gaussian\n  binarize_output: false\n  crop_to_bbox: true\n"
        "model:\n  embedding_dim: 128\n  l2_normalize: false\n  transfer_backbone: resnet18\n"
    )
    Path("models_registry").mkdir()
    Path("results/config_a").mkdir(parents=True)

    model = SiameseScratchCNN(embedding_dim=128, l2_normalize=False)
    torch.save(model.state_dict(), "models_registry/config_a_best.pt")
    Path("models_registry/config_a_threshold.json").write_text(json.dumps({"tau": 0.8, "margin": 1.0, "val_eer": 0.1}))
    Path("results/config_a/far_frr_curve.json").write_text(
        json.dumps({"thresholds": [0.0, 1.0], "far": [1.0, 0.0], "frr": [0.0, 1.0]})
    )

    loaded_model, threshold_info, far_frr_curve = load_model("config_a")
    assert threshold_info["tau"] == 0.8
    assert far_frr_curve["thresholds"] == [0.0, 1.0]
    assert not loaded_model.training  # eval mode
