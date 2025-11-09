"""Setup script for CSF package.

CSF - Cryptographic Security Framework
Inventor: Jeremy Noverraz (1988 - 2025) based on an idea by Ivàn Àvalos AND JCZD (engrenage.ch)
"""

import os
import subprocess
import sys
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

# Try to import Cython
try:
    from Cython.Build import cythonize
    CYTHON_AVAILABLE = True
except ImportError:
    CYTHON_AVAILABLE = False
    cythonize = None

# Try to import numpy (may not be available during build)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Read README for long description (prefer PyPI-specific version)
try:
    with open("README_PYPI.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            long_description = fh.read()
    except FileNotFoundError:
        long_description = """CSF-Crypto: Post-Quantum Cryptographic Security Framework

Military-grade post-quantum cryptographic system integrating fractal geometry with semantic keys. 
Resistant to both classical and quantum attacks (Shor's and Grover's algorithms).

Features:
- NIST PQC standards (CRYSTALS-Kyber, Dilithium, SPHINCS+)
- Fractal-based message encoding
- Dual-layer key system (mathematical + semantic)
- Constant-time operations for side-channel protection
- Simple API like standard cryptographic libraries

Installation: pip install csf-crypto
Documentation: https://github.com/iyotee/csf
"""

# Prepare Cython extensions
ext_modules = None
if CYTHON_AVAILABLE and NUMPY_AVAILABLE:
    try:
        extensions = [
            Extension(
                "csf.fractal._encode_cython",
                ["csf/fractal/_encode_cython.pyx"],
                include_dirs=[np.get_include()],
                extra_compile_args=["-O3", "-ffast-math"],
                language="c",
            ),
            Extension(
                "csf.fractal._decode_cython",
                ["csf/fractal/_decode_cython.pyx"],
                include_dirs=[np.get_include()],
                extra_compile_args=["-O3", "-ffast-math"],
                language="c",
            ),
        ]
        
        # Cythonize extensions
        ext_modules = cythonize(
            extensions,
            compiler_directives={
                "language_level": "3",
                "boundscheck": False,
                "wraparound": False,
                "cdivision": True,
                "initializedcheck": False,
            },
        )
    except Exception as e:
        print(f"Warning: Could not build Cython extensions: {e}")
        print("CSF will work without Cython optimizations (slower but functional)")
        ext_modules = None


class RustBuildExtension(build_ext):
    """Custom build extension to build Rust bindings with maturin."""
    
    def run(self):
        # First build Cython extensions
        super().run()
        
        # Then try to build Rust bindings
        rust_dir = os.path.join(os.path.dirname(__file__), "rust")
        if not os.path.exists(rust_dir):
            print("Warning: rust/ directory not found, skipping Rust bindings")
            return
        
        # Check for maturin
        maturin_cmd = None
        for path in [os.path.join(os.environ.get("VIRTUAL_ENV", ""), "bin", "maturin"),
                     os.path.expanduser("~/.cargo/bin/maturin"),
                     "maturin"]:
            if os.path.exists(path) if path != "maturin" else True:
                try:
                    subprocess.run([path, "--version"], capture_output=True, check=True)
                    maturin_cmd = path
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        
        if not maturin_cmd:
            print("Warning: maturin not found, skipping Rust bindings")
            print("Install with: pip install maturin or cargo install maturin")
            return
        
        # Build Rust extension
        try:
            print("Building Rust bindings with maturin...")
            env = os.environ.copy()
            env["PYO3_USE_ABI3_FORWARD_COMPATIBILITY"] = "1"
            
            result = subprocess.run(
                [maturin_cmd, "develop", "--release", "--manifest-path", os.path.join(rust_dir, "Cargo.toml")],
                cwd=rust_dir,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("Successfully built Rust bindings!")
            else:
                print(f"Warning: Rust build failed: {result.stderr}")
                print("CSF will work without Rust optimizations (slower but functional)")
        except Exception as e:
            print(f"Warning: Could not build Rust bindings: {e}")
            print("CSF will work without Rust optimizations (slower but functional)")


setup(
    name="csf-crypto",
    version="1.0.28",
    author="Jeremy Noverraz (based on an idea by Ivàn Àvalos AND JCZD (engrenage.ch))",
    maintainer="Jeremy Noverraz",
    author_email="",
    description="Post-quantum cryptographic framework with fractal encoding and semantic keys - resistant to quantum attacks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iyotee/csf",
    packages=find_packages(exclude=["tests", "tests.*", "venv", "venv.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "matplotlib>=3.7.0",
        "msgpack>=1.0.0",
    ],
    extras_require={
        "pqc": [
            # Note: These packages may not be available on PyPI
            # CSF includes fallback implementations if these are not installed
            # "pykyber>=0.1.0",  # Optional: CRYSTALS-Kyber (may not exist on PyPI)
            # "python-pqc>=0.1.0",  # Optional: Additional PQC schemes (may not exist on PyPI)
            # "pysphincs>=0.1.0",  # Optional: SPHINCS+ (may not exist on PyPI)
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
        "cython": [
            "cython>=3.0.0",
        ],
        "performance": [
            "numba>=0.58.0",  # CRITICAL: JIT compilation for 50-200x speedup (highly recommended!)
            "cython>=3.0.0",  # Optional: Cython extensions for 2-5x speedup
        ],
    },
    ext_modules=ext_modules,  # Cython extensions (if available)
    cmdclass={"build_ext": RustBuildExtension},
    entry_points={
        "console_scripts": [
            "csf-keygen=csf.tools.keygen:main",
            "csf-benchmark=csf.tools.benchmark:main",
        ],
    },
    keywords="cryptography, post-quantum, fractal, encryption, security, NIST PQC",
    project_urls={
        "Documentation": "https://github.com/iyotee/csf",
        "Source": "https://github.com/iyotee/csf",
        "GitHub": "https://github.com/iyotee/csf",
    },
    include_package_data=True,
    zip_safe=False,
)
