"""Custom exceptions for CSF."""


class CSFError(Exception):
    """Base exception for CSF."""

    pass


class SecurityError(CSFError):
    """Security-related error."""

    pass


class ValidationError(CSFError):
    """Input validation error."""

    pass


class CryptographicError(CSFError):
    """Cryptographic operation error."""

    pass


class KeyError(CSFError):
    """Key-related error."""

    pass


class EncodingError(CSFError):
    """Encoding/decoding error."""

    pass
