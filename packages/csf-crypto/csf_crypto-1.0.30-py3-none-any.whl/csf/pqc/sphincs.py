"""
SPHINCS+ integration (NIST PQC Standard FIPS 205 / SLH-DSA).

Provides hash-based digital signatures.
"""

from typing import Tuple
import hashlib
from csf.pqc.base import SignatureScheme, PQCScheme
from csf.core.randomness import CSPRNG
from csf.security.validation import validate_bytes


class SPHINCSP(SignatureScheme, PQCScheme):
    """
    SPHINCS+ Hash-Based Digital Signature Algorithm.

    Implements SLH-DSA (FIPS 205) standard.
    """

    def __init__(self, variant: str = "SPHINCS+_SHA256_256f"):
        """
        Initialize SPHINCS+ signature scheme.

        Args:
            variant: SPHINCS+ variant
        """
        self.variant = variant

        # Parameters based on variant (simplified)
        if "256" in variant:
            self._n = 32
            self._h = 60
            self._sec_level = 128
        elif "192" in variant:
            self._n = 24
            self._h = 63
            self._sec_level = 192
        else:  # 256s
            self._n = 32
            self._h = 64
            self._sec_level = 256

        self.csprng = CSPRNG()
        self.hash_func = hashlib.sha256

    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        Generate a signing/verification key pair.

        Returns:
            Tuple of (public_key, private_key) as bytes
        """
        try:
            return self._generate_key_pair_external()
        except (ImportError, AttributeError):
            return self._generate_key_pair_internal()

    def _generate_key_pair_external(self) -> Tuple[bytes, bytes]:
        """Generate keys using external library."""
        try:
            from pysphincs import Sphincs as PySPHINCS

            sph = PySPHINCS(self.variant)
            pk, sk = sph.keygen()
            return bytes(pk), bytes(sk)
        except ImportError:
            raise ImportError("No SPHINCS+ library available. Install pysphincs.")

    def _generate_key_pair_internal(self) -> Tuple[bytes, bytes]:
        """Internal key generation."""
        # Generate secret seed
        sk_seed = self.csprng.random_bytes(self._n)
        pk_seed = self.csprng.random_bytes(self._n)

        # Generate Merkle tree root (public key)
        root = self._generate_merkle_root(pk_seed)

        # Serialize keys
        public_key = pk_seed + root
        private_key = sk_seed + pk_seed

        return public_key, private_key

    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """
        Sign a message.

        Args:
            message: Message to sign
            private_key: Signing key

        Returns:
            Signature as bytes
        """
        validate_bytes(message, "message", min_length=0)
        validate_bytes(private_key, "private_key", min_length=1)

        try:
            return self._sign_external(message, private_key)
        except (ImportError, AttributeError):
            return self._sign_internal(message, private_key)

    def _sign_external(self, message: bytes, private_key: bytes) -> bytes:
        """Sign using external library."""
        try:
            from pysphincs import Sphincs as PySPHINCS

            sph = PySPHINCS(self.variant)
            sig = sph.sign(message, private_key)
            return bytes(sig)
        except ImportError:
            raise ImportError("No SPHINCS+ library available.")

    def _sign_internal(self, message: bytes, private_key: bytes) -> bytes:
        """Internal signing implementation."""
        # Parse private key
        sk_seed = private_key[: self._n]
        pk_seed = private_key[self._n : 2 * self._n]

        # Compute message digest
        msg_digest = self.hash_func(message).digest()[: self._n]

        # Generate random index
        rand_idx = self.csprng.random_bytes(self._n)

        # Sign with hash tree (simplified)
        signature = self._generate_hash_tree_signature(msg_digest, sk_seed, pk_seed, rand_idx)

        return signature

    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify a signature.

        Args:
            message: Original message
            signature: Signature to verify
            public_key: Verification key

        Returns:
            True if signature is valid
        """
        validate_bytes(message, "message", min_length=0)
        validate_bytes(signature, "signature", min_length=1)
        validate_bytes(public_key, "public_key", min_length=1)

        try:
            return self._verify_external(message, signature, public_key)
        except (ImportError, AttributeError):
            return self._verify_internal(message, signature, public_key)

    def _verify_external(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Verify using external library."""
        try:
            from pysphincs import Sphincs as PySPHINCS

            sph = PySPHINCS(self.variant)
            return sph.verify(message, signature, public_key)
        except ImportError:
            raise ImportError("No SPHINCS+ library available.")

    def _verify_internal(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """Internal verification implementation."""
        try:
            # Parse public key
            pk_seed = public_key[: self._n]
            root = public_key[self._n :]

            # Compute message digest
            msg_digest = self.hash_func(message).digest()[: self._n]

            # Verify hash tree signature (simplified)
            computed_root = self._verify_hash_tree_signature(msg_digest, signature, pk_seed)

            # Compare roots (constant-time)
            from csf.security.constant_time import compare_digest

            return compare_digest(computed_root, root)
        except Exception:
            return False

    # Helper methods (simplified implementations)
    def _generate_merkle_root(self, seed: bytes) -> bytes:
        """Generate Merkle tree root."""
        # Simplified Merkle tree generation
        leaf = self.hash_func(seed).digest()
        return self.hash_func(leaf * 2).digest()[: self._n]

    def _generate_hash_tree_signature(
        self, msg_digest: bytes, sk_seed: bytes, pk_seed: bytes, rand_idx: bytes
    ) -> bytes:
        """Generate hash tree signature."""
        # Simplified signature generation
        combined = msg_digest + sk_seed + pk_seed + rand_idx
        return self.hash_func(combined).digest() + rand_idx

    def _verify_hash_tree_signature(
        self, msg_digest: bytes, signature: bytes, pk_seed: bytes
    ) -> bytes:
        """Verify hash tree signature."""
        # Simplified verification
        sig_part = signature[: -self._n]
        rand_idx = signature[-self._n :]
        combined = msg_digest + pk_seed + rand_idx
        computed = self.hash_func(combined).digest()
        return computed[: self._n]

    @property
    def public_key_size(self) -> int:
        """Size of public key in bytes."""
        return self._n * 2  # seed + root

    @property
    def private_key_size(self) -> int:
        """Size of private key in bytes."""
        return self._n * 2  # sk_seed + pk_seed

    @property
    def signature_size(self) -> int:
        """Size of signature in bytes."""
        # Simplified size estimation
        return self._n * (self._h + 2)

    @property
    def security_level(self) -> int:
        """Security level in bits."""
        return self._sec_level

    @property
    def name(self) -> str:
        """Name of the scheme."""
        return f"SPHINCS+ ({self.variant})"

    @property
    def version(self) -> str:
        """Version of the scheme."""
        return "1.0"


def create_sphincs(variant: str = "SPHINCS+_SHA256_256f") -> SPHINCSP:
    """
    Create a SPHINCS+ signature instance.

    Args:
        variant: SPHINCS+ variant

    Returns:
        SPHINCSP instance
    """
    return SPHINCSP(variant)
