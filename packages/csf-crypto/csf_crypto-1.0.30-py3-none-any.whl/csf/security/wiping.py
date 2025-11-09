"""
Secure memory wiping utilities.

Ensures sensitive data is securely erased from memory.
"""

import numpy as np
import array
from typing import Any


def wipe_bytes(data: bytearray) -> None:
    """
    Securely wipe a bytearray by overwriting with zeros and random data.

    Args:
        data: Bytearray to wipe
    """
    if data is None:
        return

    # Overwrite with zeros
    data[:] = b"\x00" * len(data)

    # Additional pass with random data (best effort)
    try:
        import secrets

        data[:] = secrets.token_bytes(len(data))
        data[:] = b"\x00" * len(data)
    except Exception:
        # If random generation fails, zeros are better than nothing
        pass


def wipe_array(arr: np.ndarray) -> None:
    """
    Securely wipe a numpy array.

    Args:
        arr: Array to wipe
    """
    if arr is None:
        return

    # Fill with zeros
    arr.fill(0)

    # Additional pass with random data
    try:
        import secrets

        random_data = np.frombuffer(secrets.token_bytes(arr.nbytes), dtype=arr.dtype)
        if random_data.size >= arr.size:
            arr.flat[:] = random_data.flat[: arr.size]
        arr.fill(0)
    except Exception:
        # If random generation fails, zeros are better than nothing
        pass


def wipe_list(lst: list) -> None:
    """
    Securely wipe a list containing sensitive data.

    Args:
        lst: List to wipe
    """
    if lst is None:
        return

    for i, item in enumerate(lst):
        if isinstance(item, bytearray):
            wipe_bytes(item)
        elif isinstance(item, np.ndarray):
            wipe_array(item)
        elif isinstance(item, (bytes, str)):
            # Strings/bytes are immutable in Python, so we can't wipe them
            # But we can clear the reference
            lst[i] = None
        elif isinstance(item, list):
            wipe_list(item)

    lst.clear()


def wipe_dict(d: dict) -> None:
    """
    Securely wipe a dictionary containing sensitive data.

    Args:
        d: Dictionary to wipe
    """
    if d is None:
        return

    for key in list(d.keys()):
        value = d[key]

        if isinstance(value, bytearray):
            wipe_bytes(value)
        elif isinstance(value, np.ndarray):
            wipe_array(value)
        elif isinstance(value, list):
            wipe_list(value)
        elif isinstance(value, dict):
            wipe_dict(value)

        del d[key]

    d.clear()


class SecureWipe:
    """Context manager for secure wiping of variables."""

    def __init__(self, *variables):
        """
        Initialize with variables to wipe.

        Args:
            *variables: Variables to securely wipe on exit
        """
        self.variables = variables

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Wipe all variables on exit."""
        for var in self.variables:
            if isinstance(var, bytearray):
                wipe_bytes(var)
            elif isinstance(var, np.ndarray):
                wipe_array(var)
            elif isinstance(var, list):
                wipe_list(var)
            elif isinstance(var, dict):
                wipe_dict(var)
