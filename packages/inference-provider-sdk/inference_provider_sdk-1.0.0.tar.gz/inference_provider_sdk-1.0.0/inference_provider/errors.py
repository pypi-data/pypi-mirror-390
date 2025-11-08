"""
Custom error classes for Inference Provider SDK
"""

from typing import Any, Dict, Optional


class InferenceProviderError(Exception):
    """Base error class for all SDK errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        details: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message}: {self.details}"
        return self.message


class AuthenticationError(InferenceProviderError):
    """Authentication error (401)"""

    def __init__(self, message: str = "Authentication failed", details: Optional[str] = None) -> None:
        super().__init__(message, 401, details)


class ValidationError(InferenceProviderError):
    """Validation error (400)"""

    def __init__(
        self, message: str, field: Optional[str] = None, details: Optional[str] = None
    ) -> None:
        super().__init__(message, 400, details)
        self.field = field


class NotFoundError(InferenceProviderError):
    """Not found error (404)"""

    def __init__(
        self,
        message: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        super().__init__(message, 404, details)
        self.resource_type = resource_type
        self.resource_id = resource_id


class RateLimitError(InferenceProviderError):
    """Rate limit error (429)"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        current_count: Optional[int] = None,
        limit_count: Optional[int] = None,
        reset_time: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        super().__init__(message, 429, details)
        self.current_count = current_count
        self.limit_count = limit_count
        self.reset_time = reset_time


class APIError(InferenceProviderError):
    """API error (500)"""

    def __init__(
        self, message: str = "API request failed", status_code: int = 500, details: Optional[str] = None
    ) -> None:
        super().__init__(message, status_code, details)


class NetworkError(InferenceProviderError):
    """Network error"""

    def __init__(self, message: str = "Network request failed", cause: Optional[Exception] = None) -> None:
        super().__init__(message, None, str(cause) if cause else None)
        self.cause = cause


class ConfigurationError(InferenceProviderError):
    """Configuration error"""

    def __init__(self, message: str, details: Optional[str] = None) -> None:
        super().__init__(message, None, details)


def create_error_from_response(
    status_code: int, data: Dict[str, Any], default_message: str = "API request failed"
) -> InferenceProviderError:
    """Create appropriate error from API response"""
    message = data.get("error") or data.get("message") or default_message
    details = data.get("details")

    if status_code == 400:
        return ValidationError(message, details=details)
    elif status_code == 401:
        return AuthenticationError(message, details)
    elif status_code == 404:
        return NotFoundError(message, details=details)
    elif status_code == 429:
        return RateLimitError(
            message,
            data.get("current_count"),
            data.get("limit_count"),
            data.get("reset_time"),
            details,
        )
    elif status_code in (500, 502, 503, 504):
        return APIError(message, status_code, details)
    else:
        return InferenceProviderError(message, status_code, details)
