"""Load the YAML configuration used across every sigverify script."""

from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str | Path) -> Dict[str, Any]:
    """Read a YAML config file into a plain dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def merge_configs(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep-merge `override` into a copy of `base` (nested dicts merge key-by-key;
    any other value type in `override` replaces the base value outright).
    """
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = merge_configs(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config_with_override(base_path: str | Path, override_path: str | Path) -> Dict[str, Any]:
    """Load `base_path` then deep-merge `override_path` on top of it.

    Used for the Phase 7 ablation variants: each override file only lists the
    one setting it changes, instead of duplicating the whole default config.
    """
    base = load_config(base_path)
    override = load_config(override_path)
    return merge_configs(base, override)
