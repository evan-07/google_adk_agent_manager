import json
from typing import Any

def format_as_json(**kwargs: Any) -> str:
    """
    Formats any given keyword arguments into a JSON string.

    Args:
        **kwargs: Arbitrary keyword arguments to include in the JSON output.

    Returns:
        str: A JSON formatted string containing the provided data.
    """
    return json.dumps(kwargs, indent=4)