#!/usr/bin/env python3
"""
Performance benchmarking tool.

Benchmarks CSF cryptographic operations.
"""

import time
import argparse
from csf import FractalCryptoSystem
from csf.core.keys import KeyManager


def benchmark_encrypt_decrypt(message_size: int = 1000, iterations: int = 10):
    """Benchmark encryption/decryption."""
    crypto = FractalCryptoSystem()
    key_manager = KeyManager()

    message = "A" * message_size
    semantic_key = "BenchmarkKey"

    # Generate keys
    public_key, private_key = key_manager.generate_key_pair()

    # Benchmark encryption
    encrypt_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        encrypted = crypto.encrypt(message, semantic_key, public_key, private_key)
        elapsed = time.perf_counter() - start
        encrypt_times.append(elapsed)

    # Benchmark decryption
    decrypt_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        decrypted = crypto.decrypt(encrypted, semantic_key, private_key)
        elapsed = time.perf_counter() - start
        decrypt_times.append(elapsed)

    avg_encrypt = sum(encrypt_times) / len(encrypt_times)
    avg_decrypt = sum(decrypt_times) / len(decrypt_times)

    print(f"Encryption: {avg_encrypt*1000:.2f}ms (avg over {iterations} iterations)")
    print(f"Decryption: {avg_decrypt*1000:.2f}ms (avg over {iterations} iterations)")
    print(f"Message size: {message_size} bytes")


def main():
    parser = argparse.ArgumentParser(description="Benchmark CSF operations")
    parser.add_argument("--message-size", type=int, default=1000, help="Message size in bytes")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")

    args = parser.parse_args()

    print("CSF Performance Benchmark")
    print("=" * 50)
    benchmark_encrypt_decrypt(args.message_size, args.iterations)


if __name__ == "__main__":
    main()
