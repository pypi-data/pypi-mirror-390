"""
Input validation with constant-time checks.

Validates all inputs before cryptographic processing.
"""

from typing import Any, Optional
import numpy as np
from csf.utils.exceptions import ValidationError
from csf.security.constant_time import compare_digest


def validate_not_none(value: Any, name: str) -> None:
    """
    Validate that a value is not None.

    Args:
        value: Value to validate
        name: Name of the parameter (for error messages)

    Raises:
        ValidationError: If value is None
    """
    if value is None:
        raise ValidationError(f"{name} cannot be None")


def validate_bytes(
    data: bytes, name: str, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> None:
    """
    Validate byte string input.

    Args:
        data: Byte string to validate
        name: Name of the parameter
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)

    Raises:
        ValidationError: If validation fails
    """
    validate_not_none(data, name)

    if not isinstance(data, bytes):
        raise ValidationError(f"{name} must be bytes, got {type(data)}")

    if min_length is not None and len(data) < min_length:
        raise ValidationError(f"{name} length {len(data)} < minimum {min_length}")

    if max_length is not None and len(data) > max_length:
        raise ValidationError(f"{name} length {len(data)} > maximum {max_length}")


def validate_string(
    text: str, name: str, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> None:
    """
    Validate string input.

    Args:
        text: String to validate
        name: Name of the parameter
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)

    Raises:
        ValidationError: If validation fails
    """
    validate_not_none(text, name)

    if not isinstance(text, str):
        raise ValidationError(f"{name} must be str, got {type(text)}")

    if min_length is not None and len(text) < min_length:
        raise ValidationError(f"{name} length {len(text)} < minimum {min_length}")

    if max_length is not None and len(text) > max_length:
        raise ValidationError(f"{name} length {len(text)} > maximum {max_length}")


def validate_string_or_bytes(
    text, name: str, min_length: Optional[int] = None, max_length: Optional[int] = None
) -> str:
    """
    Validate string or bytes input, converting bytes to string if needed.

    Args:
        text: String or bytes to validate
        name: Name of the parameter
        min_length: Minimum length (inclusive)
        max_length: Maximum length (inclusive)

    Returns:
        String representation of the input

    Raises:
        ValidationError: If validation fails
    """
    validate_not_none(text, name)

    # Convert bytes to str if needed
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError:
            raise ValidationError(f"{name} bytes must be valid UTF-8")
    elif not isinstance(text, str):
        raise ValidationError(f"{name} must be str or bytes, got {type(text)}")

    if min_length is not None and len(text) < min_length:
        raise ValidationError(f"{name} length {len(text)} < minimum {min_length}")

    if max_length is not None and len(text) > max_length:
        raise ValidationError(f"{name} length {len(text)} > maximum {max_length}")

    return text


def validate_array(
    arr: np.ndarray,
    name: str,
    dtype: Optional[type] = None,
    shape: Optional[tuple] = None,
    min_size: Optional[int] = None,
) -> None:
    """
    Validate numpy array input.

    Args:
        arr: Array to validate
        name: Name of the parameter
        dtype: Expected dtype
        shape: Expected shape (None for any)
        min_size: Minimum total size

    Raises:
        ValidationError: If validation fails
    """
    validate_not_none(arr, name)

    if not isinstance(arr, np.ndarray):
        raise ValidationError(f"{name} must be numpy.ndarray, got {type(arr)}")

    if dtype is not None and arr.dtype != dtype:
        raise ValidationError(f"{name} dtype must be {dtype}, got {arr.dtype}")

    if shape is not None and arr.shape != shape:
        raise ValidationError(f"{name} shape must be {shape}, got {arr.shape}")

    if min_size is not None and arr.size < min_size:
        raise ValidationError(f"{name} size {arr.size} < minimum {min_size}")


def validate_positive_int(value: int, name: str) -> None:
    """
    Validate positive integer.

    Args:
        value: Integer to validate
        name: Name of the parameter

    Raises:
        ValidationError: If validation fails
    """
    validate_not_none(value, name)

    if not isinstance(value, int):
        raise ValidationError(f"{name} must be int, got {type(value)}")

    if value <= 0:
        raise ValidationError(f"{name} must be positive, got {value}")


def validate_in_range(value: float, name: str, min_val: float, max_val: float) -> None:
    """
    Validate float value is in range.

    Args:
        value: Float to validate
        name: Name of the parameter
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Raises:
        ValidationError: If validation fails
    """
    validate_not_none(value, name)

    if not isinstance(value, (int, float)):
        raise ValidationError(f"{name} must be numeric, got {type(value)}")

    if value < min_val or value > max_val:
        raise ValidationError(f"{name} {value} not in range [{min_val}, {max_val}]")


def validate_key_length(key: bytes, expected_length: int, name: str = "key") -> None:
    """
    Validate key length matches expected value.

    Uses constant-time comparison to avoid timing leaks.

    Args:
        key: Key bytes to validate
        expected_length: Expected key length
        name: Name of the parameter

    Raises:
        ValidationError: If length doesn't match
    """
    validate_bytes(key, name)

    # Use constant-time length comparison
    actual_len_bytes = len(key).to_bytes(8, "big")
    expected_len_bytes = expected_length.to_bytes(8, "big")

    if not compare_digest(actual_len_bytes, expected_len_bytes):
        raise ValidationError(f"{name} length mismatch: expected {expected_length}, got {len(key)}")
