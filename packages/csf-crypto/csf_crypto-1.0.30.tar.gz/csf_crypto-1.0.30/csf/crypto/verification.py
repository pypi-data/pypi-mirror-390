"""
Signature verification operations.
"""

from typing import Optional
import numpy as np
from csf.core.keys import KeyManager
from csf.fractal.visualizer import FractalSignature
from csf.semantic.vectorizer import SemanticVectorizer
from csf.pqc.dilithium import DilithiumSignature, create_dilithium
from csf.security.validation import validate_string, validate_bytes
from csf.security.constant_time import compare_digest


def verify_signature(
    message: str,
    fractal_signature_hash: str,
    semantic_key_text: str,
    math_private_key: bytes,
    math_public_key: bytes,
    pqc_signature: Optional[bytes] = None,
    pqc_scheme: str = "Dilithium3",
) -> bool:
    """
    Verify a message signature.

    Args:
        message: Message to verify
        fractal_signature_hash: Fractal signature hash
        semantic_key_text: Semantic key
        math_private_key: Private mathematical key
        math_public_key: Public mathematical key
        pqc_signature: Optional PQC signature
        pqc_scheme: PQC signature scheme

    Returns:
        True if signature is valid
    """
    validate_string(message, "message")
    validate_string(fractal_signature_hash, "fractal_signature_hash")
    validate_string(semantic_key_text, "semantic_key_text")
    validate_bytes(math_private_key, "math_private_key")
    validate_bytes(math_public_key, "math_public_key")

    # Initialize components
    key_manager = KeyManager()
    semantic_vectorizer = SemanticVectorizer()
    fractal_signature = FractalSignature()

    # Derive shared secret (must match signature.py method)
    # CRITICAL: Use same method as generate_signature() for consistency
    # In signature.py, we use math_private_key[:128] as shared_secret
    shared_secret = math_private_key[:128]
    shared_secret_arr = np.frombuffer(shared_secret, dtype=np.float64)

    # Transform semantic key
    semantic_vector = semantic_vectorizer.text_to_vector(semantic_key_text)

    # Verify fractal signature
    # CRITICAL FIX (v1.0.16): Pass math_private_key to ensure correct hash recomputation
    fractal_valid = fractal_signature.verify_signature(
        message, fractal_signature_hash, shared_secret_arr, semantic_vector, math_private_key=math_private_key
    )

    if not fractal_valid:
        return False

    # Verify PQC signature if provided
    if pqc_signature is not None:
        try:
            dilithium = create_dilithium(pqc_scheme)
            pqc_valid = dilithium.verify(message.encode(), pqc_signature, math_public_key)
            return pqc_valid
        except Exception:
            # If PQC verification fails, return False (don't trust broken PQC)
            return False

    return True
