"""
CSF - Cryptographic Security Framework
Military-grade post-quantum cryptographic system with fractal encoding.
"""

__version__ = "1.0.29"

from typing import Union
from csf.crypto.encrypt import encrypt
from csf.crypto.decrypt import decrypt
from csf.crypto.signature import generate_signature
from csf.crypto.encrypt_chunked import encrypt_chunked
from csf.crypto.verification import verify_signature


class FractalCryptoSystem:
    """
    Complete fractal-based cryptographic system.

    Integrates all modules: PQC, fractal encoding, semantic keys, signatures.
    """

    def __init__(self, pqc_kem_scheme: str = "Kyber768", pqc_signature_scheme: str = "Dilithium3"):
        """
        Initialize the cryptographic system.

        Args:
            pqc_kem_scheme: PQC KEM scheme ("Kyber512", "Kyber768", "Kyber1024")
            pqc_signature_scheme: PQC signature scheme ("Dilithium2", "Dilithium3", "Dilithium5")
        """
        self.pqc_kem_scheme = pqc_kem_scheme
        self.pqc_signature_scheme = pqc_signature_scheme

    def encrypt(
        self,
        message,
        semantic_key_text: str,
        math_public_key: bytes = None,
        math_private_key: bytes = None,
        return_dict: bool = False,
        compress: bool = True,
        generate_signature: bool = False,
    ) -> Union[bytes, dict]:
        """
        Encrypt a message using fractal encoding.

        Args:
            message: Plaintext message (str or bytes)
            semantic_key_text: Semantic key as text
            math_public_key: Optional pre-generated public key
            math_private_key: Optional pre-generated private key
            return_dict: If True, return dict format (legacy). If False, return bytes (optimized binary format)
            compress: Whether to compress the output (only applies if return_dict=False)
            generate_signature: If True, generate fractal signature (default False for performance)

        Returns:
            Binary serialized encrypted data (bytes) by default, or dictionary if return_dict=True
        """
        return encrypt(
            message, semantic_key_text, math_public_key, math_private_key, self.pqc_kem_scheme,
            return_dict=return_dict, compress=compress, generate_signature=generate_signature
        )

    def decrypt(self, encrypted_data: Union[bytes, dict], semantic_key_text: str, math_private_key: bytes) -> str:
        """
        Decrypt a message from fractal parameters.

        Args:
            encrypted_data: Binary serialized data (bytes) or dictionary with encrypted data (legacy format)
            semantic_key_text: Semantic key as text
            math_private_key: Private mathematical key

        Returns:
            Decrypted plaintext message
        """
        return decrypt(encrypted_data, semantic_key_text, math_private_key, self.pqc_kem_scheme)

    def sign(
        self, message: str, semantic_key_text: str, math_private_key: bytes, use_pqc: bool = True
    ) -> tuple:
        """
        Generate signature for a message.

        Args:
            message: Message to sign
            semantic_key_text: Semantic key
            math_private_key: Private mathematical key
            use_pqc: Whether to use PQC signature scheme

        Returns:
            Tuple of (fractal_signature_hash, pqc_signature_bytes)
        """
        return generate_signature(
            message, semantic_key_text, math_private_key, use_pqc, self.pqc_signature_scheme
        )

    def verify(
        self,
        message: str,
        fractal_signature_hash: str,
        semantic_key_text: str,
        math_private_key: bytes,
        math_public_key: bytes,
        pqc_signature: bytes = None,
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

        Returns:
            True if signature is valid
        """
        return verify_signature(
            message,
            fractal_signature_hash,
            semantic_key_text,
            math_private_key,
            math_public_key,
            pqc_signature,
            self.pqc_signature_scheme,
        )


__all__ = [
    "FractalCryptoSystem",
    "encrypt",
    "decrypt",
    "generate_signature",
    "verify_signature",
]
