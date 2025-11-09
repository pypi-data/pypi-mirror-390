"""
Base interfaces for Post-Quantum Cryptography implementations.

Defines abstract base classes for KEM and signature schemes.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
import numpy as np


class KEMScheme(ABC):
    """
    Abstract base class for Key Encapsulation Mechanism (KEM) schemes.
    """

    @abstractmethod
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        Generate a public/private key pair.

        Returns:
            Tuple of (public_key, private_key) as bytes
        """
        pass

    @abstractmethod
    def encapsulate(self, public_key: bytes) -> Tuple[bytes, bytes]:
        """
        Generate a shared secret and encapsulate it.

        Args:
            public_key: Public key

        Returns:
            Tuple of (ciphertext, shared_secret)
        """
        pass

    @abstractmethod
    def decapsulate(self, ciphertext: bytes, private_key: bytes) -> bytes:
        """
        Decapsulate shared secret from ciphertext.

        Args:
            ciphertext: Encapsulated ciphertext
            private_key: Private key

        Returns:
            Shared secret
        """
        pass

    @property
    @abstractmethod
    def public_key_size(self) -> int:
        """Size of public key in bytes."""
        pass

    @property
    @abstractmethod
    def private_key_size(self) -> int:
        """Size of private key in bytes."""
        pass

    @property
    @abstractmethod
    def shared_secret_size(self) -> int:
        """Size of shared secret in bytes."""
        pass

    @property
    @abstractmethod
    def ciphertext_size(self) -> int:
        """Size of ciphertext in bytes."""
        pass


class SignatureScheme(ABC):
    """
    Abstract base class for digital signature schemes.
    """

    @abstractmethod
    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """
        Generate a signing/verification key pair.

        Returns:
            Tuple of (public_key, private_key) as bytes
        """
        pass

    @abstractmethod
    def sign(self, message: bytes, private_key: bytes) -> bytes:
        """
        Sign a message.

        Args:
            message: Message to sign
            private_key: Signing key

        Returns:
            Signature as bytes
        """
        pass

    @abstractmethod
    def verify(self, message: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify a signature.

        Args:
            message: Original message
            signature: Signature to verify
            public_key: Verification key

        Returns:
            True if signature is valid, False otherwise
        """
        pass

    @property
    @abstractmethod
    def public_key_size(self) -> int:
        """Size of public key in bytes."""
        pass

    @property
    @abstractmethod
    def private_key_size(self) -> int:
        """Size of private key in bytes."""
        pass

    @property
    @abstractmethod
    def signature_size(self) -> int:
        """Size of signature in bytes."""
        pass


class PQCScheme(ABC):
    """
    Base class for Post-Quantum Cryptography schemes.
    """

    @property
    @abstractmethod
    def security_level(self) -> int:
        """
        Security level in bits.

        Common values: 128, 192, 256
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the scheme."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version of the scheme."""
        pass
