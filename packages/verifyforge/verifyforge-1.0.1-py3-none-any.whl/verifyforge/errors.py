"""
Custom exceptions for the VerifyForge SDK.
"""

from typing import Optional, Dict, Any


class VerifyForgeError(Exception):
    """
    Base exception class for all VerifyForge SDK errors.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code if applicable
        error_code: Machine-readable error code
        details: Additional error details
        docs_url: URL to relevant documentation
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        docs_url: Optional[str] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        self.docs_url = docs_url or "https://verifyforge.com/api-docs"

        super().__init__(self.message)

    def __str__(self) -> str:
        error_parts = [f"VerifyForgeError: {self.message}"]

        if self.status_code:
            error_parts.append(f"Status Code: {self.status_code}")

        if self.error_code:
            error_parts.append(f"Error Code: {self.error_code}")

        if self.details:
            error_parts.append(f"Details: {self.details}")

        if self.docs_url:
            error_parts.append(f"Docs: {self.docs_url}")

        return " | ".join(error_parts)

    def __repr__(self) -> str:
        return (
            f"VerifyForgeError(message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"error_code={self.error_code!r})"
        )


class AuthenticationError(VerifyForgeError):
    """Raised when API key authentication fails."""

    def __init__(self, message: str = "Invalid API key"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
        )


class RateLimitError(VerifyForgeError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_ERROR",
        )


class InsufficientCreditsError(VerifyForgeError):
    """Raised when account has insufficient credits."""

    def __init__(self, message: str = "Insufficient credits"):
        super().__init__(
            message=message,
            status_code=402,
            error_code="INSUFFICIENT_CREDITS",
        )


class ValidationError(VerifyForgeError):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class APIError(VerifyForgeError):
    """Raised when the API returns an unexpected error."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(
            message=message,
            status_code=status_code,
            error_code="API_ERROR",
        )
