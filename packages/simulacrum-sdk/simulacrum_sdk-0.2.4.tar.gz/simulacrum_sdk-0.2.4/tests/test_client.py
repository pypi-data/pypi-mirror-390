import os
import sys

# Ensure package import works when running tests directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import numpy as np

from pydantic import ValidationError

import simulacrum.client as simulacrum_client


@pytest.fixture
def client():
    base_url = os.environ["TEST_API"]
    api_key = os.environ["TEST_KEY"]
    return simulacrum_client.Simulacrum(api_key, base_url=base_url)


def test_client_initializes_expected_headers(client):
    assert client.headers["Authorization"] == f"Bearer {client.api_key}"
    assert client.headers["Content-Type"] == "application/json"


def test_validate_invokes_send_request_and_parses_response(client, monkeypatch):
    captured = {}

    def fake_send_request(method, url, headers, json):
        captured["method"] = method
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return {
            "valid": True,
            "client": "client-123",
            "expires_at": "2024-01-01T00:00:00Z",
        }

    monkeypatch.setattr(simulacrum_client, "send_request", fake_send_request)

    response = client.validate()

    assert captured == {
        "method": "GET",
        "url": f"{client.base_url}/tempo/v1/validate",
        "headers": client.headers,
        "json": None,
    }
    assert response.valid is True
    assert response.client == "client-123"


def test_forecast_builds_payload_and_returns_numpy_array(client, monkeypatch):
    captured_payload = {}

    class DummyRequest:
        def __init__(self, *, series, horizon, model):
            captured_payload["series"] = (
                series.tolist() if hasattr(series, "tolist") else series
            )
            captured_payload["horizon"] = horizon
            captured_payload["model"] = model

        def model_dump(self, *args, **kwargs):
            return {
                "series": captured_payload["series"],
                "horizon": captured_payload["horizon"],
                "model": captured_payload["model"],
            }

    def fake_send_request(method, url, headers, json):
        captured_payload["method"] = method
        captured_payload["url"] = url
        captured_payload["headers"] = headers
        captured_payload["json"] = json
        return {
            "forecast": [3.1, 3.9],
            "model_used": "prophet",
        }

    monkeypatch.setattr(simulacrum_client, "ForecastRequest", DummyRequest)
    monkeypatch.setattr(simulacrum_client, "send_request", fake_send_request)

    series = np.array([1.0, 2.0, 3.0])

    forecast = client.forecast(series=series, horizon=2, model="prophet")

    assert captured_payload["series"] == [1.0, 2.0, 3.0]
    assert captured_payload["horizon"] == 2
    assert captured_payload["model"] == "prophet"
    assert captured_payload["method"] == "POST"
    assert captured_payload["url"] == f"{client.base_url}/prophet/v1/forecast"
    assert captured_payload["headers"] == client.headers
    assert captured_payload["json"] == {
        "series": [1.0, 2.0, 3.0],
        "horizon": 2,
        "model": "prophet",
    }
    assert isinstance(forecast, np.ndarray)
    assert np.allclose(forecast, np.array([3.1, 3.9]))


def test_forecast_rejects_non_numeric_series(client):
    with pytest.raises(TypeError):
        client.forecast(series=["a", "b"], horizon=2, model="default")


def test_forecast_rejects_multidimensional_input(client):
    with pytest.raises(ValueError):
        client.forecast(series=[[1.0, 2.0], [3.0, 4.0]], horizon=2, model="default")


def test_forecast_rejects_non_integer_horizon(client):
    with pytest.raises(ValidationError):
        client.forecast(series=[1.0, 2.0], horizon="two", model="default")


def test_client_requires_string_api_key():
    with pytest.raises(TypeError):
        simulacrum_client.Simulacrum(api_key=None)  # type: ignore[arg-type]
