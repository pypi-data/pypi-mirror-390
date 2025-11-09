"""
Test bytes support for messages.
This is a regression test to ensure bytes input is always supported.
"""

import unittest
from csf import FractalCryptoSystem
from csf.core.keys import KeyManager


class TestBytesSupport(unittest.TestCase):
    """Test that bytes input is supported for encryption."""

    def setUp(self):
        """Set up test fixtures."""
        self.crypto = FractalCryptoSystem()
        self.key_manager = KeyManager()
        self.public_key, self.private_key = self.key_manager.generate_key_pair()

    def test_encrypt_bytes(self):
        """Test encryption with bytes input."""
        message_str = "secret message: hello Alice! Sponge Bob is not here yet"
        message_bytes = bytes(message_str, "utf-8")

        # Should not raise ValidationError
        # Default: returns binary format (bytes)
        encrypted = self.crypto.encrypt(message_bytes, "semantic_key", self.public_key, self.private_key)
        
        # Should be bytes format
        self.assertIsInstance(encrypted, bytes)

        # Should decrypt correctly
        decrypted = self.crypto.decrypt(encrypted, "semantic_key", self.private_key)
        self.assertEqual(decrypted, message_str)

    def test_encrypt_bytes_exact_user_case(self):
        """Test the exact case reported by the user."""
        message = "secret message: hello Alice! Sponge Bob is not here yet"
        message_bytes = bytes(message, "utf-8")

        # This should work without ValidationError
        # Default: returns binary format (bytes)
        encrypted = self.crypto.encrypt(message_bytes, "semantic_key", self.public_key, self.private_key)
        
        # Should be bytes format
        self.assertIsInstance(encrypted, bytes)

        decrypted = self.crypto.decrypt(encrypted, "semantic_key", self.private_key)
        self.assertEqual(decrypted, message)

    def test_encrypt_str_still_works(self):
        """Ensure str input still works (backward compatibility)."""
        message = "test message"
        # Default: returns binary format (bytes)
        encrypted = self.crypto.encrypt(message, "semantic_key", self.public_key, self.private_key)
        self.assertIsInstance(encrypted, bytes)
        decrypted = self.crypto.decrypt(encrypted, "semantic_key", self.private_key)
        self.assertEqual(decrypted, message)
    
    def test_legacy_dict_format(self):
        """Test backward compatibility with dict format."""
        message = "test message"
        # Request dict format (legacy)
        encrypted_dict = self.crypto.encrypt(
            message, "semantic_key", self.public_key, self.private_key, return_dict=True
        )
        self.assertIsInstance(encrypted_dict, dict)
        # Should decrypt correctly
        decrypted = self.crypto.decrypt(encrypted_dict, "semantic_key", self.private_key)
        self.assertEqual(decrypted, message)
    
    def test_binary_format_size(self):
        """Test that binary format is significantly smaller than dict format."""
        message = "test message" * 100  # Larger message to see size difference
        
        # Binary format (default)
        encrypted_binary = self.crypto.encrypt(
            message, "semantic_key", self.public_key, self.private_key, compress=True
        )
        
        # Dict format
        encrypted_dict = self.crypto.encrypt(
            message, "semantic_key", self.public_key, self.private_key, return_dict=True
        )
        
        # Calculate approximate dict size (JSON-like)
        import json
        dict_size = len(json.dumps(encrypted_dict).encode('utf-8'))
        binary_size = len(encrypted_binary)
        
        # Binary should be significantly smaller
        self.assertLess(binary_size, dict_size)
        # Should be at least 3x smaller (conservative estimate)
        self.assertLess(binary_size, dict_size / 2)


if __name__ == "__main__":
    unittest.main()

