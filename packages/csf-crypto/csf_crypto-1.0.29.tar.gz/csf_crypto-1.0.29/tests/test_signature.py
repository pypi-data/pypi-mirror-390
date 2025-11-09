"""
Comprehensive test suite for signature functionality (v1.0.16).

Tests critical security guarantees:
1. Message uniqueness: Different messages produce different hashes
2. Key uniqueness: Different keys produce different hashes
3. Verification rejects wrong message
4. Verification rejects wrong key
5. Verification rejects wrong hash
"""

import unittest
import csf
from csf.core.keys import KeyManager


class TestSignatureSecurity(unittest.TestCase):
    """Test signature security guarantees."""

    def setUp(self):
        """Set up test fixtures."""
        # Clear cache to ensure clean state for each test
        from csf.core.key_cache import get_global_cache
        cache = get_global_cache()
        cache.clear()
        # Also clear semantic vector and shared secret caches
        cache._semantic_vector_cache.clear()
        cache._shared_secret_cache.clear()
        
        self.crypto = csf.FractalCryptoSystem()
        self.key_manager = KeyManager()
        self.semantic_key = "test_key"
        self.math_public_key, self.math_private_key = self.key_manager.generate_key_pair()

    def test_signature_message_uniqueness(self):
        """Verify that different messages produce different hashes."""
        msg1 = "Message 1"
        msg2 = "Message 2"

        hash1, _ = self.crypto.sign(msg1, self.semantic_key, self.math_private_key, use_pqc=False)
        hash2, _ = self.crypto.sign(msg2, self.semantic_key, self.math_private_key, use_pqc=False)

        self.assertNotEqual(hash1, hash2, "Different messages must produce different hashes")

    def test_signature_key_uniqueness(self):
        """Verify that different keys produce different hashes."""
        msg = "Test message"
        math_public_key2, math_private_key2 = self.key_manager.generate_key_pair()

        hash1, _ = self.crypto.sign(msg, "key1", self.math_private_key, use_pqc=False)
        hash2, _ = self.crypto.sign(msg, "key2", math_private_key2, use_pqc=False)

        self.assertNotEqual(hash1, hash2, "Different keys must produce different hashes")

    def test_signature_semantic_key_uniqueness(self):
        """Verify that different semantic keys produce different hashes."""
        msg = "Test message"

        hash1, _ = self.crypto.sign(msg, "key1", self.math_private_key, use_pqc=False)
        hash2, _ = self.crypto.sign(msg, "key2", self.math_private_key, use_pqc=False)

        self.assertNotEqual(hash1, hash2, "Different semantic keys must produce different hashes")

    def test_signature_math_key_uniqueness(self):
        """Verify that different math keys produce different hashes."""
        msg = "Test message"
        math_public_key2, math_private_key2 = self.key_manager.generate_key_pair()

        hash1, _ = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        hash2, _ = self.crypto.sign(msg, self.semantic_key, math_private_key2, use_pqc=False)

        self.assertNotEqual(hash1, hash2, "Different math keys must produce different hashes")

    def test_verify_rejects_wrong_message(self):
        """Verify that verify() returns False for wrong message."""
        msg1 = "Original message"
        msg2 = "Tampered message"

        signature = self.crypto.sign(msg1, self.semantic_key, self.math_private_key, use_pqc=False)
        fractal_hash = signature[0]

        # Verify with correct message
        self.assertTrue(
            self.crypto.verify(msg1, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Correct message must verify as True"
        )

        # Verify with wrong message
        self.assertFalse(
            self.crypto.verify(msg2, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Wrong message must verify as False"
        )

    def test_verify_rejects_wrong_key(self):
        """Verify that verify() returns False for wrong key."""
        msg = "Test message"
        math_public_key2, math_private_key2 = self.key_manager.generate_key_pair()

        signature = self.crypto.sign(msg, "key1", self.math_private_key, use_pqc=False)
        fractal_hash = signature[0]

        # Verify with correct key
        self.assertTrue(
            self.crypto.verify(msg, fractal_hash, "key1", self.math_private_key, self.math_public_key),
            "Correct key must verify as True"
        )

        # Verify with wrong semantic key
        self.assertFalse(
            self.crypto.verify(msg, fractal_hash, "key2", self.math_private_key, self.math_public_key),
            "Wrong semantic key must verify as False"
        )

        # Verify with wrong math key
        self.assertFalse(
            self.crypto.verify(msg, fractal_hash, "key1", math_private_key2, math_public_key2),
            "Wrong math key must verify as False"
        )

    def test_verify_rejects_wrong_hash(self):
        """Verify that verify() returns False for wrong hash."""
        msg = "Test message"

        signature = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        correct_hash = signature[0]
        wrong_hash = "0000000000000000000000000000000000000000000000000000000000000000"

        # Verify with correct hash
        self.assertTrue(
            self.crypto.verify(msg, correct_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Correct hash must verify as True"
        )

        # Verify with wrong hash
        self.assertFalse(
            self.crypto.verify(msg, wrong_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Wrong hash must verify as False"
        )

    def test_signature_determinism(self):
        """Verify that same inputs always produce same hash."""
        msg = "Test message"

        hash1, _ = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        hash2, _ = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)

        self.assertEqual(hash1, hash2, "Same inputs must produce same hash")

    def test_verify_accepts_correct_signature(self):
        """Verify that verify() returns True for correct signature."""
        msg = "Test message"

        signature = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        fractal_hash = signature[0]

        self.assertTrue(
            self.crypto.verify(msg, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Correct signature must verify as True"
        )

    def test_verify_empty_message(self):
        """Verify that empty messages work correctly."""
        msg = ""

        signature = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        fractal_hash = signature[0]

        self.assertTrue(
            self.crypto.verify(msg, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Empty message must verify correctly"
        )

        # Wrong message must fail
        self.assertFalse(
            self.crypto.verify("wrong", fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Wrong message must fail even with empty original"
        )

    def test_verify_long_message(self):
        """Verify that long messages work correctly."""
        msg = "A" * 10000  # 10KB message

        signature = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        fractal_hash = signature[0]

        self.assertTrue(
            self.crypto.verify(msg, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Long message must verify correctly"
        )

        # Wrong message must fail
        wrong_msg = "B" * 10000
        self.assertFalse(
            self.crypto.verify(wrong_msg, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Wrong long message must fail"
        )

    def test_verify_special_characters(self):
        """Verify that messages with special characters work correctly."""
        msg = "Hello, World! こんにちは 🚀\n\t\r"

        signature = self.crypto.sign(msg, self.semantic_key, self.math_private_key, use_pqc=False)
        fractal_hash = signature[0]

        self.assertTrue(
            self.crypto.verify(msg, fractal_hash, self.semantic_key, self.math_private_key, self.math_public_key),
            "Special characters must verify correctly"
        )


if __name__ == "__main__":
    unittest.main()

