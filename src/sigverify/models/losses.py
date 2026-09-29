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


class TripletLoss(nn.Module):
    """L(a, p, n) = max(0, d(a,p) - d(a,n) + margin), averaged over the batch.

    Anchor/positive are two genuine signatures of the same writer; negative is
    either a skilled forgery or a genuine signature of a different writer
    (see sigverify/pairs/generator.py::build_triplets_from_pairs).
    """

    def __init__(self, margin: float = 1.0):
        super().__init__()
        self.margin = margin

    def forward(self, anchor: torch.Tensor, positive: torch.Tensor, negative: torch.Tensor) -> torch.Tensor:
        d_pos = pairwise_distance(anchor, positive)
        d_neg = pairwise_distance(anchor, negative)
        return torch.clamp(d_pos - d_neg + self.margin, min=0).mean()
