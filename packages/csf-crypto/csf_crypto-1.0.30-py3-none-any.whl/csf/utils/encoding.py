"""Data encoding/decoding utilities."""

import json
from typing import Any, Dict


def encode_json(data: Dict[str, Any]) -> str:
    """
    Encode data to JSON string.

    Args:
        data: Data dictionary

    Returns:
        JSON string
    """
    return json.dumps(data, indent=2)


def decode_json(json_str: str) -> Dict[str, Any]:
    """
    Decode JSON string to data.

    Args:
        json_str: JSON string

    Returns:
        Data dictionary
    """
    return json.loads(json_str)


def encode_base64(data: bytes) -> str:
    """
    Encode bytes to base64 string.

    Args:
        data: Bytes to encode

    Returns:
        Base64 string
    """
    import base64

    return base64.b64encode(data).decode("utf-8")


def decode_base64(base64_str: str) -> bytes:
    """
    Decode base64 string to bytes.

    Args:
        base64_str: Base64 string

    Returns:
        Decoded bytes
    """
    import base64

    return base64.b64decode(base64_str)
