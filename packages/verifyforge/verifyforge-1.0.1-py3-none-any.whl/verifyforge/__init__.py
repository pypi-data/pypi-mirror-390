"""
VerifyForge Python SDK

Official Python client library for the VerifyForge Email Validation API.
Provides powerful email validation with hybrid validation and batch processing.

Example:
    >>> from verifyforge import VerifyForge
    >>> client = VerifyForge(api_key="your_api_key")
    >>> result = client.validate("test@example.com")
    >>> print(result.is_valid)
"""

from verifyforge.client import VerifyForge
from verifyforge.errors import VerifyForgeError
from verifyforge.types import (
    ValidationResult,
    BulkValidationResult,
    BulkValidationResponse,
    ValidationResponse,
)

__version__ = "1.0.0"
__all__ = [
    "VerifyForge",
    "VerifyForgeError",
    "ValidationResult",
    "BulkValidationResult",
    "BulkValidationResponse",
    "ValidationResponse",
]
