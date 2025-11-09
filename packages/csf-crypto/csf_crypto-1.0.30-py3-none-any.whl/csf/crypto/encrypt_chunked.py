"""
Chunked parallel encryption for large files.

Implements chunking and parallel processing to improve performance for large data.
"""

import math
from typing import Dict, Optional, Union
import numpy as np
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing as mp
from csf.core.keys import KeyManager
from csf.fractal.encoder import FractalEncoder
from csf.semantic.vectorizer import SemanticVectorizer
from csf.fractal.visualizer import FractalSignature
from csf.security.validation import validate_string, validate_bytes, validate_string_or_bytes
from csf.core.fractal_hash import fractal_hash
from csf.utils.serialization import serialize_encrypted_data


def encrypt_chunk(chunk_data: bytes, chunk_index: int, semantic_key_text: str, 
                  shared_secret: bytes, semantic_vector: np.ndarray) -> Dict:
    """
    Encrypt a single chunk of data.
    
    Args:
        chunk_data: Chunk of data to encrypt
        chunk_index: Index of this chunk
        semantic_key_text: Semantic key text
        shared_secret: Shared secret bytes
        semantic_vector: Semantic vector
        
    Returns:
        Encrypted chunk dictionary
    """
    # Convert chunk to string
    message = chunk_data.decode('utf-8')
    
    # Use optimized encoder (already imported as FractalEncoder)
    fractal_encoder = FractalEncoder(iterations=25)
    
    # Extract shared secret array
    shared_secret_arr = np.frombuffer(shared_secret[:128], dtype=np.float64)
    
    # Encode message
    fractal_params = fractal_encoder.encode_message(message, shared_secret_arr, semantic_vector)
    
    return {
        'index': chunk_index,
        'params': fractal_params,
        'size': len(chunk_data)
    }


