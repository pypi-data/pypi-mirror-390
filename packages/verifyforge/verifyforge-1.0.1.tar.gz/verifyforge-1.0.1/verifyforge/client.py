"""
Main VerifyForge client class.
"""

import requests
from typing import List, Optional
from urllib.parse import urljoin

from verifyforge.errors import (
    VerifyForgeError,
    AuthenticationError,
    RateLimitError,
    InsufficientCreditsError,
    ValidationError,
    APIError,
)
from verifyforge.types import ValidationResponse, BulkValidationResponse


class VerifyForge:
    """
    VerifyForge API client for email validation.

    This is the main class for interacting with the VerifyForge API.
    It provides methods for validating single emails and bulk validation.

    Args:
        api_key: Your VerifyForge API key
        base_url: Base URL for the API (default: https://verifyforge.com)
        timeout: Request timeout in seconds (default: 30)

    Example:
        >>> from verifyforge import VerifyForge
        >>> client = VerifyForge(api_key="your_api_key")
        >>> result = client.validate("test@example.com")
        >>> print(f"Valid: {result.data.is_valid}")

    Raises:
        AuthenticationError: If the API key is invalid
        InsufficientCreditsError: If account has insufficient credits
        RateLimitError: If rate limit is exceeded
        ValidationError: If request validation fails
        APIError: If an unexpected API error occurs
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://verifyforge.com",
        timeout: int = 30,
    ):
        """
        Initialize the VerifyForge client.

        Args:
            api_key: Your VerifyForge API key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session."""
        session = requests.Session()
        session.headers.update(
            {
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "VerifyForge-Python-SDK/1.0.0",
            }
        )
        return session

    def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> dict:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response data as dictionary

        Raises:
            VerifyForgeError: If the request fails
        """
        url = urljoin(self.base_url, endpoint)

        try:
            response = self._session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )

            # Handle HTTP errors
            if response.status_code == 401:
                raise AuthenticationError("Invalid API key")
            elif response.status_code == 402:
                raise InsufficientCreditsError("Insufficient credits")
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            elif response.status_code == 400:
                error_data = response.json()
                raise ValidationError(
                    message=error_data.get("error", "Validation failed"),
                    details=error_data,
                )
            elif response.status_code >= 500:
                raise APIError(
                    message="Internal server error",
                    status_code=response.status_code,
                )
            elif not response.ok:
                error_data = response.json() if response.content else {}
                raise APIError(
                    message=error_data.get("error", "Request failed"),
                    status_code=response.status_code,
                )

            return response.json()

        except requests.exceptions.Timeout:
            raise VerifyForgeError("Request timed out")
        except requests.exceptions.ConnectionError:
            raise VerifyForgeError("Connection failed")
        except requests.exceptions.RequestException as e:
            raise VerifyForgeError(f"Request failed: {str(e)}")

    def validate(self, email: str) -> ValidationResponse:
        """
        Validate a single email address.

        Performs comprehensive validation including syntax, MX records,
        SMTP verification, and disposable/role account detection.

        Args:
            email: Email address to validate

        Returns:
            ValidationResponse with complete validation results

        Example:
            >>> result = client.validate("user@example.com")
            >>> if result.data.is_valid:
            ...     print("Email is valid!")
            >>> print(f"Credits remaining: {result.remaining_credits}")

        Raises:
            ValidationError: If email format is invalid
            InsufficientCreditsError: If account has insufficient credits
            APIError: If validation fails
        """
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")

        data = self._make_request(
            method="GET",
            endpoint="/api/validate",
            params={"email": email},
        )

        return ValidationResponse.from_dict(data)

    def validate_bulk(self, emails: List[str]) -> BulkValidationResponse:
        """
        Validate multiple email addresses in bulk.

        Validates up to 100 emails in a single request. Automatically
        deduplicates emails and filters out invalid formats.

        Args:
            emails: List of email addresses to validate (max 100)

        Returns:
            BulkValidationResponse with results for all emails

        Example:
            >>> emails = ["user1@example.com", "user2@example.com"]
            >>> result = client.validate_bulk(emails)
            >>> print(f"Validated {result.summary.total} emails")
            >>> for item in result.results:
            ...     print(f"{item.email}: {item.is_valid}")

        Raises:
            ValidationError: If email list is invalid or exceeds 100 emails
            InsufficientCreditsError: If account has insufficient credits
            APIError: If validation fails
        """
        if not emails or not isinstance(emails, list):
            raise ValueError("Emails must be a non-empty list")

        if len(emails) > 100:
            raise ValidationError(
                message="Maximum 100 emails allowed per request",
                details={"provided": len(emails), "maximum": 100},
            )

        data = self._make_request(
            method="POST",
            endpoint="/api/validate/bulk",
            json={"emails": emails},
        )

        return BulkValidationResponse.from_dict(data)

    def close(self):
        """Close the HTTP session."""
        if self._session:
            self._session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return f"VerifyForge(base_url={self.base_url!r})"
