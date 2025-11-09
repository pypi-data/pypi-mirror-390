"""
QUANTUM SECURITY: Entropy validation for semantic keys.

Ensures semantic keys have sufficient entropy to resist quantum attacks.
"""

import numpy as np
from typing import Optional
from csf.security.validation import validate_string


def calculate_shannon_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of text.
    
    Args:
        text: Input text
    
    Returns:
        Entropy value (0.0 to log2(alphabet_size))
    """
    if len(text) == 0:
        return 0.0
    
    # Count character frequencies
    char_counts = {}
    for char in text:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # Calculate Shannon entropy: H = -Σ(p * log2(p))
    entropy = 0.0
    length = len(text)
    for count in char_counts.values():
        p = count / length
        if p > 0:
            entropy -= p * np.log2(p)
    
    return float(entropy)


def check_semantic_key_entropy(semantic_key: str, min_entropy: float = 3.0) -> tuple[bool, float, Optional[str]]:
    """
    Check if semantic key has sufficient entropy.
    
    QUANTUM SECURITY: Ensures semantic keys have enough entropy to resist
    quantum brute-force attacks. Low entropy keys can be targeted by
    quantum search algorithms.
    
    Args:
        semantic_key: Semantic key text
        min_entropy: Minimum required entropy (bits per character)
                    Default 3.0 = ~8 bits for ASCII (reasonable security)
    
    Returns:
        Tuple of (is_valid, actual_entropy, warning_message)
    """
    validate_string(semantic_key, "semantic_key")
    
    entropy = calculate_shannon_entropy(semantic_key)
    
    # Check minimum entropy
    if entropy < min_entropy:
        warning = (
            f"Semantic key entropy ({entropy:.2f} bits/char) is below recommended minimum "
            f"({min_entropy:.2f} bits/char). This may be vulnerable to quantum brute-force attacks. "
            f"Consider using a longer or more diverse key."
        )
        return False, entropy, warning
    
    # Check for very short keys (even with good entropy per char, total entropy might be low)
    min_total_entropy = 32.0  # Minimum 32 bits total entropy for quantum security
    total_entropy = entropy * len(semantic_key)
    
    if total_entropy < min_total_entropy:
        warning = (
            f"Semantic key total entropy ({total_entropy:.2f} bits) is below recommended minimum "
            f"({min_total_entropy:.2f} bits). Consider using a longer key."
        )
        return False, entropy, warning
    
    return True, entropy, None


def ensure_minimum_entropy(semantic_key: str, min_entropy: float = 3.0) -> str:
    """
    Ensure semantic key has minimum entropy by padding if necessary.
    
    QUANTUM SECURITY: If key entropy is too low, pad with high-entropy material.
    
    Args:
        semantic_key: Semantic key text
        min_entropy: Minimum required entropy
    
    Returns:
        Key with ensured minimum entropy (may be padded)
    """
    is_valid, entropy, warning = check_semantic_key_entropy(semantic_key, min_entropy)
    
    if is_valid:
        return semantic_key
    
    # Add high-entropy padding
    from csf.core.randomness import CSPRNG
    csprng = CSPRNG()
    
    # Generate random padding
    padding_length = max(8, len(semantic_key))  # At least 8 chars of padding
    padding = csprng.generate_bytes(padding_length).hex()[:padding_length]
    
    # Combine with original key
    padded_key = semantic_key + padding
    
    return padded_key

