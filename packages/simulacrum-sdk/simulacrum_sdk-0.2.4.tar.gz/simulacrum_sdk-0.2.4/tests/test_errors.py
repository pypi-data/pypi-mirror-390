import json
import os
import sys

# Ensure package import works when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime, timedelta, timezone

from simulacrum._errors import parse_error
from simulacrum.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    UnauthorizedError,
    ValidationError,
)


class DummyResponse:
    def __init__(self, *, status_code: int, headers: dict | None = None, body: object | None = None, text: str | None = None):
        self.status_code = status_code
        self.headers = headers or {}
        self._body = body
        self._text = text

    def json(self):
        if self._body is None:
            raise ValueError("no json body")
        return self._body

    @property
    def text(self):
        if self._text is not None:
            return self._text
        return json.dumps(self._body) if self._body is not None else ""


def mk_envelope(error_type: str, message: str, details: dict | None = None, trace_id: str | None = "t-123"):
    return {
        "error": {"type": error_type, "message": message, "details": details},
        "trace_id": trace_id,
    }


def test_401_unauthorized_json_and_plain_text():
    r1 = DummyResponse(status_code=401, headers={"X-Request-ID": "abc"}, body=mk_envelope("unauthorized", "bad key"))
    exc = parse_error(r1, service="tempo", endpoint="/v1/validate")
    assert isinstance(exc, UnauthorizedError)
    assert exc.trace_id() in {"t-123", "abc"}

    r2 = DummyResponse(status_code=401, headers={}, body=None, text="Unauthorized")
    exc2 = parse_error(r2, service="tempo", endpoint="/v1/validate")
    assert isinstance(exc2, UnauthorizedError)


def test_403_forbidden_variations():
    r = DummyResponse(status_code=403, headers={}, body=mk_envelope("forbidden", "revoked"))
    exc = parse_error(r, service="tempo", endpoint="/v1/validate")
    assert isinstance(exc, ForbiddenError)


def test_422_and_400_validation_details_list():
    details = {"problems": [
        {"field": "series[5]", "message": "invalid value"},
        {"field": "horizon", "message": "too large"},
    ]}
    r = DummyResponse(status_code=422, headers={}, body=mk_envelope("validation_error", "schema error", details))
    exc = parse_error(r, service="tempo", endpoint="/v1/forecast")
    assert isinstance(exc, ValidationError)
    s = str(exc)
    assert "validation_error" in s and "schema error" in s


def test_400_domain_validation_details_specific_keys():
    details = {"invalid_index": 7, "invalid_value": -1}
    r = DummyResponse(status_code=400, headers={}, body=mk_envelope("validation_error", "domain error", details))
    exc = parse_error(r, service="tempo", endpoint="/v1/forecast")
    assert isinstance(exc, ValidationError)


def test_404_and_409_mapping():
    r404 = DummyResponse(status_code=404, headers={}, body=mk_envelope("http_error", "not found"))
    r409 = DummyResponse(status_code=409, headers={}, body=mk_envelope("http_error", "conflict"))
    assert isinstance(parse_error(r404, service="tempo", endpoint="/x"), NotFoundError)
    assert isinstance(parse_error(r409, service="tempo", endpoint="/x"), ConflictError)


def test_429_retry_after_seconds_and_date():
    r = DummyResponse(status_code=429, headers={"Retry-After": "30"}, body=mk_envelope("rate_limit", "slow down"))
    exc = parse_error(r, service="tempo", endpoint="/v1/forecast")
    assert isinstance(exc, RateLimitError)
    assert exc.retry_after_seconds == 30.0

    http_date = (datetime.now(timezone.utc) + timedelta(seconds=45)).strftime("%a, %d %b %Y %H:%M:%S %Z")
    r2 = DummyResponse(status_code=429, headers={"Retry-After": http_date}, body=mk_envelope("rate_limit", "slow down"))
    exc2 = parse_error(r2, service="tempo", endpoint="/v1/forecast")
    assert isinstance(exc2, RateLimitError)
    assert exc2.retry_after_seconds is not None and exc2.retry_after_seconds >= 0.0


def test_500_server_error_json_and_plain():
    r1 = DummyResponse(status_code=500, headers={}, body=mk_envelope("internal_error", "boom"))
    r2 = DummyResponse(status_code=500, headers={}, body=None, text="internal error")
    assert isinstance(parse_error(r1, service="tempo", endpoint="/x"), ServerError)
    assert isinstance(parse_error(r2, service="tempo", endpoint="/x"), ServerError)


def test_trace_id_from_body_or_header_and_str_formatting():
    r = DummyResponse(status_code=401, headers={"X-Request-ID": "rid-1"}, body=mk_envelope("unauthorized", "bad key", trace_id=None))
    exc = parse_error(r, service="onsiteiq", endpoint="/v1/validate")
    assert exc.trace_id() == "rid-1"
    s = str(exc)
    assert "[onsiteiq]" in s and "401 unauthorized".split()[1] in s.lower()


