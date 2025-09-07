import re
from typing import Dict


def parse_fields(text: str) -> Dict[str, str]:
    """A very small placeholder for an LLM that extracts key/value pairs.

    Expected format: "key=value" separated by commas or newlines.
    """
    parts = re.split(r"[\n,]+", text)
    data: Dict[str, str] = {}
    for part in parts:
        if "=" in part:
            k, v = part.split("=", 1)
        elif ":" in part:
            k, v = part.split(":", 1)
        else:
            continue
        data[k.strip()] = v.strip()
    return data
