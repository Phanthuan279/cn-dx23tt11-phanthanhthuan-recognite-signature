from sigverify.utils.config import load_config


def test_import_sigverify():
    import sigverify  # noqa: F401


def test_load_default_config():
    config = load_config("configs/default.yaml")
    assert "seed" in config
    assert config["seed"] == 42
