"""Shared Siamese training loop, used by both Config A (scratch CNN) and
Config B (transfer learning) -- only the model, optimizer and image mode
differ between the two.
"""

from __future__ import annotations

import random
from typing import Optional

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

from sigverify.evaluation.metrics import compute_far_frr, find_eer
from sigverify.models.losses import pairwise_distance
from sigverify.preprocessing.pipeline import preprocess_image
from sigverify.training.augment import augment_image


class PairDataset(Dataset):
    """Loads and preprocesses image pairs on the fly. Augmentation (train-only)
    is applied AFTER preprocessing, using the global `random` module so the
    whole run stays reproducible from a single `set_seed(...)` call.
    """

    def __init__(
        self,
        pairs_df: pd.DataFrame,
        target_size: tuple[int, int],
        mode: str = "unit",
        denoise_method: str = "gaussian",
        binarize_output: bool = False,
        augment: bool = False,
    ):
        self.pairs_df = pairs_df.reset_index(drop=True)
        self.target_size = target_size
        self.mode = mode
        self.denoise_method = denoise_method
        self.binarize_output = binarize_output
        self.augment = augment

    def __len__(self) -> int:
        return len(self.pairs_df)

    def _load(self, path: str) -> torch.Tensor:
        img = preprocess_image(path, self.target_size, self.mode, self.denoise_method, self.binarize_output)
        if self.augment:
            img = augment_image(img, rng=random)
        # (H, W, C) -> (C, H, W)
        return torch.from_numpy(np.ascontiguousarray(img.transpose(2, 0, 1))).float()

    def __getitem__(self, idx: int):
        row = self.pairs_df.iloc[idx]
        img_a = self._load(row["path_a"])
        img_b = self._load(row["path_b"])
        label = torch.tensor(row["label"], dtype=torch.float32)
        return img_a, img_b, label, row["forgery_type"]


def compute_pair_scores(
    model: torch.nn.Module,
    pairs_df: pd.DataFrame,
    target_size: tuple[int, int],
    mode: str,
    denoise_method: str,
    binarize_output: bool,
    device: torch.device,
    batch_size: int = 64,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Run the (frozen, eval-mode) model over every pair and return
    (distances, labels, forgery_types) as numpy arrays. Never applies
    augmentation -- val/test evaluation must be deterministic.
    """
    dataset = PairDataset(pairs_df, target_size, mode, denoise_method, binarize_output, augment=False)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    model.eval()
    scores, labels, forgery_types = [], [], []
    with torch.no_grad():
        for img_a, img_b, label, forgery_type in loader:
            img_a, img_b = img_a.to(device), img_b.to(device)
            e1, e2 = model(img_a), model(img_b)
            d = pairwise_distance(e1, e2)
            scores.append(d.cpu().numpy())
            labels.append(label.numpy())
            forgery_types.extend(forgery_type)
    return np.concatenate(scores), np.concatenate(labels).astype(int), np.array(forgery_types)


def train_one_config(
    model: torch.nn.Module,
    train_pairs_df: pd.DataFrame,
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
    optimizer: Optional[torch.optim.Optimizer] = None,
) -> tuple[dict, list[dict]]:
    """Train `model` with contrastive loss, early-stopping on validation EER.

    Returns (best_state_dict, history) -- history is a list of per-epoch
    {epoch, train_loss, val_eer} dicts, useful for the margin-sweep report.
    """
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    from sigverify.models.losses import ContrastiveLoss

    criterion = ContrastiveLoss(margin=margin)
    optimizer = optimizer or torch.optim.Adam(
        (p for p in model.parameters() if p.requires_grad), lr=lr
    )

    train_loader = DataLoader(
        PairDataset(train_pairs_df, target_size, mode, denoise_method, binarize_output, augment=True),
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
        for img_a, img_b, label, _ in train_loader:
            img_a, img_b, label = img_a.to(device), img_b.to(device), label.to(device)
            optimizer.zero_grad()
            e1, e2 = model(img_a), model(img_b)
            loss = criterion(e1, e2, label)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * img_a.size(0)
        train_loss = total_loss / max(1, len(train_loader.dataset))

        val_scores, val_labels, _ = compute_pair_scores(
            model, val_pairs_df, target_size, mode, denoise_method, binarize_output, device, batch_size
        )
        far, frr, thresholds = compute_far_frr(val_scores, val_labels)
        val_eer, _ = find_eer(far, frr, thresholds)

        history.append({"epoch": epoch, "train_loss": train_loss, "val_eer": val_eer})
        print(f"[train_one_config] epoch={epoch} train_loss={train_loss:.4f} val_eer={val_eer:.4f}")

        if val_eer < best_eer:
            best_eer = val_eer
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            epochs_without_improvement = 0
        elif epoch >= warmup_epochs:
            epochs_without_improvement += 1
            if epochs_without_improvement >= patience:
                print(f"[train_one_config] Early stopping at epoch {epoch} (best_val_eer={best_eer:.4f})")
                break

    model.load_state_dict(best_state)
    return best_state, history
