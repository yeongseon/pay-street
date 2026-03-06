# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportAny=false, reportExplicitAny=false
"""Load and select video templates."""

import os
from typing import Any

import yaml

from paystreet.app.config import get_settings


def load_template(template_id: str) -> dict[str, Any]:
    """Load a video template YAML by ID. Returns the parsed dict."""
    settings = get_settings()
    templates_dir = settings.templates_dir
    path = os.path.join(templates_dir, f"{template_id}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Template not found: {path}")
    with open(path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data if isinstance(data, dict) else {}
