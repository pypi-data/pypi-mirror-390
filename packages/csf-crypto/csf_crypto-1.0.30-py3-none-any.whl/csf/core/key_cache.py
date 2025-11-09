"""
Key caching for CSF-Crypto.

Caches Kyber key pairs to avoid regeneration overhead,
significantly improving performance for repeated operations.
"""

from typing import Dict, Tuple, Optional, Any
from threading import Lock
import numpy as np
from csf.core.fractal_hash import fractal_hash


class KeyCache:
    """
    Thread-safe cache for Kyber key pairs.
    
    Caches keys based on semantic key hash to avoid regeneration
    overhead. This can save 0.1-0.5s per encryption operation.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize key cache.
        
        Args:
            max_size: Maximum number of cached key pairs
        """
        self._cache: Dict[str, Tuple[bytes, bytes]] = {}
        self._semantic_vector_cache: Dict[str, np.ndarray] = {}
        self._shared_secret_cache: Dict[str, Tuple[bytes, np.ndarray]] = {}
        self._max_size = max_size
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
    
    def _get_cache_key(self, semantic_key: str, pqc_scheme: str) -> str:
        """
        Generate cache key from semantic key and PQC scheme.
        
        Uses fractal hash to maintain protocol alignment (100% fractal-based).
        
        Args:
            semantic_key: Semantic key text
            pqc_scheme: PQC scheme name
            
        Returns:
            Cache key (fractal hash hex)
        """
        key_data = f"{semantic_key}:{pqc_scheme}".encode('utf-8')
        # Use fractal hash instead of SHA-256 for protocol alignment
        return fractal_hash(key_data, output_length=32).hex()
    
    def get_or_generate(
        self, 
        semantic_key: str, 
        pqc_scheme: str,
        generate_func
    ) -> Tuple[bytes, bytes]:
        """
        Get cached keys or generate new ones.
        
        Args:
            semantic_key: Semantic key text
            pqc_scheme: PQC scheme name
            generate_func: Function to generate keys if not cached
                          Should return (public_key, private_key)
        
        Returns:
            Tuple of (public_key, private_key)
        """
        cache_key = self._get_cache_key(semantic_key, pqc_scheme)
        
        with self._lock:
            # Check cache
            if cache_key in self._cache:
                self._hits += 1
                return self._cache[cache_key]
            
            # Generate new keys
            self._misses += 1
            public_key, private_key = generate_func()
            
            # Cache if not full
            if len(self._cache) < self._max_size:
                self._cache[cache_key] = (public_key, private_key)
            else:
                # Evict oldest (FIFO) - simple eviction
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
                self._cache[cache_key] = (public_key, private_key)
            
            return public_key, private_key
    
    def get_semantic_vector(self, semantic_key_text: str, compute_func) -> np.ndarray:
        """
        Get cached semantic vector or compute new one.
        
        Args:
            semantic_key_text: Semantic key text
            compute_func: Function to compute semantic vector if not cached
        
        Returns:
            Semantic vector as numpy array
        """
        cache_key = self._get_cache_key(semantic_key_text, "semantic_vector")
        
        with self._lock:
            if cache_key in self._semantic_vector_cache:
                return self._semantic_vector_cache[cache_key].copy()
            
            vector = compute_func()
            
            # Cache if not full
            if len(self._semantic_vector_cache) < self._max_size:
                self._semantic_vector_cache[cache_key] = vector.copy()
            else:
                # Evict oldest
                oldest_key = next(iter(self._semantic_vector_cache))
                del self._semantic_vector_cache[oldest_key]
                self._semantic_vector_cache[cache_key] = vector.copy()
            
            return vector
    
    def get_shared_secret(self, semantic_key_text: str, pqc_scheme: str, math_public_key: bytes, math_private_key: bytes, compute_func) -> Tuple[bytes, np.ndarray]:
        """
        Get cached shared secret or compute new one.
        
        Args:
            semantic_key_text: Semantic key text
            pqc_scheme: PQC scheme name
            math_public_key: Mathematical public key (for cache key)
            math_private_key: Mathematical private key (for cache key)
            compute_func: Function to compute shared secret if not cached
                         Should return (shared_secret_bytes, shared_secret_arr)
        
        Returns:
            Tuple of (shared_secret_bytes, shared_secret_arr)
        """
        # Include public key in cache key to ensure correct shared secret
        key_hash = fractal_hash(math_public_key + math_private_key, output_length=16).hex()
        cache_key = self._get_cache_key(semantic_key_text, f"{pqc_scheme}_shared_secret_{key_hash}")
        
        with self._lock:
            if cache_key in self._shared_secret_cache:
                secret_bytes, secret_arr = self._shared_secret_cache[cache_key]
                return secret_bytes, secret_arr.copy()
            
            secret_bytes, secret_arr = compute_func()
            
            # Cache if not full
            if len(self._shared_secret_cache) < self._max_size:
                self._shared_secret_cache[cache_key] = (secret_bytes, secret_arr.copy())
            else:
                # Evict oldest
                oldest_key = next(iter(self._shared_secret_cache))
                del self._shared_secret_cache[oldest_key]
                self._shared_secret_cache[cache_key] = (secret_bytes, secret_arr.copy())
            
            return secret_bytes, secret_arr
    
    def clear(self):
        """Clear all caches."""
        with self._lock:
            self._cache.clear()
            self._semantic_vector_cache.clear()
            self._shared_secret_cache.clear()
            self._hits = 0
            self._misses = 0
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            return {
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': hit_rate,
                'size': len(self._cache),
                'max_size': self._max_size
            }


# Global cache instance
_global_key_cache = KeyCache(max_size=100)


def get_global_cache() -> KeyCache:
    """Get the global key cache instance."""
    return _global_key_cache

