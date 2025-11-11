![Simulacrum Logo](https://github.com/Smlcrm/assets/blob/main/Asset%201@4x-8.png?raw=true "Simulacrum SDK")

# Simulacrum SDK

A lightweight Python client for the Simulacrum time-series forecasting API. The SDK wraps Simulacrum's REST endpoints with type-safe models, error handling, and convenience helpers so you can focus on building forecasting workflows instead of wiring HTTP requests.

---

## Features

- 🔐 **Authenticated client** with automatic bearer-token headers
- 📈 **Forecast API wrapper** that serialises NumPy arrays transparently
- ✅ **API key validation** to inspect key status, client ID, and expiry
- 🚫 **Rich exceptions** that map Simulacrum error codes to Python types
- 🧪 **Tested models** built on Pydantic for strict data validation

---

## Installation

### From PyPI (recommended)

> Requires Python 3.8 or newer

```bash
pip install simulacrum-sdk
```

### From GitHub source

Install directly from the latest commit on the main repository:

```bash
pip install git+https://github.com/Smlcrm/simulacrum-sdk.git
```

To work with the sources locally for development (Python 3.8+):

```bash
git clone https://github.com/Smlcrm/simulacrum-sdk.git
cd simulacrum-sdk
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -e .[dev]
```

---

## Usage Overview

### Creating a client

```python
from simulacrum import Simulacrum

client = Simulacrum(api_key="sp_your_api_key")
```

If you are running a local version of the Simulacrum API (i.e., on-premise model hosting), override the base URL:

```python
client = Simulacrum(api_key="sp_your_api_key", base_url="https://staging.api.smlcrm.com")
```

### Validating an API key

Your forecast requests will fail if your API key is invalid. To check your API key is valid run the following.

```python
validation = client.validate()
print("Valid:", validation.valid)
print("Client ID:", validation.client)
```

### Requesting a forecast

```python
import numpy as np

series = np.array([102.4, 106.0, 108.3, 111.9])
forecast = client.forecast(series=series, horizon=3, model="default")

print("Next periods:", forecast)
```

The SDK returns a `numpy.ndarray` so you can pipe results into downstream analytics or visualisations immediately.



### Handling errors

All API error codes are mapped to dedicated exceptions. Catch them to distinguish between authentication, quota, and request issues:

```python
from simulacrum.exceptions import AuthError, QuotaExceededError, SimulacrumError

try:
    client.forecast(series=[1, 2, 3], horizon=5, model="default")
except AuthError:
    print("Check that your API key is correct and active.")
except QuotaExceededError:
    print("You have reached your usage limit for the current period.")
except SimulacrumError as exc:
    print(f"Unhandled Simulacrum error: {exc}")
```

---

## Tutorial: Forecast a Time Series in Five Steps

1. **Install the SDK**
    ```bash
    pip install simulacrum-sdk
    ```

2. **Create a project structure**
    ```bash
    mkdir simulacrum-sample && cd simulacrum-sample
    python -m venv .venv
    source .venv/bin/activate
    pip install simulacrum-sdk
    ```

3. **Write a forecast script (`forecast_example.py`)**
    ```python
    from simulacrum import Simulacrum

    def main() -> None:
        client = Simulacrum(api_key="sp_your_api_key")
        series = [24.5, 25.1, 25.7, 26.2, 26.9]
        forecast = client.forecast(series=series, horizon=3, model="default")
        print("Forecast:", forecast.tolist())

    if __name__ == "__main__":
        main()
    ```

4. **Validate your API key (optional)**
    ```python
    validation = client.validate()
    if validation.valid:
        print("Key is active until", validation.expires_at)
    ```
    
5. **Run the script**
    ```bash
    python forecast_example.py
    ```

This workflow demonstrates the complete loop: initialising the client, requesting a forecast, and checking key status.

---

## Documentation

The public API is intentionally small:

| Component | Description |
|-----------|-------------|
| `simulacrum.Simulacrum` | High-level client exposing `forecast()` and `validate()` methods. |
| `simulacrum.models.ForecastRequest` | Pydantic model ensuring forecast payloads are well-formed. |
| `simulacrum.models.ForecastResponse` | Wraps forecast results and exposes `get_forecast()` to return a `numpy.ndarray`. |
| `simulacrum.models.ValidateAPIKeyResponse` | Validation metadata returned by `Simulacrum.validate()`. |
| `simulacrum.exceptions.*` | Custom error hierarchy mapping Simulacrum error codes to Python exceptions. |

Explore inline docstrings for detailed parameter and return type information. The tests in [`tests/test_client.py`](tests/test_client.py) demonstrate advanced usage patterns and validation behavior.

If you are contributing, run the suite with:

```bash
pip install -e .[dev]
python -m pytest
```

---

## License

MIT © Simulacrum, Inc.
