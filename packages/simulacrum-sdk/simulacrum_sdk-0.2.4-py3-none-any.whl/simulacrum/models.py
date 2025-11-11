"""Data models that map request and response payloads for the Simulacrum API."""

from datetime import datetime
from typing import List, Optional, Sequence, Union

import numpy as np
from pydantic import BaseModel, field_validator, model_validator


class ForecastRequest(BaseModel):
    """Payload submitted to the Simulacrum forecast endpoint.

    Attributes:
        series (list[float]): Historical observations used as forecast input.
        horizon (int | None): Number of future periods to predict. Optional for the ``"onsiteiq"`` model.
        model (str | None): Identifier of the forecasting model, defaults to ``"default"``.

    Example:
        >>> from simulacrum.models import ForecastRequest
        >>> payload = ForecastRequest(series=[1.0, 2.0, 3.0], horizon=2, model="default")
        >>> payload.model_dump()
        {'series': [1.0, 2.0, 3.0], 'horizon': 2, 'model': 'default'}
    """

    # TODO: It must be List[List[float]] (num_steps, num_series) remove after refactoring
    series: Union[List[float], List[List[float]]]
    horizon: Optional[int] = None
    model: Optional[str] = "default"

    @field_validator("series", mode="before")
    @classmethod
    def _ensure_series_list(cls, value: Union[np.ndarray, Sequence[float]]) -> List[float]:  # type: ignore[override]
        """Normalise the series field to ``list[float]``.

        Args:
            value (numpy.ndarray | Sequence[float]): Incoming value from caller.

        Returns:
            list[float]: Serialisable list of floats.
        """
        if isinstance(value, np.ndarray):
            return value.astype(float).tolist()
        return list(value)

    @model_validator(mode="after")
    def _validate_horizon_requirement(self):
        # Horizon is required for all models except onsiteiq
        model_name = (self.model or "").lower()
        if model_name != "onsiteiq" and self.horizon is None:
            raise ValueError("horizon is required and must be a positive integer for this model")

        # When provided, horizon must be an integer >= 1
        if self.horizon is not None:
            if not isinstance(self.horizon, int):
                raise ValueError(
                    f"horizon must be an integer (got {type(self.horizon).__name__})"
                )
            if self.horizon < 1:
                raise ValueError("horizon must be >= 1")
        return self


class ForecastResponse(BaseModel):
    """Forecast output returned by the API.

    Attributes:
        forecast (list[float]): Forecasted values returned by the service.
        model_used (str): Identifier of the model the backend selected.

    Example:
        >>> from simulacrum.models import ForecastResponse
        >>> response = ForecastResponse(forecast=[4.2, 4.8], model_used="default")
        >>> response.get_forecast().tolist()
        [4.2, 4.8]
    """

    forecast: Union[List[float], List[List[float]]]

    def get_forecast(self) -> np.ndarray:
        """Return forecast values as a numpy array for downstream processing.

        Returns:
            numpy.ndarray: Forecast data cast to an array of floats.
        """
        return np.array(self.forecast, dtype=float)


class ValidateAPIKeyResponse(BaseModel):
    """Metadata describing the validity of an API key.

    Attributes:
        valid (bool): Indicates whether the API key is currently valid.
        client (str): Identifier of the owning client account.
        expires_at (datetime | None): Expiration timestamp if provided by the API.
    """

    valid: bool
    client: Optional[str] = None
    key_id: Optional[str] = None
    expires_at: Optional[datetime]

    @model_validator(mode="after")
    def _coalesce_client(self):
        # Prefer explicit client; fall back to key_id when provided by API
        if not self.client and self.key_id:
            self.client = self.key_id
        return self
