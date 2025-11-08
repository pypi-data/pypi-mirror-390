"""
Custom exception classes for the memofai SDK.

This module defines all custom exceptions used throughout the SDK,
providing detailed error information and type-safe error handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from .types import MoaErrorResponse, ValidationErrorDetail


class ApiError(Exception):
    """Base exception for all API errors."""

    def __init__(self, message: str, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__(message)
        self.status = status
        self.status_text = status_text
        self.response = response
        self.timestamp = datetime.utcnow().isoformat()

    def is_subscription_error(self) -> bool:
        """Check if this is a subscription-related error."""
        return self.response.error_type in ["subscription_required", "subscription_expired"]

    def get_resource_type(self) -> Optional[str]:
        """Get the resource type that caused the limit error (if applicable)."""
        return self.response.resource_type

    def get_limit(self) -> Optional[int]:
        """Get the limit value (if applicable)."""
        return self.response.limit

    def get_current_usage(self) -> Optional[int]:
        """Get the current usage (if applicable)."""
        return self.response.current_usage


class ValidationError(ApiError):
    """Exception raised when request validation fails."""

    def __init__(self, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__("Validation failed", status, status_text, response)
        self.validation_errors = self._parse_validation_errors(response)

    def _parse_validation_errors(self, response: MoaErrorResponse) -> List[ValidationErrorDetail]:
        """Parse validation errors from the response."""
        errors: List[ValidationErrorDetail] = []

        # Check detail field
        if response.detail:
            errors.append(ValidationErrorDetail(field="general", message=response.detail))

        # Check extra fields
        for field, message in response.extra.items():
            if isinstance(message, list):
                for msg in message:
                    errors.append(ValidationErrorDetail(field=field, message=str(msg)))
            elif isinstance(message, str):
                errors.append(ValidationErrorDetail(field=field, message=message))

        return errors


class AuthenticationError(ApiError):
    """Exception raised when authentication fails."""

    def __init__(self, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__("Authentication required", status, status_text, response)


class AuthorizationError(ApiError):
    """Exception raised when authorization fails."""

    def __init__(self, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__("Permission denied", status, status_text, response)


class NotFoundError(ApiError):
    """Exception raised when a resource is not found."""

    def __init__(self, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__("Resource not found", status, status_text, response)


class ServiceUnavailableError(ApiError):
    """Exception raised when the service is unavailable."""

    def __init__(self, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__("Service temporarily unavailable", status, status_text, response)


class RequestLimitError(ApiError):
    """Exception raised when request limit is exceeded."""

    def __init__(self, status: int, status_text: str, response: MoaErrorResponse):
        super().__init__("Monthly request limit exceeded", status, status_text, response)


class NetworkError(Exception):
    """Exception raised when a network error occurs."""

    def __init__(self, message: str, original_error: Exception):
        super().__init__(message)
        self.original_error = original_error
