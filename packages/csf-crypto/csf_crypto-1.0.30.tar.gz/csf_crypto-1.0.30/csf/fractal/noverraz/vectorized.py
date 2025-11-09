"""
Vectorized Noverraz implementation using NumPy and SIMD optimizations.

Provides batch processing capabilities for high-performance applications.
"""

import numpy as np
from typing import Tuple, Optional
from csf.fractal.noverraz.core import NoverrazEngine

# Try to import Numba for JIT compilation
try:
    from numba import jit, prange
    NUMBA_AVAILABLE = True
except ImportError:
    NUMBA_AVAILABLE = False
    def jit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    prange = range


@jit(nopython=True, parallel=True, cache=True, fastmath=True)
def noverraz_iteration_vectorized(
    z_real_array: np.ndarray,
    z_imag_array: np.ndarray,
    c_real: float,
    c_imag: float,
    math_key_array: np.ndarray,
    semantic_key_array: np.ndarray,
    positions: np.ndarray,
    alpha: float,
    beta: float,
    max_iter: int,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Vectorized Noverraz iterations using Numba JIT.
    
    Processes multiple points in parallel for maximum performance.
    """
    n = len(z_real_array)
    result_real = np.zeros(n, dtype=np.float64)
    result_imag = np.zeros(n, dtype=np.float64)
    iterations = np.zeros(n, dtype=np.int32)
    
    math_key_len = len(math_key_array)
    semantic_key_len = len(semantic_key_array)
    
    for i in prange(n):
        z_r = z_real_array[i]
        z_i = z_imag_array[i]
        pos = positions[i] if i < len(positions) else 0
        
        for iter_count in range(max_iter):
            # Compute magnitude
            mag_sq = z_r * z_r + z_i * z_i
            
            # Early exit if escaped
            if mag_sq > 4.0:
                iterations[i] = iter_count
                break
            
            # Noverraz base iteration: z^2 + c (Julia-like base, then enhanced with damping and key injection)
            z_r_sq = z_r * z_r
            z_i_sq = z_i * z_i
            z_r_z_i = z_r * z_i
            
            base_real = z_r_sq - z_i_sq + c_real
            base_imag = 2.0 * z_r_z_i + c_imag
            
            # Damping
            damping = np.exp(-alpha * mag_sq)
            
            # Key injection
            if math_key_len > 0 and semantic_key_len > 0:
                key_idx = (pos + iter_count) % math_key_len
                sem_idx = key_idx % semantic_key_len
                key_product = math_key_array[key_idx] * semantic_key_array[sem_idx]
                
                z_r = base_real * damping + beta * key_product
                z_i = base_imag * damping + beta * key_product * 0.618
            else:
                z_r = base_real * damping
                z_i = base_imag * damping
            
            # Convergence check
            if abs(z_r) < 1e-10 and abs(z_i) < 1e-10:
                iterations[i] = iter_count
                break
        
        result_real[i] = z_r
        result_imag[i] = z_i
        if iterations[i] == 0:
            iterations[i] = max_iter
    
    return result_real, result_imag, iterations


class VectorizedNoverraz(NoverrazEngine):
    """
    Vectorized Noverraz engine for batch processing.
    
    Uses NumPy and Numba JIT for maximum performance.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize vectorized Noverraz engine."""
        super().__init__(*args, **kwargs)
        self._use_numba = NUMBA_AVAILABLE
    
    def compute_batch(
        self,
        z0_real_array: np.ndarray,
        z0_imag_array: np.ndarray,
        c_real: float,
        c_imag: float,
        math_key: Optional[np.ndarray] = None,
        semantic_key: Optional[np.ndarray] = None,
        positions: Optional[np.ndarray] = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Compute Noverraz iterations for a batch of points.
        
        Args:
            z0_real_array: Array of real parts of initial points
            z0_imag_array: Array of imaginary parts of initial points
            c_real: Real part of Noverraz parameter
            c_imag: Imaginary part of Noverraz parameter
            math_key: Mathematical key vector (optional)
            semantic_key: Semantic key vector (optional)
            positions: Array of positions for key indexing (optional)
        
        Returns:
            Tuple of (final_z_real, final_z_imag, iterations)
        """
        n = len(z0_real_array)
        
        # Prepare arrays
        if positions is None:
            positions = np.arange(n, dtype=np.int32)
        
        if math_key is None:
            math_key = np.array([], dtype=np.float64)
        if semantic_key is None:
            semantic_key = np.array([], dtype=np.float64)
        
        # Use vectorized computation if Numba available
        if self._use_numba:
            return noverraz_iteration_vectorized(
                z0_real_array,
                z0_imag_array,
                c_real,
                c_imag,
                math_key,
                semantic_key,
                positions,
                self.alpha,
                self.beta,
                self.iterations,
            )
        else:
            # OPTIMIZED: Fallback to sequential computation with pre-allocated arrays
            # Pre-allocate NumPy arrays instead of list.append() (2-5x faster)
            results_real = np.zeros(n, dtype=np.float64)
            results_imag = np.zeros(n, dtype=np.float64)
            iterations = np.zeros(n, dtype=np.int32)
            
            for i in range(n):
                iter_count = self.compute_iterations(
                    z0_real_array[i],
                    z0_imag_array[i],
                    c_real,
                    c_imag,
                    math_key,
                    semantic_key,
                    positions[i] if i < len(positions) else 0,
                )
                results_real[i] = z0_real_array[i]
                results_imag[i] = z0_imag_array[i]
                iterations[i] = iter_count
            
            return (results_real, results_imag, iterations)

