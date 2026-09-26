"""Deterministic seeding across random, numpy and torch."""

import random

import numpy as np


def set_seed(seed: int) -> None:
    """Fix the seed for random, numpy and torch (CPU and CUDA) if torch is installed."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass
