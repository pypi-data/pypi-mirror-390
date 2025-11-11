"""Custom exceptions raised by the Simulacrum SDK.

This module defines a rich, typed hierarchy aligned with Simulacrum services' ErrorEnvelope
and preserves backward compatibility with previously exported exception names.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Type


class SimulacrumError(Exception):
    """Base exception for all SDK errors with structured fields."""

    def __init__(
        self,
        *,
        service: str,
        endpoint: str,
        status_code: int,
        error_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        trace_id_body: Optional[str] = None,
        request_id_header: Optional[str] = None,
        response: Any = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.service = service
        self.endpoint = endpoint
        self.status_code = status_code
        self.error_type = error_type
        self.message = message
        self.details = details
        self.trace_id_body = trace_id_body
        self.request_id_header = request_id_header
        self.response = response
        self.context = context or {}

    def trace_id(self) -> Optional[str]:
        return self.trace_id_body or self.request_id_header

    def __str__(self) -> str:
        tid = self.trace_id()
        tid_str = f" trace_id={tid}" if tid else ""
        return f"[{self.service}] {self.status_code} {self.error_type}: {self.message}{tid_str}"


class UnauthorizedError(SimulacrumError):
    pass


class ForbiddenError(SimulacrumError):
    pass


class NotFoundError(SimulacrumError):
    pass


class ConflictError(SimulacrumError):
    pass


class ValidationError(SimulacrumError):
    pass


class RateLimitError(SimulacrumError):
    def __init__(
        self, *args, retry_after_seconds: Optional[float] = None, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.retry_after_seconds = retry_after_seconds


class ServerError(SimulacrumError):
    pass


class HTTPClientError(SimulacrumError):
    pass


# Backward compatibility aliases/classes
class AuthError(UnauthorizedError):
    """Raised when authentication with the API fails (back-compat)."""


class ApiKeyExpiredError(ForbiddenError):
    """Raised when the API key has expired (back-compat)."""


class ApiKeyInactiveError(ForbiddenError):
    """Raised when the API key has been deactivated (back-compat)."""


class ApiKeyInvalidError(UnauthorizedError):
    """Raised when the API key is not recognised (back-compat)."""


class ForecastAlreadyRunningError(ConflictError):
    """Raised when a forecast job is already in progress (back-compat)."""


class InvalidRequestError(ValidationError):
    """Raised when the request payload is malformed (back-compat)."""


class QuotaExceededError(RateLimitError):
    """Raised when the API usage quota has been exhausted (back-compat)."""


class ApiError(HTTPClientError):
    """Catch-all for unclassified API errors (back-compat)."""


ERROR_CODE_MAP: Dict[str, Type[SimulacrumError]] = {
    "API_KEY_EXPIRED": ApiKeyExpiredError,
    "API_KEY_INVALID": ApiKeyInvalidError,
    "API_KEY_INACTIVE": ApiKeyInactiveError,
    "API_USAGE_LIMIT": QuotaExceededError,
    "REQUEST_INVALID": InvalidRequestError,
    "FORECAST_ALREADY_RUNNING": ForecastAlreadyRunningError,
}
