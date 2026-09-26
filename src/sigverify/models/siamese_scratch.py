"""Config A: a from-scratch CNN Siamese branch (5 Conv+BN+ReLU+MaxPool blocks
+ 2 fully-connected layers -> 128-d embedding), with shared weights realized
simply by calling the same module instance on both images of a pair.
"""

from __future__ import annotations

import torch
import torch.nn as nn


def _conv_block(in_channels: int, out_channels: int) -> nn.Sequential:
    return nn.Sequential(
        nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
        nn.BatchNorm2d(out_channels),
        nn.ReLU(inplace=True),
        nn.MaxPool2d(2),
    )


class SiameseScratchCNN(nn.Module):
    """Input: (N, 1, H, W) grayscale. Output: (N, embedding_dim) embedding.

    Not L2-normalized by default (see model.l2_normalize in configs/default.yaml)
    so the full margin sweep {0.5, 1.0, 2.0} stays meaningful (a normalized
    embedding caps Euclidean distance at 2, which would make margin=2 nearly
    always saturate).
    """

    def __init__(self, embedding_dim: int = 128, l2_normalize: bool = False):
        super().__init__()
        self.l2_normalize = l2_normalize
        self.features = nn.Sequential(
            _conv_block(1, 32),
            _conv_block(32, 64),
            _conv_block(64, 128),
            _conv_block(128, 256),
            _conv_block(256, 256),
        )
        # AdaptiveAvgPool makes the flatten dimension independent of the exact
        # input size, so changing image.size_scratch in the config never
        # breaks the architecture.
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, embedding_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.features(x)
        x = self.pool(x)
        embedding = self.head(x)
        if self.l2_normalize:
            embedding = nn.functional.normalize(embedding, p=2, dim=1)
        return embedding
