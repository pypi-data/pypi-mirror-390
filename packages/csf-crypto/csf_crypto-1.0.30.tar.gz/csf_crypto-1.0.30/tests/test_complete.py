#!/usr/bin/env python3
"""
Complete CSF System Tests - Full verification before presentation.
"""

import sys
import os
import numpy as np

# Helper function for safe Unicode printing on Windows
def safe_print(text, unicode_text=None):
    """Print text with Unicode fallback for Windows compatibility."""
    if unicode_text is None:
        unicode_text = text
    try:
        print(unicode_text)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        print(text)

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    if sys.stdout.encoding and "utf" not in sys.stdout.encoding.lower():
        os.environ["PYTHONIOENCODING"] = "utf-8"

print("=" * 80)
print("CSF - COMPLETE SYSTEM TESTS")
print("Inventor: Jeremy Noverraz (1988 - 2025) based on an idea by Ivàn Àvalos AND JCZD (engrenage.ch)")
print("=" * 80)
print()

tests_passed = 0
tests_failed = 0

def test(name, func):
    """Execute a test."""
    global tests_passed, tests_failed
    try:
        result = func()
        if result:
            safe_print(f"[PASS] {name}", f"\u2713 {name}")
            tests_passed += 1
            return True
        else:
            safe_print(f"[FAIL] {name}", f"\u2717 {name}")
            tests_failed += 1
            return False
    except Exception as e:
        safe_print(f"[FAIL] {name}: {e}", f"\u2717 {name}: {e}")
        tests_failed += 1
        import traceback
        traceback.print_exc()
        return False

# Test 1: Imports
# Note: This file is designed to run standalone, not with pytest
# Pytest will collect these but they should be excluded
def _test_imports():
    from csf import FractalCryptoSystem
    from csf.core.keys import KeyManager
    from csf.fractal.encoder import FractalEncoder
    from csf.fractal.decoder import FractalDecoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.security.constant_time import compare_digest
    return True

test("Module imports", _test_imports)

print()

# Test 2: Key generation
def _test_keygen():
    from csf.core.keys import KeyManager
    key_manager = KeyManager("Kyber768")
    public_key, private_key = key_manager.generate_key_pair()
    return len(public_key) > 0 and len(private_key) > 0

test("Mathematical key generation", _test_keygen)

# Test 3: Semantic transformation
def _test_semantic():
    from csf.semantic.vectorizer import SemanticVectorizer
    semantic = SemanticVectorizer(vector_dim=128)
    vec = semantic.text_to_vector("TestKey123")
    norm = np.linalg.norm(vec)
    # Vector should be normalized (norm ~= 1.0) or at least non-zero
    return len(vec) == 128 and norm > 0.5

test("Semantic key transformation", _test_semantic)

print()

# Test 4: Fractal encoding/decoding - Short messages
messages_short = [
    "A",
    "AB",
    "ABC",
    "Hello",
    "World",
]

def _test_encode_decode_short(msg):
    from csf.fractal.encoder import FractalEncoder
    from csf.fractal.decoder import FractalDecoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.core.keys import KeyManager
    
    encoder = FractalEncoder()
    decoder = FractalDecoder()
    semantic = SemanticVectorizer(vector_dim=128)
    key_manager = KeyManager()
    
    # Generate keys
    pk, sk = key_manager.generate_key_pair()
    
    # Derive shared secret
    shared_secret = key_manager.derive_shared_secret(pk, sk)
    shared_arr = np.frombuffer(shared_secret[:128*8], dtype=np.float64)[:128]
    
    # Semantic key
    semantic_key = semantic.text_to_vector("TestKey")
    
    # Encode
    params = encoder.encode_message(msg, shared_arr, semantic_key)
    
    # Decode
    decoded = decoder.decode_message(params, shared_arr, semantic_key)
    
    return decoded == msg

for msg in messages_short:
    test(f"Encode/Decode: '{msg}'", lambda m=msg: _test_encode_decode_short(m))

print()

