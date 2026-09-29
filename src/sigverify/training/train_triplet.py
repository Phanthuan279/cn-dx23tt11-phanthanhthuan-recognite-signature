"""Triplet-loss training path (T6: contrastive vs. triplet loss comparison).

Reuses the same preprocessing/augmentation/early-stopping machinery as
train_siamese.py -- only the loss and the on-disk triplet layout differ.
Validation/model-selection still uses compute_pair_scores() on the ordinary
val_pairs_df (genuine vs. forgery distances), so the val EER is directly
comparable to the contrastive-loss runs: both are "how well does this
embedding space separate genuine pairs from forged pairs", regardless of
which loss shaped that embedding space during training.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

from sigverify.evaluation.metrics import compute_far_frr, find_eer
from sigverify.models.losses import TripletLoss
from sigverify.preprocessing.pipeline import preprocess_image
from sigverify.training.augment import augment_image
from sigverify.training.train_siamese import compute_pair_scores


class TripletDataset(Dataset):
    def __init__(
        self,
        triplets_df: pd.DataFrame,
        target_size: tuple[int, int],
        mode: str = "unit",
        denoise_method: str = "gaussian",
        binarize_output: bool = False,
        crop_to_bbox: bool = True,
        augment: bool = False,
    ):
        self.triplets_df = triplets_df.reset_index(drop=True)
        self.target_size = target_size
        self.mode = mode
        self.denoise_method = denoise_method
        self.binarize_output = binarize_output
        self.crop_to_bbox = crop_to_bbox
        self.augment = augment

    def __len__(self) -> int:
        return len(self.triplets_df)

    def _load(self, path: str) -> torch.Tensor:
        img = preprocess_image(
            path, self.target_size, self.mode, self.denoise_method, self.binarize_output, self.crop_to_bbox
        )
        if self.augment:
            img = augment_image(img, rng=random)
        return torch.from_numpy(np.ascontiguousarray(img.transpose(2, 0, 1))).float()

    def __getitem__(self, idx: int):
        row = self.triplets_df.iloc[idx]
        return self._load(row["anchor"]), self._load(row["positive"]), self._load(row["negative"])


def train_triplet_config(
    model: torch.nn.Module,
    train_triplets_df: pd.DataFrame,
    val_pairs_df: pd.DataFrame,
    target_size: tuple[int, int],
    mode: str,
    margin: float,
    lr: float = 1e-3,
    max_epochs: int = 100,
    patience: int = 10,
    warmup_epochs: int = 5,
    batch_size: int = 64,
    device: Optional[torch.device] = None,
    denoise_method: str = "gaussian",
    binarize_output: bool = False,
    crop_to_bbox: bool = True,
    augmentation_enabled: bool = True,
) -> tuple[dict, list[dict]]:
    """Train `model` with triplet loss, early-stopping on validation EER
    (computed the same way as the contrastive path, via compute_pair_scores
    on val_pairs_df). Returns (best_state_dict, history)."""
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    criterion = TripletLoss(margin=margin)
    optimizer = torch.optim.Adam((p for p in model.parameters() if p.requires_grad), lr=lr)

    train_loader = DataLoader(
        TripletDataset(
            train_triplets_df, target_size, mode, denoise_method, binarize_output, crop_to_bbox,
            augment=augmentation_enabled,
        ),
        batch_size=batch_size,
        shuffle=True,
    )

    best_eer = float("inf")
    best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
    epochs_without_improvement = 0
    history = []

    for epoch in range(max_epochs):
        model.train()
        total_loss = 0.0
        for img_a, img_p, img_n in train_loader:
            img_a, img_p, img_n = img_a.to(device), img_p.to(device), img_n.to(device)
            optimizer.zero_grad()
            e_a, e_p, e_n = model(img_a), model(img_p), model(img_n)
            loss = criterion(e_a, e_p, e_n)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * img_a.size(0)
        train_loss = total_loss / max(1, len(train_loader.dataset))

        val_scores, val_labels, _ = compute_pair_scores(
            model, val_pairs_df, target_size, mode, denoise_method, binarize_output, device, batch_size, crop_to_bbox
        )
        far, frr, thresholds = compute_far_frr(val_scores, val_labels)
        val_eer, _ = find_eer(far, frr, thresholds)

        history.append({"epoch": epoch, "train_loss": train_loss, "val_eer": val_eer})
        print(f"[train_triplet_config] epoch={epoch} train_loss={train_loss:.4f} val_eer={val_eer:.4f}", flush=True)

        if val_eer < best_eer:
            best_eer = val_eer
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            epochs_without_improvement = 0
        elif epoch >= warmup_epochs:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                print(f"[train_triplet_config] Early stopping at epoch {epoch} (best_val_eer={best_eer:.4f})", flush=True)
                break

    model.load_state_dict(best_state)
    return best_state, history
