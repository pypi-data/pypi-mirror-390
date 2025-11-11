from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from .exceptions import (
    ConflictError,
    ForbiddenError,
    HTTPClientError,
    NotFoundError,
    RateLimitError,
    ServerError,
    SimulacrumError,
    UnauthorizedError,
    ValidationError,
)


def _parse_retry_after(value: str) -> Optional[float]:
    try:
        return float(value)
    except Exception:
        try:
            dt = datetime.strptime(value, "%a, %d %b %Y %H:%M:%S %Z")
            return max(
                0.0,
                (dt.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)).total_seconds(),
            )
        except Exception:
            return None


def parse_error(response, *, service: str, endpoint: str) -> SimulacrumError:
    status = getattr(response, "status_code")
    headers = getattr(response, "headers", {}) or {}
    req_id = headers.get("X-Request-ID")

    error_type = "http_error"
    message = f"HTTP {status}"
    details = None
    trace_id = None

    # Try parse JSON body according to ErrorEnvelope
    try:
        data = response.json()
        err = (data or {}).get("error") or {}
        error_type = str(err.get("type") or error_type)
        message = str(err.get("message") or message)
        details = err.get("details")
        trace_id = (data or {}).get("trace_id")
    except Exception:
        try:
            text = response.text
        except Exception:
            text = None
        if text:
            message = str(text).strip()[:500]

    common = dict(
        service=service,
        endpoint=endpoint,
        status_code=status,
        error_type=error_type,
        message=message,
        details=details,
        trace_id_body=trace_id,
        request_id_header=req_id,
        response=response,
    )

    if status == 401:
        return UnauthorizedError(**common)
    if status == 403:
        return ForbiddenError(**common)
    if status == 404:
        return NotFoundError(**common)
    if status == 409:
        return ConflictError(**common)
    if status in (400, 422):
        return ValidationError(**common)
    if status == 429:
        ra = headers.get("Retry-After")
        return RateLimitError(**common, retry_after_seconds=_parse_retry_after(ra) if ra else None)
    if 500 <= status <= 599:
        return ServerError(**common)
    if 400 <= status <= 499:
        return HTTPClientError(**common)
    return HTTPClientError(**common)


def is_retryable(exc: SimulacrumError) -> bool:
    return exc.status_code in {429, 500, 502, 503, 504}


def retry_after(exc: RateLimitError) -> Optional[float]:
    return getattr(exc, "retry_after_seconds", None)


def extract_trace_id(exc: SimulacrumError) -> Optional[str]:
    return exc.trace_id()


