"""
Signature generation operations.
"""

from typing import Tuple, Optional
import numpy as np
from csf.core.keys import KeyManager
from csf.fractal.visualizer import FractalSignature
from csf.semantic.vectorizer import SemanticVectorizer
from csf.pqc.dilithium import DilithiumSignature, create_dilithium
from csf.security.validation import validate_string, validate_bytes


def generate_signature(
    message: str,
    semantic_key_text: str,
    math_private_key: bytes,
    use_pqc: bool = True,
    pqc_scheme: str = "Dilithium3",
) -> Tuple[str, Optional[bytes]]:
    """
    Generate a signature for a message.

    Args:
        message: Message to sign
        semantic_key_text: Semantic key
        math_private_key: Private mathematical key
        use_pqc: Whether to use PQC signature scheme
        pqc_scheme: PQC signature scheme to use

    Returns:
        Tuple of (fractal_signature_hash, pqc_signature_bytes)
    """
    validate_string(message, "message")
    validate_string(semantic_key_text, "semantic_key_text")
    validate_bytes(math_private_key, "math_private_key")

    # Initialize components
    key_manager = KeyManager()
    semantic_vectorizer = SemanticVectorizer()
    fractal_signature = FractalSignature()

    # Derive shared secret (simplified - in practice need public key)
    shared_secret = math_private_key[:128]
    shared_secret_arr = np.frombuffer(shared_secret, dtype=np.float64)

    # Transform semantic key
    semantic_vector = semantic_vectorizer.text_to_vector(semantic_key_text)

    # Generate fractal signature
    # CRITICAL FIX (v1.0.16): Pass math_private_key to ensure hash incorporates all inputs
    _, fractal_hash = fractal_signature.generate_signature(
        message, shared_secret_arr, semantic_vector, math_private_key=math_private_key
    )

    # Generate PQC signature if requested
    pqc_signature = None
    if use_pqc:
        try:
            dilithium = create_dilithium(pqc_scheme)
            # In practice, need to derive proper signing key from math_private_key
            pqc_signature = dilithium.sign(message.encode(), math_private_key)
        except Exception:
            # Fallback if PQC not available
            pass

    return fractal_hash, pqc_signature
