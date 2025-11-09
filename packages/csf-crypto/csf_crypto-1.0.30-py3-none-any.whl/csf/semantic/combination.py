"""Key combination operations."""

import numpy as np
from csf.security.validation import validate_array


def combine_keys(semantic_vec: np.ndarray, math_key: np.ndarray) -> np.ndarray:
    """
    Combine semantic and mathematical keys.

    Args:
        semantic_vec: Semantic vector
        math_key: Mathematical key

    Returns:
        Combined key vector
    """
    validate_array(semantic_vec, "semantic_vec")
    validate_array(math_key, "math_key")

    min_len = min(len(semantic_vec), len(math_key))
    combined = np.zeros(min_len, dtype=np.float64)

    for i in range(min_len):
        combined[i] = (semantic_vec[i] + math_key[i]) / 2.0

    return combined
