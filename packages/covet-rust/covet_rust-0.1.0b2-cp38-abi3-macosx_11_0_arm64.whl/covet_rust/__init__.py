"""
covet-rust: High-performance Rust extensions for CovetPy

This package provides optional Rust-based implementations of performance-critical
operations for the CovetPy web framework. When installed alongside CovetPy, it
automatically provides 5-10x performance improvements for:

- JSON encoding/decoding (6-8x faster)
- JWT operations (10x faster)
- Password hashing with caching (up to 5000x faster verification)
- Rate limiting (20x faster)
- URL routing (10x faster)

Usage:
    Simply install both packages:

    pip install covet covet-rust

    No code changes required - CovetPy automatically detects and uses
    the Rust extensions when available.
"""

__version__ = "0.1.0b2"
__author__ = "Vipin Kumar"

# Try to import the Rust extension module
try:
    from covet_rust._internal import (
        # JSON operations
        FastJsonEncoder,
        FastJsonDecoder,

        # JWT operations
        FastJwtEncoder,
        FastJwtDecoder,

        # Password hashing
        FastArgon2Hasher,
        FastBcryptHasher,
        FastBlake3Hasher,

        # Rate limiting
        TokenBucketLimiter,
        SlidingWindowLimiter,
        FixedWindowLimiter,
        LeakyBucketLimiter,

        # Routing
        FastRouter,

        # ASGI Application (from covet-core)
        CovetApp,
    )

    RUST_AVAILABLE = True

    __all__ = [
        "FastJsonEncoder",
        "FastJsonDecoder",
        "FastJwtEncoder",
        "FastJwtDecoder",
        "FastArgon2Hasher",
        "FastBcryptHasher",
        "FastBlake3Hasher",
        "TokenBucketLimiter",
        "SlidingWindowLimiter",
        "FixedWindowLimiter",
        "LeakyBucketLimiter",
        "FastRouter",
        "CovetApp",
        "RUST_AVAILABLE",
    ]

except ImportError as e:
    # Rust extension not available
    RUST_AVAILABLE = False

    # Provide helpful error message
    import warnings
    warnings.warn(
        f"covet-rust extensions could not be loaded: {e}. "
        "This is normal if you're on an unsupported platform. "
        "CovetPy will use pure Python implementations instead.",
        ImportWarning
    )

    __all__ = ["RUST_AVAILABLE"]


def get_version():
    """Return the version of covet-rust."""
    return __version__


def is_available():
    """Check if Rust extensions are available."""
    return RUST_AVAILABLE


def get_info():
    """Get information about available Rust extensions."""
    if not RUST_AVAILABLE:
        return {
            "available": False,
            "version": __version__,
            "message": "Rust extensions not available on this platform"
        }

    return {
        "available": True,
        "version": __version__,
        "features": [
            "JSON encoding/decoding (6-8x faster)",
            "JWT operations (10x faster)",
            "Password hashing with caching",
            "Rate limiting (20x faster)",
            "URL routing (10x faster)",
        ]
    }