# Test 5: Encoding/Decoding - Long messages
messages_long = [
    "Message de test pour CSF - Post-Quantum Security!",
    "The quick brown fox jumps over the lazy dog.",
    "1234567890 !@#$%^&*()",
    "Àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ",
    "Это тестовое сообщение для проверки UTF-8",
]

def _test_encode_decode_long(msg):
    from csf.fractal.encoder import FractalEncoder
    from csf.fractal.decoder import FractalDecoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.core.keys import KeyManager
    
    encoder = FractalEncoder()
    decoder = FractalDecoder()
    semantic = SemanticVectorizer(vector_dim=128)
    key_manager = KeyManager()
    
    pk, sk = key_manager.generate_key_pair()
    shared_secret = key_manager.derive_shared_secret(pk, sk)
    shared_arr = np.frombuffer(shared_secret[:128*8], dtype=np.float64)[:128]
    semantic_key = semantic.text_to_vector("TestKey")
    
    params = encoder.encode_message(msg, shared_arr, semantic_key)
    decoded = decoder.decode_message(params, shared_arr, semantic_key)
    
    return decoded == msg

for msg in messages_long:
    test(f"Encode/Decode long: '{msg[:30]}...'", lambda m=msg: _test_encode_decode_long(m))

print()

# Test 6: Complete system - Encryption/Decryption
def _test_full_system():
    from csf import FractalCryptoSystem
    from csf.core.keys import KeyManager
    
    crypto = FractalCryptoSystem()
    key_manager = KeyManager()
    
    message = "Complete test message for CSF - Post-Quantum Security!"
    semantic_key = "MySecretKey123"
    
    pk, sk = key_manager.generate_key_pair()
    encrypted = crypto.encrypt(message, semantic_key, pk, sk)
    decrypted = crypto.decrypt(encrypted, semantic_key, sk)
    
    return decrypted == message

test("Complete system - Encryption/Decryption", _test_full_system)

print()

# Test 7: Fractal signatures
def _test_signature():
    from csf import FractalCryptoSystem
    from csf.core.keys import KeyManager
    
    crypto = FractalCryptoSystem()
    key_manager = KeyManager()
    
    message = "Message to sign"
    semantic_key = "Key123"
    
    pk, sk = key_manager.generate_key_pair()
    fractal_hash, pqc_sig = crypto.sign(message, semantic_key, sk, use_pqc=False)
    
    return len(fractal_hash) == 64  # SHA256 hex digest

test("Fractal signature generation", _test_signature)

# Test 8: Signature verification
def _test_verify():
    from csf import FractalCryptoSystem
    from csf.core.keys import KeyManager
    
    crypto = FractalCryptoSystem()
    key_manager = KeyManager()
    
    message = "Message to sign"
    semantic_key = "Key123"
    
    pk, sk = key_manager.generate_key_pair()
    fractal_hash, _ = crypto.sign(message, semantic_key, sk, use_pqc=False)
    
    is_valid = crypto.verify(message, fractal_hash, semantic_key, sk, pk)
    return is_valid

test("Signature verification", _test_verify)

print()

# Test 9: Different keys = different messages
def _test_security():
    from csf.fractal.encoder import FractalEncoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.core.keys import KeyManager
    
    encoder = FractalEncoder()
    semantic = SemanticVectorizer(vector_dim=128)
    key_manager = KeyManager()
    
    message = "Test message"
    pk1, sk1 = key_manager.generate_key_pair()
    pk2, sk2 = key_manager.generate_key_pair()
    
    shared1 = key_manager.derive_shared_secret(pk1, sk1)
    shared2 = key_manager.derive_shared_secret(pk2, sk2)
    
    shared_arr1 = np.frombuffer(shared1[:128*8], dtype=np.float64)[:128]
    shared_arr2 = np.frombuffer(shared2[:128*8], dtype=np.float64)[:128]
    
    semantic_key = semantic.text_to_vector("Key")
    
    params1 = encoder.encode_message(message, shared_arr1, semantic_key)
    params2 = encoder.encode_message(message, shared_arr2, semantic_key)
    
    # Parameters must be different
    return params1 != params2

