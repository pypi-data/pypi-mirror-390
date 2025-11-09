#!/usr/bin/env python3
"""
Performance benchmark script for CSF-Crypto.

Measures encryption/decryption throughput and compares with target performance.
"""

import time
import sys
import numpy as np
import csf
from csf.pqc.kyber import create_kyber


def benchmark_csf(size_mb: float, iterations: int = 3, warmup: int = 1):
    """
    Benchmark CSF encryption/decryption.
    
    Args:
        size_mb: Size of test data in MB
        iterations: Number of iterations to average
        warmup: Number of warmup iterations
    
    Returns:
        Dictionary with performance metrics
    """
    size_bytes = int(size_mb * 1024 * 1024)
    
    # Generate test data
    test_data = "X" * size_bytes
    
    fcs = csf.FractalCryptoSystem()
    semantic_key = 'test_key_benchmark'
    kyber = create_kyber('Kyber768')
    math_public_key, math_private_key = kyber.generate_key_pair()
    
    encrypt_times = []
    decrypt_times = []
    
    # Warmup
    for _ in range(warmup):
        encrypted = fcs.encrypt(test_data, semantic_key, math_public_key, math_private_key)
        _ = fcs.decrypt(encrypted, semantic_key, math_private_key)
    
    # Actual benchmark
    for i in range(iterations):
        # Encryption
        start = time.perf_counter()
        encrypted = fcs.encrypt(test_data, semantic_key, math_public_key, math_private_key)
        encrypt_time = time.perf_counter() - start
        encrypt_times.append(encrypt_time)
        
        # Decryption
        start = time.perf_counter()
        decrypted = fcs.decrypt(encrypted, semantic_key, math_private_key)
        decrypt_time = time.perf_counter() - start
        decrypt_times.append(decrypt_time)
        
        # Verify correctness
        if decrypted != test_data:
            print(f"ERROR: Decryption failed on iteration {i+1}")
            return None
        
        print(f"  Iteration {i+1}/{iterations}: Encrypt={encrypt_time*1000:.2f}ms, Decrypt={decrypt_time*1000:.2f}ms")
    
    encrypt_avg = np.mean(encrypt_times)
    decrypt_avg = np.mean(decrypt_times)
    encrypt_std = np.std(encrypt_times)
    decrypt_std = np.std(decrypt_times)
    
    throughput_encrypt = size_mb / encrypt_avg
    throughput_decrypt = size_mb / decrypt_avg
    
    return {
        'size_mb': size_mb,
        'size_bytes': size_bytes,
        'encrypt_avg': encrypt_avg,
        'decrypt_avg': decrypt_avg,
        'encrypt_std': encrypt_std,
        'decrypt_std': decrypt_std,
        'throughput_encrypt_mb_s': throughput_encrypt,
        'throughput_decrypt_mb_s': throughput_decrypt,
        'iterations': iterations,
    }


def print_results(results):
    """Print benchmark results in a formatted way."""
    print(f"\n{'='*60}")
    print(f"Benchmark Results: {results['size_mb']:.2f} MB")
    print(f"{'='*60}")
    print(f"Size: {results['size_bytes']:,} bytes ({results['size_mb']:.2f} MB)")
    print(f"\nEncryption:")
    print(f"  Average: {results['encrypt_avg']*1000:.2f} ms")
    print(f"  Std Dev: {results['encrypt_std']*1000:.2f} ms")
    print(f"  Throughput: {results['throughput_encrypt_mb_s']:.2f} MB/s")
    print(f"\nDecryption:")
    print(f"  Average: {results['decrypt_avg']*1000:.2f} ms")
    print(f"  Std Dev: {results['decrypt_std']*1000:.2f} ms")
    print(f"  Throughput: {results['throughput_decrypt_mb_s']:.2f} MB/s")
    print(f"\nTarget Performance:")
    print(f"  Target Encrypt: 10-50 MB/s")
    print(f"  Current Encrypt: {results['throughput_encrypt_mb_s']:.2f} MB/s")
    if results['throughput_encrypt_mb_s'] >= 10:
        print(f"  ✅ Meets minimum target (10 MB/s)")
    else:
        improvement_needed = 10 / results['throughput_encrypt_mb_s']
        print(f"  ❌ Needs {improvement_needed:.1f}x improvement to reach 10 MB/s")
    print(f"{'='*60}\n")


def main():
    """Run benchmarks for different file sizes."""
    print("CSF-Crypto Performance Benchmark")
    print("="*60)
    
    # Test sizes in MB
    test_sizes = [0.1, 0.5, 1.0, 5.0, 10.0]
    
    all_results = []
    
    for size_mb in test_sizes:
        print(f"\nTesting {size_mb} MB...")
        try:
            results = benchmark_csf(size_mb, iterations=3, warmup=1)
            if results:
                print_results(results)
                all_results.append(results)
            else:
                print(f"ERROR: Benchmark failed for {size_mb} MB")
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    if all_results:
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"{'Size (MB)':<12} {'Encrypt (MB/s)':<18} {'Decrypt (MB/s)':<18}")
        print("-"*60)
        for r in all_results:
            print(f"{r['size_mb']:<12.2f} {r['throughput_encrypt_mb_s']:<18.2f} {r['throughput_decrypt_mb_s']:<18.2f}")
        print("="*60)
        
        # Check if we meet targets
        avg_encrypt = np.mean([r['throughput_encrypt_mb_s'] for r in all_results])
        avg_decrypt = np.mean([r['throughput_decrypt_mb_s'] for r in all_results])
        
        print(f"\nAverage Throughput:")
        print(f"  Encryption: {avg_encrypt:.2f} MB/s")
        print(f"  Decryption: {avg_decrypt:.2f} MB/s")
        
        if avg_encrypt >= 10:
            print(f"\n✅ PASS: Average encryption throughput ({avg_encrypt:.2f} MB/s) meets minimum target (10 MB/s)")
        else:
            print(f"\n❌ FAIL: Average encryption throughput ({avg_encrypt:.2f} MB/s) below minimum target (10 MB/s)")


if __name__ == "__main__":
    main()

