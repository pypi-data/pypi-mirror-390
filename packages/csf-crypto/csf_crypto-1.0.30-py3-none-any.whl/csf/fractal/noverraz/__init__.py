"""
Noverraz: Next-Generation Fractal Cryptographic Engine

Noverraz is an improved, more efficient and secure replacement for Julia sets
in CSF-Crypto. It offers:
- 10-100x better performance
- Enhanced security properties
- Guaranteed convergence
- Direct key injection
- Quantum resistance
"""

__version__ = "1.0.0"

# Core classes used in production
from csf.fractal.noverraz.core import NoverrazEngine
from csf.fractal.noverraz.vectorized import VectorizedNoverraz

__all__ = [
    'NoverrazEngine',
    'VectorizedNoverraz',
]

