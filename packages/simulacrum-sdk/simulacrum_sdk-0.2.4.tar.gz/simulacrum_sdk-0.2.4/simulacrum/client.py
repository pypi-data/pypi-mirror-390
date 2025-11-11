"""High-level client for interacting with the Simulacrum forecasting API."""

from typing import Any, Dict, Sequence

import numpy as np

from simulacrum.api import send_request
from simulacrum.config import BASE_URL
from simulacrum.exceptions import ApiError, AuthError
from simulacrum.models import ForecastRequest, ForecastResponse, ValidateAPIKeyResponse


class Simulacrum:
    """Client wrapper around Simulacrum's REST API.

    Example:
        >>> from simulacrum import Simulacrum
        >>> client = Simulacrum(api_key="sp_example_key")
        >>> forecast = client.forecast(series=[1.0, 1.1, 1.2], horizon=2, model="default")
        >>> forecast.shape
        (2,)
    """

    def __init__(self, api_key: str, base_url: str = BASE_URL) -> None:
        """Create a client that can issue authenticated requests to Simulacrum.

        Args:
            api_key (str): Simulacrum API key that authorizes requests.
            base_url (str): Base URL for the API; defaults to the production endpoint.
        """
        if not isinstance(api_key, str) or not api_key.strip():
            raise TypeError("api_key must be a non-empty string.")
        if not isinstance(base_url, str) or not base_url.strip():
            raise TypeError("base_url must be a non-empty string.")

        self.api_key: str = api_key
        self.base_url: str = base_url
        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def forecast(
        self, series: Sequence[float] | np.ndarray, horizon: int | None = None, model: str = "default"
    ) -> np.ndarray:
        """Request a forecast for the provided time series.

        Args:
            series (Sequence[float] | numpy.ndarray): One-dimensional historical observations used as
                forecast input.
            horizon (int): Number of future periods to predict.
            model (str): Identifier of the forecasting model, for example ``"default"``.

        Returns:
            numpy.ndarray: Array containing the forecasted values in chronological order.

        Raises:
            TypeError: ``series`` is not a numpy array or sequence of numeric values.
            ValueError: ``series`` is a numpy array or sequence with dimensionality other than one.
            ApiError: The API returned an error response.
            AuthError: Authentication failed for the provided API key.
        """
        if isinstance(series, np.ndarray):
            if series.ndim != 1:
                raise ValueError("series must be a one-dimensional numpy array.")
            series_to_send = series.astype(float)
        elif isinstance(series, Sequence):
            if isinstance(series, (str, bytes)):
                raise TypeError(
                    "series must be a one-dimensional numpy array or sequence of floats."
                )
            try:
                series_to_send = np.asarray(list(series), dtype=float)
            except (TypeError, ValueError) as exc:
                raise TypeError(
                    "series must be a one-dimensional numpy array or sequence of floats."
                ) from exc
            if series_to_send.ndim != 1:
                raise ValueError("series must be one-dimensional.")
        else:
            raise TypeError(
                "series must be a one-dimensional numpy array or sequence of floats."
            )

        payload: ForecastRequest = ForecastRequest(
            series=series_to_send, horizon=horizon, model=model
        )
        request_body: Dict[str, Any] = payload.model_dump()
        # Exclude optional fields that are None (e.g., horizon for onsiteiq)
        request_body = payload.model_dump(exclude_none=True)
        response_data: Dict[str, Any] = send_request(
            method="POST",
            url=f"{self.base_url}/{model}/v1/forecast",
            headers=self.headers,
            json=request_body,
        )
        validated_response: ForecastResponse = ForecastResponse.model_validate(
            response_data
        )
        return validated_response.get_forecast()

    def validate(self, model: str = "tempo") -> ValidateAPIKeyResponse:
        """Validate the configured API key and return its metadata.

        Returns:
            ValidateAPIKeyResponse: Structured validation details including key status and expiration date.

        Raises:
            AuthError: The API key is invalid or unauthorized.
            ApiError: An unexpected API error occurred.

        Example:
            >>> client = Simulacrum(api_key="sp_example_key")
            >>> validation = client.validate()
            >>> validation.valid
            True
        """
        response_data: Dict[str, Any] = send_request(
            method="GET",
            url=f"{self.base_url}/{model}/v1/validate",
            headers=self.headers,
            json=None,
        )

        return ValidateAPIKeyResponse.model_validate(response_data)
