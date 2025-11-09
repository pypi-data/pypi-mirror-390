"""
Secure memory operations.

Secure allocation and deallocation of sensitive data.
"""

import numpy as np
from typing import Optional
from csf.security.wiping import wipe_array, wipe_bytes


class SecureMemory:
    """
    Secure memory buffer for sensitive data.

    Automatically wipes memory on deletion.
    """

    def __init__(self, size: int, dtype: type = np.uint8):
        """
        Allocate secure memory buffer.

        Args:
            size: Size of buffer
            dtype: Data type (default: uint8 for bytes)
        """
        self.size = size
        self.dtype = dtype

        if dtype == np.uint8 or dtype == bytes:
            self.data = bytearray(size)
        else:
            self.data = np.zeros(size, dtype=dtype)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Wipe memory on exit."""
        self.wipe()

    def __del__(self):
        """Wipe memory on deletion."""
        try:
            self.wipe()
        except Exception:
            pass  # Ignore errors during cleanup

    def wipe(self) -> None:
        """Securely wipe the memory buffer."""
        if isinstance(self.data, bytearray):
            wipe_bytes(self.data)
        elif isinstance(self.data, np.ndarray):
            wipe_array(self.data)
        self.data = None

    def get_bytes(self) -> bytes:
        """
        Get bytes from secure memory.

        Returns:
            Bytes copy
        """
        if isinstance(self.data, bytearray):
            return bytes(self.data)
        elif isinstance(self.data, np.ndarray):
            return self.data.tobytes()
        else:
            return bytes(self.data)


def secure_alloc(size: int, dtype: type = np.uint8) -> SecureMemory:
    """
    Allocate secure memory buffer.

    Args:
        size: Size of buffer
        dtype: Data type

    Returns:
        SecureMemory instance
    """
    return SecureMemory(size, dtype)


def zeroize(data: Optional[np.ndarray]) -> None:
    """
    Zeroize a numpy array.

    Args:
        data: Array to zeroize (can be None)
    """
    if data is not None:
        wipe_array(data)
