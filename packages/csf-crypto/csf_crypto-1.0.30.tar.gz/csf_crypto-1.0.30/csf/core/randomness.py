"""
Cryptographically Secure Pseudorandom Number Generator (CSPRNG).

Replaces insecure numpy.random with secure alternatives.
"""

import secrets
import numpy as np
from typing import Optional, Tuple


class CSPRNG:
    """
    Cryptographically Secure Pseudorandom Number Generator.

    Wraps Python's secrets module for secure randomness.
    """

    @staticmethod
    def random_bytes(length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.

        Args:
            length: Number of bytes to generate

        Returns:
            Random bytes
        """
        if length < 0:
            raise ValueError("Length must be non-negative")

        return secrets.token_bytes(length)

    @staticmethod
    def random_int(min_val: int, max_val: int) -> int:
        """
        Generate cryptographically secure random integer in range [min_val, max_val).

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)

        Returns:
            Random integer
        """
        if min_val >= max_val:
            raise ValueError("min_val must be less than max_val")

        return secrets.randbelow(max_val - min_val) + min_val

    @staticmethod
    def random_array(shape: Tuple[int, ...], dtype: type = np.float64) -> np.ndarray:
        """
        Generate cryptographically secure random array.

        Args:
            shape: Array shape
            dtype: Array dtype

        Returns:
            Random array
        """
        total_size = 1
        for dim in shape:
            total_size *= dim

        # Generate bytes based on dtype
        if dtype == np.uint8 or dtype == np.int8:
            bytes_needed = total_size
        elif dtype == np.uint16 or dtype == np.int16:
            bytes_needed = total_size * 2
        elif dtype == np.uint32 or dtype == np.int32:
            bytes_needed = total_size * 4
        elif dtype == np.uint64 or dtype == np.int64 or dtype == np.float64:
            bytes_needed = total_size * 8
        elif dtype == np.float32:
            bytes_needed = total_size * 4
        else:
            # Default to float64
            bytes_needed = total_size * 8

        random_bytes = secrets.token_bytes(bytes_needed)
        arr = np.frombuffer(random_bytes, dtype=dtype)

        # Ensure we have exactly the right size
        if arr.size >= total_size:
            arr = arr[:total_size]
        else:
            # If not enough, pad with more random bytes
            additional = secrets.token_bytes(bytes_needed - len(random_bytes))
            random_bytes = random_bytes + additional
            arr = np.frombuffer(random_bytes, dtype=dtype)[:total_size]

        return arr.reshape(shape).copy()  # Make a copy to ensure contiguous memory

    @staticmethod
    def random_vector(dimension: int, dtype: type = np.float64) -> np.ndarray:
        """
        Generate cryptographically secure random vector.

        Args:
            dimension: Vector dimension
            dtype: Vector dtype

        Returns:
            Random vector
        """
        return CSPRNG.random_array((dimension,), dtype=dtype)

    @staticmethod
    def random_matrix(rows: int, cols: int, dtype: type = np.float64) -> np.ndarray:
        """
        Generate cryptographically secure random matrix.

        Args:
            rows: Number of rows
            cols: Number of columns
            dtype: Matrix dtype

        Returns:
            Random matrix
        """
        return CSPRNG.random_array((rows, cols), dtype=dtype)

    @staticmethod
    def random_choice(elements: list, count: int = 1) -> list:
        """
        Generate cryptographically secure random choices.

        Args:
            elements: List of elements to choose from
            count: Number of choices

        Returns:
            List of randomly chosen elements
        """
        if count > len(elements):
            raise ValueError("count cannot exceed number of elements")

        # Use secrets.randbelow for each choice
        chosen_indices = set()
        while len(chosen_indices) < count:
            idx = secrets.randbelow(len(elements))
            chosen_indices.add(idx)

        return [elements[idx] for idx in chosen_indices]

    @staticmethod
    def random_normal(size: int, mean: float = 0.0, stddev: float = 1.0) -> np.ndarray:
        """
        Generate cryptographically secure random values from normal distribution.

        Uses Box-Muller transform for conversion.

        Args:
            size: Number of values to generate
            mean: Mean of distribution
            stddev: Standard deviation

        Returns:
            Random values from normal distribution
        """
        # Box-Muller transform requires even number of samples
        n_samples = size if size % 2 == 0 else size + 1

        # Generate uniform random values [0, 1)
        u1 = CSPRNG.random_array((n_samples // 2,), dtype=np.float64)
        u2 = CSPRNG.random_array((n_samples // 2,), dtype=np.float64)

        # Avoid zero values
        u1 = np.maximum(u1, 1e-10)
        u2 = np.maximum(u2, 1e-10)

        # Box-Muller transform
        z0 = np.sqrt(-2.0 * np.log(u1)) * np.cos(2.0 * np.pi * u2)
        z1 = np.sqrt(-2.0 * np.log(u1)) * np.sin(2.0 * np.pi * u2)

        # Combine and scale
        z = np.concatenate([z0, z1])[:size]
        z = z * stddev + mean

        return z


# Global CSPRNG instance
csprng = CSPRNG()


# Convenience functions
def random_bytes(length: int) -> bytes:
    """Generate random bytes."""
    return csprng.random_bytes(length)


def random_int(min_val: int, max_val: int) -> int:
    """Generate random integer."""
    return csprng.random_int(min_val, max_val)


def random_array(shape: Tuple[int, ...], dtype: type = np.float64) -> np.ndarray:
    """Generate random array."""
    return csprng.random_array(shape, dtype)


def random_vector(dimension: int, dtype: type = np.float64) -> np.ndarray:
    """Generate random vector."""
    return csprng.random_vector(dimension, dtype)


def random_matrix(rows: int, cols: int, dtype: type = np.float64) -> np.ndarray:
    """Generate random matrix."""
    return csprng.random_matrix(rows, cols, dtype)
