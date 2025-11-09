#!/usr/bin/env python3
"""
Performance benchmarks for CSF-Crypto.

Professional benchmarking suite for measuring and tracking performance improvements.
"""

import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csf
from csf.core.keys import KeyManager


def benchmark_encryption_decryption(data_sizes=None):
    """
    Benchmark encryption and decryption for various data sizes.
    
    Args:
        data_sizes: List of data sizes in bytes (default: [1KB, 10KB, 100KB, 1MB])
    
    Returns:
        Dictionary with benchmark results
    """
    if data_sizes is None:
        data_sizes = [
            (1024, "1 KB"),
            (10 * 1024, "10 KB"),
            (100 * 1024, "100 KB"),
            (1024 * 1024, "1 MB"),
        ]
    
    print("=" * 80)
    print("CSF-Crypto Performance Benchmark")
    print("=" * 80)
    print()
    
    fcs = csf.FractalCryptoSystem()
    key_manager = KeyManager()
    math_public_key, math_private_key = key_manager.generate_key_pair()
    semantic_key = "benchmark_semantic_key"
    
    results = []
    
    for size_bytes, label in data_sizes:
        print(f"\n{'='*80}")
        print(f"Benchmark: {label} ({size_bytes:,} bytes)")
        print('='*80)
        
        test_data = b"X" * size_bytes
        
        # Encryption benchmark
        start = time.time()
        try:
            encrypted = fcs.encrypt(
                test_data, 
                semantic_key, 
                math_public_key, 
                math_private_key,
                return_dict=False,
                compress=True
            )
            encrypt_time = time.time() - start
            encrypt_throughput = size_bytes / encrypt_time if encrypt_time > 0 else 0
        except Exception as e:
            print(f"❌ Encryption FAILED: {e}")
            continue
        
        # Decryption benchmark
        start = time.time()
        try:
            decrypted = fcs.decrypt(encrypted, semantic_key, math_private_key)
            decrypt_time = time.time() - start
            decrypt_throughput = size_bytes / decrypt_time if decrypt_time > 0 else 0
        except Exception as e:
            print(f"❌ Decryption FAILED: {e}")
            continue
        
        # Verify correctness
        if decrypted != test_data.decode('utf-8'):
            print(f"❌ Verification FAILED: Decrypted data doesn't match")
            continue
        
        # Calculate metrics
        total_time = encrypt_time + decrypt_time
        size_ratio = len(encrypted) / size_bytes
        
        print(f"\nResults:")
        print(f"  Encryption:")
        print(f"    Time: {encrypt_time:.3f}s")
        print(f"    Throughput: {encrypt_throughput/1024:.1f} KB/s")
        print(f"  Decryption:")
        print(f"    Time: {decrypt_time:.3f}s")
        print(f"    Throughput: {decrypt_throughput/1024:.1f} KB/s")
        print(f"  Total: {total_time:.3f}s")
        print(f"  Size ratio: {size_ratio:.2f}x ({size_bytes:,} → {len(encrypted):,} bytes)")
        
        results.append({
            'size': size_bytes,
            'label': label,
            'encrypt_time': encrypt_time,
            'decrypt_time': decrypt_time,
            'total_time': total_time,
            'encrypt_throughput': encrypt_throughput,
            'decrypt_throughput': decrypt_throughput,
            'size_ratio': size_ratio,
        })
    
    # Summary table
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    print(f"{'Size':<12} {'Encrypt':<12} {'Decrypt':<12} {'Total':<12} {'Enc KB/s':<12} {'Dec KB/s':<12}")
    print('-'*80)
    for r in results:
        print(f"{r['label']:<12} {r['encrypt_time']:.3f}s{' '*6} {r['decrypt_time']:.3f}s{' '*6} "
              f"{r['total_time']:.3f}s{' '*6} {r['encrypt_throughput']/1024:.1f}{' '*10} "
              f"{r['decrypt_throughput']/1024:.1f}")
    
    return results


if __name__ == "__main__":
    results = benchmark_encryption_decryption()
    
    # Check performance targets
    print(f"\n{'='*80}")
    print("PERFORMANCE TARGETS")
    print('='*80)
    
    targets_met = True
    for r in results:
        if r['size'] >= 1024 * 1024:  # 1MB
            encrypt_ok = r['encrypt_time'] < 1.0
            decrypt_ok = r['decrypt_time'] < 0.5
            status = "✅" if (encrypt_ok and decrypt_ok) else "⚠️"
            print(f"{r['label']}: Encrypt < 1s: {encrypt_ok} ({r['encrypt_time']:.3f}s) {status}")
            print(f"{r['label']}: Decrypt < 0.5s: {decrypt_ok} ({r['decrypt_time']:.3f}s) {status}")
            if not (encrypt_ok and decrypt_ok):
                targets_met = False
    
    if targets_met:
        print("\n✅ All performance targets met!")
    else:
        print("\n⚠️  Some performance targets not met - further optimization needed")
    
    sys.exit(0 if targets_met else 1)

