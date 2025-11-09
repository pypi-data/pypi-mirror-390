"""
Semantic key vectorizer.

Transforms text to numerical vectors.
"""

from functools import lru_cache
from typing import Optional
import numpy as np
from csf.core.fractal_hash import fractal_hash
from csf.security.validation import validate_string
from csf.core.randomness import CSPRNG


class SemanticVectorizer:
    """
    Converts semantic input (text/symbols) to numerical vectors.
    """

    def __init__(self, vector_dim: int = 128):
        """
        Initialize semantic vectorizer.

        Args:
            vector_dim: Dimension of output vector
        """
        self.vector_dim = vector_dim
        self.csprng = CSPRNG()

    def text_to_vector(self, text: str) -> np.ndarray:
        """
        Convert text to numerical vector using hash-based embedding.

        Args:
            text: Input text

        Returns:
            Normalized numerical vector
        """
        validate_string(text, "text")

        # Use multiple hash functions to create diverse features
        vectors = []
        # We need enough hashes to fill vector_dim
        # Each hash gives 8 float32 values (32 bytes)
        n_hashes = (self.vector_dim + 7) // 8

        for i in range(n_hashes):
            # Create hash with different salts using fractal hash (100% fractal-based)
            salt = f"salt_{i}".encode()
            combined = (text + str(i)).encode() + salt
            # Use fractal hash instead of SHA-256 for protocol alignment
            hash_bytes = fractal_hash(combined, output_length=32)

            # Convert to float array (8 floats per 32 bytes)
            # Use uint32 first, then convert to float to avoid NaN/Inf
            hash_ints = np.frombuffer(hash_bytes, dtype=np.uint32)
            # Convert to float in [0, 1) range
            hash_floats = (hash_ints.astype(np.float32) / np.iinfo(np.uint32).max)[:8]
            vectors.append(hash_floats)

        # Concatenate and ensure correct dimension
        if vectors:
            vector = np.concatenate(vectors)[: self.vector_dim]
        else:
            vector = np.zeros(self.vector_dim, dtype=np.float32)

        # If we don't have enough, pad with repeated hash
        if len(vector) < self.vector_dim:
            # Repeat last elements
            needed = self.vector_dim - len(vector)
            padding = np.tile(vector[-8:], (needed // 8 + 1))[:needed]
            vector = np.concatenate([vector, padding])

        # Normalize to unit sphere (constant-time normalization)
        norm = np.linalg.norm(vector)
        if norm > 1e-10:  # Avoid division by zero
            vector = vector / norm
        else:
            # If zero vector, use deterministic random vector from fractal hash
            # Use fractal hash instead of SHA-256 for protocol alignment
            fallback_hash = fractal_hash(text.encode(), output_length=32)
            fallback_ints = np.frombuffer(
                fallback_hash * (self.vector_dim // 4 + 1), dtype=np.uint32
            )
            vector = fallback_ints[: self.vector_dim].astype(np.float32) / np.iinfo(np.uint32).max
            norm = np.linalg.norm(vector)
            if norm > 1e-10:
                vector = vector / norm
            else:
                # Last resort: uniform vector
                vector = np.ones(self.vector_dim, dtype=np.float32) / np.sqrt(self.vector_dim)

        return vector.astype(np.float64)  # Return as float64 for consistency

    def combine_keys(self, semantic_vec: np.ndarray, math_key: np.ndarray) -> np.ndarray:
        """
        Combine semantic and mathematical keys.

        Args:
            semantic_vec: Semantic vector
            math_key: Mathematical key

        Returns:
            Combined key vector
        """
        min_len = min(len(semantic_vec), len(math_key))

        # OPTIMIZED: Vectorized combination (much faster than loop)
        combined = (semantic_vec[:min_len] + math_key[:min_len]) / 2.0

        return combined
