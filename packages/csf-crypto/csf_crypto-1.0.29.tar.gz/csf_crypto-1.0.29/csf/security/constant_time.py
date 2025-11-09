"""
Constant-time operations for side-channel protection.

All operations must execute in constant time regardless of secret data values.
"""

import secrets
from typing import Any
import numpy as np


def compare_digest(a: bytes, b: bytes) -> bool:
    """
    Constant-time comparison of two byte strings.

    Args:
        a: First byte string
        b: Second byte string

    Returns:
        True if strings are equal, False otherwise
    """
    if len(a) != len(b):
        return False
    return secrets.compare_digest(a, b)


def compare_arrays(arr1: np.ndarray, arr2: np.ndarray) -> bool:
    """
    Constant-time comparison of two numpy arrays.

    Args:
        arr1: First array
        arr2: Second array

    Returns:
        True if arrays are equal, False otherwise
    """
    if arr1.shape != arr2.shape:
        return False

    # Convert to bytes for constant-time comparison
    arr1_bytes = arr1.tobytes()
    arr2_bytes = arr2.tobytes()

    return compare_digest(arr1_bytes, arr2_bytes)


def select(condition: bool, true_val: Any, false_val: Any) -> Any:
    """
    Constant-time selection: returns true_val if condition is True, false_val otherwise.

    Uses bitwise operations to avoid branches.

    Args:
        condition: Boolean condition
        true_val: Value to return if condition is True
        false_val: Value to return if condition is False

    Returns:
        Selected value
    """
    # Use bitwise operations to avoid branches
    mask = -1 if condition else 0

    if isinstance(true_val, bytes) and isinstance(false_val, bytes):
        if len(true_val) != len(false_val):
            raise ValueError("Values must have same length for constant-time selection")
        result = bytearray(len(true_val))
        for i in range(len(true_val)):
            result[i] = (true_val[i] & mask) | (false_val[i] & ~mask)
        return bytes(result)
    elif isinstance(true_val, (int, float)) and isinstance(false_val, (int, float)):
        return (true_val & mask) | (false_val & ~mask)
    else:
        # For other types, we still want to minimize timing differences
        # but may need to use conditional (not perfectly constant-time)
        return true_val if condition else false_val


def select_int(condition: bool, true_val: int, false_val: int) -> int:
    """
    Constant-time integer selection.

    Args:
        condition: Boolean condition
        true_val: Integer to return if condition is True
        false_val: Integer to return if condition is False

    Returns:
        Selected integer
    """
    mask = -1 if condition else 0
    return (true_val & mask) | (false_val & ~mask)


def constant_time_equals(a: bytes, b: bytes) -> bool:
    """
    Constant-time equality check for byte strings.

    Args:
        a: First byte string
        b: Second byte string

    Returns:
        True if equal, False otherwise
    """
    return secrets.compare_digest(a, b)


def zeroize_array(arr: np.ndarray) -> None:
    """
    Securely zeroize a numpy array.

    Args:
        arr: Array to zeroize
    """
    arr.fill(0)


def constant_time_or(a: bool, b: bool) -> bool:
    """
    Constant-time OR operation.

    Args:
        a: First boolean
        b: Second boolean

    Returns:
        Result of a OR b
    """
    return bool(a | b)


def constant_time_and(a: bool, b: bool) -> bool:
    """
    Constant-time AND operation.

    Args:
        a: First boolean
        b: Second boolean

    Returns:
        Result of a AND b
    """
    return bool(a & b)