test("Security: different keys produce different parameters", _test_security)

# Test 10: Same keys = same parameters (determinism)
def _test_determinism():
    from csf.fractal.encoder import FractalEncoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.core.keys import KeyManager
    
    encoder = FractalEncoder()
    semantic = SemanticVectorizer(vector_dim=128)
    key_manager = KeyManager()
    
    message = "Test"
    pk, sk = key_manager.generate_key_pair()
    shared = key_manager.derive_shared_secret(pk, sk)
    shared_arr = np.frombuffer(shared[:128*8], dtype=np.float64)[:128]
    semantic_key = semantic.text_to_vector("Key")
    
    params1 = encoder.encode_message(message, shared_arr, semantic_key)
    params2 = encoder.encode_message(message, shared_arr, semantic_key)
    
    # Same parameters (within epsilon for floats)
    return all(abs(params1[i]['c'][0] - params2[i]['c'][0]) < 1e-10 for i in range(len(params1)))

test("Determinism: same keys produce same parameters", _test_determinism)

print()

# Test 11: Empty messages and edge cases
def _test_empty():
    from csf.fractal.encoder import FractalEncoder
    from csf.fractal.decoder import FractalDecoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.core.keys import KeyManager
    
    encoder = FractalEncoder()
    decoder = FractalDecoder()
    semantic = SemanticVectorizer(vector_dim=128)
    key_manager = KeyManager()
    
    pk, sk = key_manager.generate_key_pair()
    shared = key_manager.derive_shared_secret(pk, sk)
    shared_arr = np.frombuffer(shared[:128*8], dtype=np.float64)[:128]
    semantic_key = semantic.text_to_vector("Key")
    
    # Empty message
    try:
        params = encoder.encode_message("", shared_arr, semantic_key)
        decoded = decoder.decode_message(params, shared_arr, semantic_key)
        return decoded == ""
    except Exception:
        return False

test("Empty messages and edge cases", _test_empty)

print()

# Test 12: Special characters and UTF-8
def _test_special():
    from csf.fractal.encoder import FractalEncoder
    from csf.fractal.decoder import FractalDecoder
    from csf.semantic.vectorizer import SemanticVectorizer
    from csf.core.keys import KeyManager
    
    encoder = FractalEncoder()
    decoder = FractalDecoder()
    semantic = SemanticVectorizer(vector_dim=128)
    key_manager = KeyManager()
    
    pk, sk = key_manager.generate_key_pair()
    shared = key_manager.derive_shared_secret(pk, sk)
    shared_arr = np.frombuffer(shared[:128*8], dtype=np.float64)[:128]
    semantic_key = semantic.text_to_vector("Key")
    
    special = "émojis 🚀🔐💻\n\t\r\x00\xff"
    
    params = encoder.encode_message(special, shared_arr, semantic_key)
    decoded = decoder.decode_message(params, shared_arr, semantic_key)
    
    return decoded == special

test("Special characters and UTF-8", _test_special)

print()

# Final summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Tests passed: {tests_passed}")
print(f"Tests failed: {tests_failed}")
print(f"Total: {tests_passed + tests_failed}")
print()

if tests_failed == 0:
    print("=" * 80)
    safe_print("*** ALL TESTS PASSED ***", "\u2713\u2713\u2713 ALL TESTS PASSED \u2713\u2713\u2713")
    print("=" * 80)
    print()
    print("CSF System is COMPLETE and READY for presentation!")
    print("Inventor: Jeremy Noverraz (1988 - 2025) based on an idea by Ivàn Àvalos AND JCZD (engrenage.ch)")
    print()
    # Don't exit if running under pytest
    if not hasattr(sys.modules.get('_pytest', None), '__version__'):
        sys.exit(0)
else:
    print("=" * 80)
    safe_print(f"[FAIL] {tests_failed} TEST(S) FAILED", f"\u2717 {tests_failed} TEST(S) FAILED")
    print("=" * 80)
    print()
    # Don't exit if running under pytest
    if not hasattr(sys.modules.get('_pytest', None), '__version__'):
        sys.exit(1)
