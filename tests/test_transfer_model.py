import torch

from sigverify.models.siamese_transfer import SiameseTransferCNN


def _count_trainable(model) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def test_resnet18_forward_pass_output_shape():
    model = SiameseTransferCNN(embedding_dim=128, backbone="resnet18", pretrained=False)
    x = torch.randn(2, 3, 224, 224)
    out = model(x)
    assert out.shape == (2, 128)


def test_resnet18_freeze_backbone_leaves_only_embedding_layer_trainable():
    model = SiameseTransferCNN(embedding_dim=128, backbone="resnet18", pretrained=False)
    model.freeze_backbone()
    trainable = _count_trainable(model)
    expected = sum(p.numel() for p in model.embedding_layer.parameters())
    assert trainable == expected
    assert trainable > 0


def test_resnet18_unfreeze_last_block_increases_trainable_params():
    model = SiameseTransferCNN(embedding_dim=128, backbone="resnet18", pretrained=False)
    model.freeze_backbone()
    before = _count_trainable(model)
    model.unfreeze_last_block()
    after = _count_trainable(model)
    assert after > before

    expected_last_block = sum(p.numel() for m in model.last_block_modules for p in m.parameters())
    expected_head = sum(p.numel() for p in model.embedding_layer.parameters())
    assert after == expected_last_block + expected_head


def test_vgg16_forward_pass_output_shape():
    model = SiameseTransferCNN(embedding_dim=128, backbone="vgg16", pretrained=False)
    x = torch.randn(1, 3, 224, 224)
    out = model(x)
    assert out.shape == (1, 128)


def test_param_groups_have_different_learning_rates():
    model = SiameseTransferCNN(embedding_dim=128, backbone="resnet18", pretrained=False)
    model.freeze_backbone()
    model.unfreeze_last_block()
    groups = model.param_groups(lr_backbone=1e-5, lr_head=1e-4)
    assert len(groups) == 2
    assert groups[0]["lr"] == 1e-5
    assert groups[1]["lr"] == 1e-4
    assert len(groups[0]["params"]) > 0
    assert len(groups[1]["params"]) > 0
