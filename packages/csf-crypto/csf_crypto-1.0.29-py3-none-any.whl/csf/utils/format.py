"""Format conversion utilities."""

import numpy as np
from typing import List, Any


def array_to_list(arr: np.ndarray) -> List[Any]:
    """
    Convert numpy array to list.

    Args:
        arr: Numpy array

    Returns:
        List
    """
    return arr.tolist()


def list_to_array(lst: List[Any], dtype: type = np.float64) -> np.ndarray:
    """
    Convert list to numpy array.

    Args:
        lst: List
        dtype: Data type

    Returns:
        Numpy array
    """
    return np.array(lst, dtype=dtype)


def bytes_to_array(data: bytes, dtype: type = np.float64) -> np.ndarray:
    """
    Convert bytes to numpy array.

    Args:
        data: Bytes
        dtype: Data type

    Returns:
        Numpy array
    """
    return np.frombuffer(data, dtype=dtype)


def array_to_bytes(arr: np.ndarray) -> bytes:
    """
    Convert numpy array to bytes.

    Args:
        arr: Numpy array

    Returns:
        Bytes
    """
    return arr.tobytes()