def encrypt_chunked(
    message: Union[str, bytes],
    semantic_key_text: str,
    math_public_key: Optional[bytes] = None,
    math_private_key: Optional[bytes] = None,
    pqc_scheme: str = "Kyber768",
    chunk_size: int = 131072,  # OPTIMIZATION: 128KB chunks (was 64KB) for better performance
    num_workers: Optional[int] = None,
    return_dict: bool = False,
    compress: bool = True,
    generate_signature: bool = False,
) -> Union[bytes, Dict]:
    """
    Encrypt with chunking and parallel processing.
    
    Args:
        message: Message to encrypt
        semantic_key_text: Semantic key
        math_public_key: Optional public key
        math_private_key: Optional private key
        pqc_scheme: PQC scheme
        chunk_size: Size of each chunk (default 8KB)
        num_workers: Number of parallel workers (default: CPU count)
        return_dict: Return dict format
        compress: Compress output
        
    Returns:
        Encrypted data
    """
    # Validate inputs
    message = validate_string_or_bytes(message, "message")
    validate_string(semantic_key_text, "semantic_key_text")
    
    # Initialize components
    key_manager = KeyManager(pqc_scheme)
    semantic_vectorizer = SemanticVectorizer()
    
    # Generate or use provided keys (with caching)
    from csf.core.key_cache import get_global_cache
    cache = get_global_cache()
    
    if math_public_key is None or math_private_key is None:
        math_public_key, math_private_key = cache.get_or_generate(
            semantic_key_text,
            pqc_scheme,
            lambda: key_manager.generate_key_pair()
        )
    else:
        validate_bytes(math_public_key, "math_public_key")
        validate_bytes(math_private_key, "math_private_key")
    
    # Derive shared secret (with caching)
    def compute_shared_secret():
        secret = key_manager.derive_shared_secret(math_public_key, math_private_key)
        secret_arr = np.frombuffer(secret[:128], dtype=np.float64)
        return secret, secret_arr
    
    shared_secret, _ = cache.get_shared_secret(
        semantic_key_text, pqc_scheme, math_public_key, math_private_key, compute_shared_secret
    )
    
    # OPTIMIZATION: Reduced to 16 bytes (sufficient for validation, 2x faster)
    shared_secret_hash = fractal_hash(shared_secret, output_length=16)
    
    # Transform semantic key (with caching)
    semantic_vector = cache.get_semantic_vector(
        semantic_key_text, lambda: semantic_vectorizer.text_to_vector(semantic_key_text)
    )
    
    # Convert message to bytes
    message_bytes = message.encode('utf-8')
    
    # Decide whether to use chunking
    if len(message_bytes) < chunk_size:
        # Small message: use core encryption directly (avoid recursion)
        from csf.crypto.encrypt import _encrypt_core
        return _encrypt_core(message, semantic_key_text, math_public_key, math_private_key, 
                            pqc_scheme, return_dict, compress, generate_signature)
    
    # Large message: use chunked processing
    if num_workers is None:
        # Use more workers for better parallelization (up to 8)
        num_workers = min(mp.cpu_count(), 8)
    
    # Split into chunks
    chunks = []
    for i in range(0, len(message_bytes), chunk_size):
        chunk = message_bytes[i:i+chunk_size]
        chunks.append((chunk, i // chunk_size))
    
    # Process chunks in parallel
    # Use ProcessPoolExecutor for better CPU utilization (Python GIL bypass)
    # Note: encrypt_chunk must be picklable (top-level function)
    fractal_params = []
    if num_workers > 1 and len(chunks) > 1:
        # PHASE 5 OPTIMIZATION: Adaptive ProcessPoolExecutor threshold
        # Only use ProcessPoolExecutor if chunks are large enough (overhead < 10% of processing time)
        min_chunk_size = 128 * 1024  # 128KB threshold
        avg_chunk_size = len(message_bytes) // len(chunks)
        
        if avg_chunk_size >= min_chunk_size:
            # Large chunks: ProcessPoolExecutor (true parallelism, bypasses GIL)
            with ProcessPoolExecutor(max_workers=num_workers) as executor:
                futures = [
                    executor.submit(encrypt_chunk, chunk, idx, semantic_key_text, 
                                  shared_secret, semantic_vector)
                    for chunk, idx in chunks
                ]
                
                # Collect results in order
                chunk_results = [future.result() for future in futures]
                chunk_results.sort(key=lambda x: x['index'])
                
                # Combine fractal params
                for result in chunk_results:
                    fractal_params.extend(result['params'])
        else:
            # Small chunks: ThreadPoolExecutor (less overhead, GIL acceptable for small data)
            with ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [
                    executor.submit(encrypt_chunk, chunk, idx, semantic_key_text, 
                                  shared_secret, semantic_vector)
                    for chunk, idx in chunks
                ]
                
                # Collect results in order
                chunk_results = [future.result() for future in futures]
                chunk_results.sort(key=lambda x: x['index'])
                
                # Combine fractal params
                for result in chunk_results:
                    fractal_params.extend(result['params'])
    else:
        # Single worker or single chunk: process directly
        for chunk, idx in chunks:
            result = encrypt_chunk(chunk, idx, semantic_key_text, shared_secret, semantic_vector)
            fractal_params.extend(result['params'])
    
    # Generate signature (OPTIMIZATION: Optional, disabled by default for performance)
    signature_hash = None
    signature_image_shape = None
    if generate_signature:
        # OPTIMIZATION: Reduced resolution 32x32 → 8x8 (16x fewer pixels = 16x faster)
        signature_gen = FractalSignature(width=8, height=8)
        shared_secret_arr = np.frombuffer(shared_secret[:128], dtype=np.float64)
        signature_image, signature_hash = signature_gen.generate_signature(
            message, shared_secret_arr, semantic_vector, math_private_key
        )
        signature_image_shape = list(signature_image.shape)
    
    # OPTIMIZED: Vectorized validation using NumPy (much faster than loops)
    num_params = len(fractal_params)
    if num_params > 0:
        # Pre-extract all values into arrays (single pass, direct access)
        c_real_arr = np.zeros(num_params, dtype=np.float64)
        c_imag_arr = np.zeros(num_params, dtype=np.float64)
        z0_real_arr = np.zeros(num_params, dtype=np.float64)
        z0_imag_arr = np.zeros(num_params, dtype=np.float64)
        iterations_arr = np.zeros(num_params, dtype=np.int32)
        byte_values_arr = np.zeros(num_params, dtype=np.uint8)
        
        # OPTIMIZED: Cache type checks to reduce isinstance() calls (was 11M calls!)
        # Check type of first element once, then use direct access
        first_param = fractal_params[0]
        c_tuple = first_param["c"]
        z0_tuple = first_param["z0"]
        c_is_tuple = isinstance(c_tuple, (tuple, list))
        z0_is_tuple = isinstance(z0_tuple, (tuple, list))
        
        # Extract in single pass with minimal isinstance() calls
        for i, p in enumerate(fractal_params):
            c_tuple = p["c"]
            z0_tuple = p["z0"]
            
            # Use cached type check for subsequent items (same structure expected)
            if c_is_tuple and isinstance(c_tuple, (tuple, list)):
                c_real_arr[i] = c_tuple[0]
                c_imag_arr[i] = c_tuple[1] if len(c_tuple) > 1 else 0.0
            else:
                c_real_arr[i] = float(c_tuple)
                c_imag_arr[i] = 0.0
            
            if z0_is_tuple and isinstance(z0_tuple, (tuple, list)):
                z0_real_arr[i] = z0_tuple[0]
                z0_imag_arr[i] = z0_tuple[1] if len(z0_tuple) > 1 else 0.0
            else:
                z0_real_arr[i] = float(z0_tuple)
                z0_imag_arr[i] = 0.0
            
            iterations_arr[i] = int(p["iteration"])
            byte_values_arr[i] = int(p["byte_value"]) % 256
        
        # Vectorized finite check (single pass)
        c_real_arr = np.where(np.isfinite(c_real_arr), c_real_arr, 0.0)
        c_imag_arr = np.where(np.isfinite(c_imag_arr), c_imag_arr, 0.0)
        z0_real_arr = np.where(np.isfinite(z0_real_arr), z0_real_arr, 0.0)
        z0_imag_arr = np.where(np.isfinite(z0_imag_arr), z0_imag_arr, 0.0)
        
        # Build validated params list (pre-allocated for better performance)
        validated_params = [None] * num_params
        for i in range(num_params):
            validated_params[i] = {
                "c": [c_real_arr[i], c_imag_arr[i]],  # Keep as list for compatibility
                "z0": [z0_real_arr[i], z0_imag_arr[i]],
                "iteration": int(iterations_arr[i]),
                "byte_value": int(byte_values_arr[i]),
            }
    else:
        validated_params = []
    
    result = {
        "encrypted_data": {
            "fractal_params": validated_params,
            "public_key": list(math_public_key),
            "shared_secret_hash": list(shared_secret_hash),
        },
        "metadata": {"message_length": len(message), "pqc_scheme": pqc_scheme},
    }
    
    # Only include signature if generated
    if signature_hash is not None:
        result["encrypted_data"]["signature_hash"] = signature_hash
        if signature_image_shape is not None:
            result["encrypted_data"]["signature_image_shape"] = signature_image_shape
    
    if return_dict:
        return result
    else:
        return serialize_encrypted_data(result, compress=compress)

