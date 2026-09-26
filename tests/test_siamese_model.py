import torch

from sigverify.models.losses import ContrastiveLoss, pairwise_distance
from sigverify.models.siamese_scratch import SiameseScratchCNN


def test_forward_pass_output_shape():
    model = SiameseScratchCNN(embedding_dim=128)
    x = torch.randn(4, 1, 150, 220)  # (N, C, H, W); H,W from image.size_scratch=[220,150]
    out = model(x)
    assert out.shape == (4, 128)


def test_l2_normalize_option_produces_unit_vectors():
    model = SiameseScratchCNN(embedding_dim=128, l2_normalize=True)
    x = torch.randn(2, 1, 150, 220)
    out = model(x)
    norms = torch.norm(out, p=2, dim=1)
    assert torch.allclose(norms, torch.ones(2), atol=1e-5)


def test_pairwise_distance():
    e1 = torch.tensor([[0.0, 0.0]])
    e2 = torch.tensor([[3.0, 4.0]])
    d = pairwise_distance(e1, e2)
    assert torch.isclose(d, torch.tensor([5.0]))


def test_contrastive_loss_same_pair_zero_distance_gives_zero_loss():
    loss_fn = ContrastiveLoss(margin=1.0)
    e1, e2 = torch.zeros(1, 4), torch.zeros(1, 4)
    loss = loss_fn(e1, e2, torch.tensor([1.0]))
    assert torch.isclose(loss, torch.tensor(0.0))


def test_contrastive_loss_different_pair_within_margin():
    # D=0, different pair (y=0), margin=1 -> loss = max(0, 1-0)^2 = 1
    loss_fn = ContrastiveLoss(margin=1.0)
    e1, e2 = torch.zeros(1, 4), torch.zeros(1, 4)
    loss = loss_fn(e1, e2, torch.tensor([0.0]))
    assert torch.isclose(loss, torch.tensor(1.0))


def test_contrastive_loss_different_pair_beyond_margin_is_zero():
    # D=2 > margin=1 -> hinge clamps to 0
    loss_fn = ContrastiveLoss(margin=1.0)
    e1 = torch.zeros(1, 4)
    e2 = torch.tensor([[2.0, 0.0, 0.0, 0.0]])
    loss = loss_fn(e1, e2, torch.tensor([0.0]))
    assert torch.isclose(loss, torch.tensor(0.0))
