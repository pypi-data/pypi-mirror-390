"""
Decryption operations.

Provides high-level decryption API.
"""

from typing import Dict, Union
import numpy as np
from csf.core.keys import KeyManager
from csf.fractal.decoder import FractalDecoder
from csf.fractal.visualizer import FractalSignature
from csf.semantic.vectorizer import SemanticVectorizer
from csf.security.validation import validate_string, validate_bytes
from csf.security.constant_time import compare_digest
from csf.utils.exceptions import ValidationError
from csf.core.fractal_hash import fractal_hash
from csf.utils.serialization import deserialize_encrypted_data, is_binary_format


def decrypt(
    encrypted_data: Union[bytes, Dict],
    semantic_key_text: str,
    math_private_key: bytes,
    pqc_scheme: str = "Kyber768",
) -> str:
    """
    Decrypt a message from fractal parameters.

    Args:
        encrypted_data: Binary serialized data (bytes) or dictionary with encrypted data (legacy format)
        semantic_key_text: Semantic key as text
        math_private_key: Private mathematical key
        pqc_scheme: PQC scheme used

    Returns:
        Decrypted plaintext message
    """
    validate_string(semantic_key_text, "semantic_key_text")
    validate_bytes(math_private_key, "math_private_key")

    # Deserialize if binary format
    if is_binary_format(encrypted_data):
        encrypted_data = deserialize_encrypted_data(encrypted_data)
    
    # PHASE 4: Check if adaptive fractal encryption (post-quantum)
    if encrypted_data.get("encrypted_data", {}).get("adaptive", False):
        from csf.crypto.adaptive_fractal import decrypt_adaptive
        return decrypt_adaptive(encrypted_data, semantic_key_text, math_private_key, pqc_scheme)

    # Extract data
    fractal_params = encrypted_data["encrypted_data"]["fractal_params"]
    math_public_key = bytes(encrypted_data["encrypted_data"]["public_key"])
    
    # Extract stored shared secret hash for key validation
    stored_secret_hash = bytes(encrypted_data["encrypted_data"].get("shared_secret_hash", []))

    # Initialize components
    key_manager = KeyManager(pqc_scheme)
    fractal_decoder = FractalDecoder()
    semantic_vectorizer = SemanticVectorizer()

    # Derive shared secret
    shared_secret = key_manager.derive_shared_secret(math_public_key, math_private_key)
    
    # Validate that the private key matches the public key by comparing shared secret hash
    # Using fractal hash for post-quantum resistance
    # OPTIMIZATION: Use 16 bytes (matches encryption)
    if stored_secret_hash:
        computed_secret_hash = fractal_hash(shared_secret, output_length=16)
        if not compare_digest(stored_secret_hash, computed_secret_hash):
            raise ValidationError(
                "Key mismatch: The provided private key does not correspond to the public key used for encryption. Decryption failed."
            )
    
    shared_secret_arr = np.frombuffer(shared_secret[:128], dtype=np.float64)

    # Transform semantic key
    semantic_vector = semantic_vectorizer.text_to_vector(semantic_key_text)

    # Convert fractal params back to internal format
    internal_params = [
        {
            "c": (p["c"][0], p["c"][1]),
            "z0": (p["z0"][0], p["z0"][1]),
            "iteration": p["iteration"],
            "byte_value": p["byte_value"],
        }
        for p in fractal_params
    ]

    # Decode message
    message = fractal_decoder.decode_message(internal_params, shared_secret_arr, semantic_vector)

    # Validate semantic key by verifying fractal signature if present
    stored_signature_hash = encrypted_data["encrypted_data"].get("signature_hash")
    if stored_signature_hash:
        signature_gen = FractalSignature()
        # CRITICAL: Pass math_private_key to ensure correct hash recomputation
        is_valid = signature_gen.verify_signature(
            message, stored_signature_hash, shared_secret_arr, semantic_vector, math_private_key=math_private_key
        )
        if not is_valid:
            raise ValidationError(
                "Semantic key mismatch: The provided semantic key does not match the one used for encryption. Decryption may have produced incorrect results."
            )

    return message
