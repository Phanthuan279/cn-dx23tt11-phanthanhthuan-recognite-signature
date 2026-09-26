"""Config B: transfer-learning Siamese branch built on a pretrained ImageNet
backbone (ResNet18 by default, VGG16 as an alternative), fine-tuned in two
stages (see train_config_b.py):
  stage 1: backbone frozen, only the new embedding layer trains
  stage 2: the backbone's last block is unfrozen too, at a lower learning rate
"""

from __future__ import annotations

from typing import List

import torch
import torch.nn as nn
import torchvision.models as tv_models


class SiameseTransferCNN(nn.Module):
    """Input: (N, 3, 224, 224), ImageNet-normalized. Output: (N, embedding_dim)."""

    def __init__(self, embedding_dim: int = 128, backbone: str = "resnet18", pretrained: bool = True):
        super().__init__()
        self.backbone_name = backbone

        if backbone == "resnet18":
            weights = tv_models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
            net = tv_models.resnet18(weights=weights)
            in_features = net.fc.in_features
            net.fc = nn.Linear(in_features, embedding_dim)
            self.backbone = net
            self.embedding_layer = net.fc
            self.last_block_modules: List[nn.Module] = [net.layer4]
        elif backbone == "vgg16":
            weights = tv_models.VGG16_Weights.IMAGENET1K_V1 if pretrained else None
            net = tv_models.vgg16(weights=weights)
            in_features = net.classifier[6].in_features
            net.classifier[6] = nn.Linear(in_features, embedding_dim)
            self.backbone = net
            self.embedding_layer = net.classifier[6]
            # last conv block of VGG16's features: last 7 layers (3x [Conv,ReLU] + MaxPool)
            self.last_block_modules = list(net.features.children())[-7:]
        else:
            raise ValueError(f"Unknown transfer backbone: {backbone}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.backbone(x)

    def freeze_backbone(self) -> None:
        """Stage 1: freeze everything except the new embedding layer."""
        for p in self.backbone.parameters():
            p.requires_grad = False
        for p in self.embedding_layer.parameters():
            p.requires_grad = True

    def unfreeze_last_block(self) -> None:
        """Stage 2: additionally unfreeze the backbone's last block (embedding
        layer stays trainable from stage 1).
        """
        for module in self.last_block_modules:
            for p in module.parameters():
                p.requires_grad = True

    def param_groups(self, lr_backbone: float, lr_head: float) -> list[dict]:
        """Optimizer param groups for stage 2: last block at a lower lr,
        embedding head at a higher lr.
        """
        backbone_params = [p for m in self.last_block_modules for p in m.parameters() if p.requires_grad]
        head_params = [p for p in self.embedding_layer.parameters() if p.requires_grad]
        return [
            {"params": backbone_params, "lr": lr_backbone},
            {"params": head_params, "lr": lr_head},
        ]
