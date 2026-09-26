"""Contrastive loss for the Siamese network.

Label convention (shared with src/sigverify/pairs/generator.py and
src/sigverify/evaluation/metrics.py): y=1 means the pair is the SAME
signer's genuine signatures (should end up with small distance); y=0 means a
forged or cross-signer pair (should end up with distance >= margin).
"""

from __future__ import annotations

import torch
import torch.nn as nn


def pairwise_distance(e1: torch.Tensor, e2: torch.Tensor) -> torch.Tensor:
    """Euclidean distance between two batches of embeddings, shape (N,)."""
    return torch.norm(e1 - e2, p=2, dim=1)


class ContrastiveLoss(nn.Module):
    """L(y, D) = y * D^2 + (1 - y) * max(0, margin - D)^2, averaged over the batch."""

    def __init__(self, margin: float = 1.0):
        super().__init__()
        self.margin = margin

    def forward(self, e1: torch.Tensor, e2: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
        d = pairwise_distance(e1, e2)
        y = y.float()
        same_term = y * d.pow(2)
        diff_term = (1 - y) * torch.clamp(self.margin - d, min=0).pow(2)
        return (same_term + diff_term).mean()
