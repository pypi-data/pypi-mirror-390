"""
Type definitions for the VerifyForge SDK.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class SyntaxValidation:
    """Email syntax validation details."""

    valid: bool
    username: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class MXRecord:
    """MX record information."""

    exchange: str
    priority: int


@dataclass
class SMTPAnalysis:
    """SMTP server analysis results."""

    host: Optional[str] = None
    port: Optional[int] = None
    connection_successful: bool = False
    accepts_mail: bool = False
    error: Optional[str] = None


@dataclass
class Gravatar:
    """Gravatar profile information."""

    has_gravatar: bool
    avatar_url: Optional[str] = None
    profile_url: Optional[str] = None


@dataclass
class ValidationResult:
    """
    Complete validation result for a single email address.

    Attributes:
        email: The validated email address
        is_valid: Overall validation status
        syntax: Syntax validation details
        mx_records_list: List of MX records for the domain
        smtp: SMTP verification results
        disposable: Whether the email is from a disposable provider
        role_account: Whether the email is a role-based account
        free_provider: Whether the email is from a free provider
        reachability: Reachability status (safe, risky, invalid, unknown)
        suggestion: Suggested correction for typos
        gravatar: Gravatar profile information if available
    """

    email: str
    is_valid: bool
    disposable: bool
    role_account: bool
    free_provider: bool
    reachability: str
    syntax: Optional[SyntaxValidation] = None
    mx_records_list: List[MXRecord] = None
    smtp: Optional[SMTPAnalysis] = None
    suggestion: Optional[str] = None
    gravatar: Optional[Gravatar] = None

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.mx_records_list is None:
            self.mx_records_list = []

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResult":
        """Create a ValidationResult from API response data."""
        return cls(
            email=data["email"],
            is_valid=data["isValid"],
            disposable=data.get("disposable", False),
            role_account=data.get("roleAccount", False),
            free_provider=data.get("freeProvider", False),
            reachability=data.get("reachability", "unknown"),
            syntax=SyntaxValidation(**data["syntax"]) if data.get("syntax") else None,
            mx_records_list=[MXRecord(**mx) for mx in data.get("mxRecordsList", [])],
            smtp=SMTPAnalysis(**data["smtp"]) if data.get("smtp") else None,
            suggestion=data.get("suggestion"),
            gravatar=Gravatar(**data["gravatar"]) if data.get("gravatar") else None,
        )


@dataclass
class ValidationResponse:
    """
    Response from single email validation.

    Attributes:
        success: Whether the request was successful
        data: Validation result details
        credits_used: Number of credits consumed
        remaining_credits: Remaining account credits
        validation_duration: Time taken for validation in milliseconds
        api_version: API version used
    """

    success: bool
    data: ValidationResult
    credits_used: int
    remaining_credits: int
    validation_duration: Optional[int] = None
    api_version: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ValidationResponse":
        """Create a ValidationResponse from API response data."""
        return cls(
            success=data["success"],
            data=ValidationResult.from_dict(data["data"]),
            credits_used=data["creditsUsed"],
            remaining_credits=data["remainingCredits"],
            validation_duration=data.get("validationDuration"),
            api_version=data.get("meta", {}).get("apiVersion"),
        )


@dataclass
class BulkValidationResult:
    """
    Validation result for a single email in bulk validation.

    Attributes:
        email: The validated email address
        is_valid: Overall validation status
        disposable: Whether the email is from a disposable provider
        role_account: Whether the email is a role-based account
        free_provider: Whether the email is from a free provider
        reachable: Reachability status
        syntax: Syntax validation details
        error: Error message if validation failed
    """

    email: str
    is_valid: bool
    disposable: bool
    role_account: bool
    free_provider: bool
    reachable: str
    syntax: Optional[SyntaxValidation] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkValidationResult":
        """Create a BulkValidationResult from API response data."""
        return cls(
            email=data["email"],
            is_valid=data["isValid"],
            disposable=data.get("disposable", False),
            role_account=data.get("roleAccount", False),
            free_provider=data.get("freeProvider", False),
            reachable=data.get("reachability", "unknown"),  # API uses 'reachability' not 'reachable'
            syntax=SyntaxValidation(**data["syntax"]) if data.get("syntax") else None,
            error=data.get("error"),
        )


@dataclass
class BulkValidationSummary:
    """Summary statistics for bulk validation."""

    total: int
    duplicates_removed: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkValidationSummary":
        """Create a BulkValidationSummary from API response data."""
        return cls(
            total=data["total"],
            duplicates_removed=data.get("duplicatesRemoved", 0),
        )


@dataclass
class BulkValidationResponse:
    """
    Response from bulk email validation.

    Attributes:
        success: Whether the request was successful
        results: List of validation results
        summary: Summary statistics
        credits_used: Number of credits consumed
        remaining_credits: Remaining account credits
        duration: Time taken for validation in milliseconds
        api_version: API version used
    """

    success: bool
    results: List[BulkValidationResult]
    summary: BulkValidationSummary
    credits_used: int
    remaining_credits: int
    duration: Optional[int] = None
    api_version: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BulkValidationResponse":
        """Create a BulkValidationResponse from API response data."""
        return cls(
            success=data["success"],
            results=[
                BulkValidationResult.from_dict(result)
                for result in data["data"]["results"]
            ],
            summary=BulkValidationSummary.from_dict(data["data"]["summary"]),
            credits_used=data["creditsUsed"],
            remaining_credits=data["remainingCredits"],
            duration=data.get("duration"),
            api_version=data.get("meta", {}).get("apiVersion"),
        )
