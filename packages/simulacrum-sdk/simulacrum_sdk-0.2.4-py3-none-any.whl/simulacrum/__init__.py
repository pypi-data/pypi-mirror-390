"""Simulacrum SDK public interface.

This package exposes the primary client you will use to interact with the
Simulacrum forecasting API.

Example:
    >>> from simulacrum import Simulacrum
    >>> client = Simulacrum(api_key="sp_your_api_key")
    >>> forecast = client.forecast(series=[1.0, 1.5, 2.0], horizon=3, model="default")
"""

from .client import Simulacrum

__all__ = ["Simulacrum", "__version__"]
__version__: str = "0.1.0"
