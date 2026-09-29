import torch

from sigverify.models.losses import ContrastiveLoss, TripletLoss, pairwise_distance


def test_pairwise_distance_matches_euclidean_norm():
    e1 = torch.tensor([[0.0, 0.0], [1.0, 1.0]])
    e2 = torch.tensor([[3.0, 4.0], [1.0, 1.0]])
    d = pairwise_distance(e1, e2)
    assert torch.allclose(d, torch.tensor([5.0, 0.0]))


def test_contrastive_loss_zero_for_perfectly_separated_batch():
    # same-signer pair with distance 0, different-signer pair with distance >= margin
    e1 = torch.tensor([[0.0, 0.0], [0.0, 0.0]])
    e2 = torch.tensor([[0.0, 0.0], [2.0, 0.0]])
    y = torch.tensor([1.0, 0.0])
    loss = ContrastiveLoss(margin=1.0)(e1, e2, y)
    assert loss.item() == 0.0


def test_contrastive_loss_positive_when_not_separated():
    e1 = torch.tensor([[0.0, 0.0]])
    e2 = torch.tensor([[0.5, 0.0]])
    y = torch.tensor([0.0])  # different signer, but distance < margin
    loss = ContrastiveLoss(margin=1.0)(e1, e2, y)
    assert loss.item() > 0.0


def test_triplet_loss_zero_when_negative_already_far_enough():
    anchor = torch.tensor([[0.0, 0.0]])
    positive = torch.tensor([[0.1, 0.0]])
    negative = torch.tensor([[5.0, 0.0]])  # d(a,n) - d(a,p) >> margin
    loss = TripletLoss(margin=1.0)(anchor, positive, negative)
    assert loss.item() == 0.0


def test_triplet_loss_positive_when_negative_too_close():
    anchor = torch.tensor([[0.0, 0.0]])
    positive = torch.tensor([[2.0, 0.0]])  # far from anchor
    negative = torch.tensor([[0.1, 0.0]])  # closer to anchor than positive is
    loss = TripletLoss(margin=1.0)(anchor, positive, negative)
    assert loss.item() > 0.0
