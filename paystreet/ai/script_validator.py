"""Validate AI-generated script JSON."""

import json
from paystreet.ai.llm import ScriptContent


def validate_script_json(raw: str) -> ScriptContent:
    """Parse and validate raw JSON string into ScriptContent. Raises ValueError on failure."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Script is not valid JSON: {e}") from e

    if "hook" not in data:
        raise ValueError("Script missing 'hook' field")
    if "dialogue" not in data or not isinstance(data["dialogue"], list):
        raise ValueError("Script missing or invalid 'dialogue' field")
    if "outro" not in data:
        raise ValueError("Script missing 'outro' field")
    if len(data["dialogue"]) == 0:
        raise ValueError("Script dialogue cannot be empty")

    return ScriptContent(**data)
