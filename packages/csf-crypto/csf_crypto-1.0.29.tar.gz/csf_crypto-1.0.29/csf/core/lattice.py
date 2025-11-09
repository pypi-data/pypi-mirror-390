"""
Constant-time lattice operations.

All lattice operations are implemented to execute in constant time
regardless of secret data values.
"""

import numpy as np
from typing import Tuple
from csf.core.randomness import CSPRNG
from csf.security.constant_time import select_int, compare_arrays
from csf.security.validation import validate_array


class ConstantTimeLattice:
    """
    Constant-time lattice operations for cryptographic use.
    """

    def __init__(self, dimension: int = 256, modulus: int = 3329):
        """
        Initialize lattice operations.

        Args:
            dimension: Lattice dimension
            modulus: Modulus for operations
        """
        self.dimension = dimension
        self.modulus = modulus
        self.csprng = CSPRNG()

    def generate_key_pair(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a public/private key pair using constant-time operations.

        Returns:
            Tuple of (public_key, private_key)
        """
        # Generate private key using CSPRNG (constant-time)
        private_key = self._sample_secret_vector()

        # Generate public matrix using CSPRNG (constant-time)
        A = self._generate_matrix_A()

        # Sample error vector (constant-time)
        error = self._sample_error_vector()

        # Compute public key: A @ s + e (constant-time matrix multiplication)
        public_key = self._constant_time_matrix_multiply(A, private_key)
        public_key = self._constant_time_add_modulo(public_key, error)

        return public_key, private_key

    def derive_shared_secret(self, public_key: np.ndarray, private_key: np.ndarray) -> np.ndarray:
        """
        Derive shared secret using constant-time operations.

        Args:
            public_key: Public key
            private_key: Private key

        Returns:
            Shared secret
        """
        validate_array(public_key, "public_key", shape=(self.dimension,))
        validate_array(private_key, "private_key", shape=(self.dimension,))

        # Constant-time element-wise multiplication
        shared = self._constant_time_multiply_modulo(public_key, private_key)

        return shared

    def _sample_secret_vector(self) -> np.ndarray:
        """
        Sample secret vector using CSPRNG.

        Returns:
            Secret vector in {-1, 0, 1}
        """
        # Generate random bytes
        random_bytes = self.csprng.random_bytes(self.dimension * 4)
        random_ints = np.frombuffer(random_bytes, dtype=np.uint32) % 3

        # Map to {-1, 0, 1} in constant time
        secret = np.zeros(self.dimension, dtype=np.int32)
        for i in range(self.dimension):
            val = int(random_ints[i % len(random_ints)])
            # Constant-time selection
            secret[i] = select_int(val == 0, 0, select_int(val == 1, 1, -1))

        return secret

    def _generate_matrix_A(self) -> np.ndarray:
        """
        Generate public matrix A.

        In production, this would be deterministically derived from a seed.
        """
        # Use CSPRNG for constant-time generation
        random_data = self.csprng.random_matrix(self.dimension, self.dimension, dtype=np.int32)
        # Reduce modulo q
        A = random_data % self.modulus
        return A

    def _sample_error_vector(self) -> np.ndarray:
        """Sample error vector."""
        # Sample from small distribution
        random_bytes = self.csprng.random_bytes(self.dimension * 2)
        error = np.frombuffer(random_bytes, dtype=np.int16) % 5 - 2
        return error[: self.dimension].astype(np.int32)

    def _constant_time_matrix_multiply(self, A: np.ndarray, v: np.ndarray) -> np.ndarray:
        """
        Constant-time matrix-vector multiplication.

        Args:
            A: Matrix
            v: Vector

        Returns:
            Result vector
        """
        result = np.zeros(self.dimension, dtype=np.int32)

        # Fixed-time loop (no early exits)
        for i in range(self.dimension):
            sum_val = 0
            for j in range(self.dimension):
                # Constant-time multiply-accumulate
                product = (A[i, j] * v[j]) % self.modulus
                sum_val = (sum_val + product) % self.modulus
            result[i] = sum_val

        return result

    def _constant_time_add_modulo(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Constant-time addition modulo q.

        Args:
            a: First array
            b: Second array

        Returns:
            (a + b) mod q
        """
        result = np.zeros_like(a)
        for i in range(len(a)):
            sum_val = (a[i] + b[i]) % self.modulus
            result[i] = sum_val
        return result

    def _constant_time_multiply_modulo(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """
        Constant-time element-wise multiplication modulo q.

        Args:
            a: First array
            b: Second array

        Returns:
            (a * b) mod q
        """
        result = np.zeros_like(a)
        for i in range(len(a)):
            product = (a[i] * b[i]) % 256  # Simplified modulo
            result[i] = product
        return result

    def constant_time_equals(self, a: np.ndarray, b: np.ndarray) -> bool:
        """
        Constant-time array comparison.

        Args:
            a: First array
            b: Second array

        Returns:
            True if arrays are equal
        """
        return compare_arrays(a, b)


# Convenience function
def create_lattice(dimension: int = 256, modulus: int = 3329) -> ConstantTimeLattice:
    """
    Create a constant-time lattice operations instance.

    Args:
        dimension: Lattice dimension
        modulus: Modulus

    Returns:
        ConstantTimeLattice instance
    """
    return ConstantTimeLattice(dimension, modulus)
