"""Low-level HTTP helpers used by the Simulacrum client."""

from typing import Any, Dict, Mapping, Optional

import uuid
import httpx

from simulacrum._errors import parse_error


def _infer_service_from_url(url: str) -> str:
    lowered = url.lower()
    if "/onsiteiq/" in lowered:
        return "onsiteiq"
    if "/tempo/" in lowered:
        return "tempo"
    return "tempo"


def send_request(method: str, url: str, headers: Mapping[str, str], json: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    """Execute an HTTP request against the Simulacrum API and raise rich typed errors on failure.

    Args:
        method (str): HTTP method to invoke ("GET", "POST", ...).
        url (str): Fully-qualified endpoint URL.
        headers (Mapping[str, str]): HTTP headers that include authorization and content type.
        json (Mapping[str, Any] | None): JSON-serialisable payload for the request body.

    Returns:
        dict[str, Any]: Parsed JSON payload returned by the API.
    """
    # Ensure we always send an X-Request-ID
    merged_headers: Dict[str, str] = dict(headers)
    merged_headers.setdefault("X-Request-ID", str(uuid.uuid4()))

    with httpx.Client(timeout=30) as client:
        response = client.request(method=method, url=url, headers=merged_headers, json=json)

    if 200 <= response.status_code < 300:
        # Let JSON decode errors propagate as ValueError to be consistent with prior behavior
        return response.json()  # type: ignore[return-value]

    service = _infer_service_from_url(url)
    endpoint = httpx.URL(url).path
    raise parse_error(response, service=service, endpoint=endpoint)
