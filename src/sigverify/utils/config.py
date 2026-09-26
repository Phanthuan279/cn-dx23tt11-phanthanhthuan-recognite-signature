"""Load the YAML configuration used across every sigverify script."""

from pathlib import Path
from typing import Any, Dict

import yaml


def load_config(path: str | Path) -> Dict[str, Any]:
    """Read a YAML config file into a plain dict."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
