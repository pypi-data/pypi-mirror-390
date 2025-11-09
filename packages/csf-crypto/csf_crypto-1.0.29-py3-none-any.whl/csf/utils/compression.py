"""
Compression utilities for CSF-Crypto.

Provides optimized compression using lz4 for better performance,
with fallback to zlib for compatibility.
"""

import zlib
from typing import Optional


# Try to import lz4 for faster compression
try:
    import lz4.frame
    LZ4_AVAILABLE = True
except ImportError:
    LZ4_AVAILABLE = False


def compress_data(data: bytes, algorithm: str = "auto", level: int = 1) -> bytes:
    """
    Compress data using the fastest available algorithm.
    
    Args:
        data: Data to compress
        algorithm: Compression algorithm ("auto", "lz4", "zlib")
                   "auto" uses lz4 if available, falls back to zlib
        level: Compression level (1-9 for zlib, 1-16 for lz4)
               Lower = faster, higher = better compression
        
    Returns:
        Compressed data
    """
    # Don't compress very small data
    if len(data) < 1024:
        return data
    
    # Auto-detect best algorithm
    if algorithm == "auto":
        if LZ4_AVAILABLE:
            algorithm = "lz4"
        else:
            algorithm = "zlib"
    
    # Compress using selected algorithm
    if algorithm == "lz4" and LZ4_AVAILABLE:
        # lz4 is 2-3x faster than zlib
        return lz4.frame.compress(data, compression_level=level)
    elif algorithm == "zlib":
        # zlib fallback (compatible everywhere)
        return zlib.compress(data, level=min(level, 9))
    else:
        raise ValueError(f"Unsupported compression algorithm: {algorithm}")


def decompress_data(data: bytes, algorithm: Optional[str] = None) -> bytes:
    """
    Decompress data, auto-detecting the algorithm.
    
    Args:
        data: Compressed data
        algorithm: Compression algorithm ("auto", "lz4", "zlib")
                   If None, auto-detects based on magic bytes
        
    Returns:
        Decompressed data
    """
    # Auto-detect algorithm if not specified
    if algorithm is None or algorithm == "auto":
        # Try lz4 first (magic bytes: 0x184D2204)
        if len(data) >= 4 and data[:4] == b'\x04\x22\x4D\x18':
            algorithm = "lz4"
        else:
            # Assume zlib (no magic bytes, but zlib can decompress most things)
            algorithm = "zlib"
    
    # Decompress
    if algorithm == "lz4" and LZ4_AVAILABLE:
        try:
            return lz4.frame.decompress(data)
        except:
            # Fallback to zlib if lz4 fails
            algorithm = "zlib"
    
    if algorithm == "zlib":
        return zlib.decompress(data)
    else:
        raise ValueError(f"Unsupported compression algorithm: {algorithm}")

