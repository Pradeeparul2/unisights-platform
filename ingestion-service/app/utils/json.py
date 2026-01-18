import json
from typing import Any


def safe_json_loads(data: str) -> Any:
    """
    Safely parse JSON string.

    Raises ValueError on failure.
    """
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON payload") from e
