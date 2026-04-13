import json
import time
import requests
from stockpulse import config


def fetch_daily_data(ticker: str, use_cache: bool = True) -> dict:
    """
    Fetch daily time series data for a ticker from Alpha Vantage.
    Returns the raw JSON response as a dict — from cache if available,
    otherwise from the API (saving to cache before returning).
    """
    ticker = ticker.upper()
    cache_path = config.CACHE_DIR / f"{ticker}.json"

    # --- Cache check ---
    if use_cache and cache_path.is_file():
        print(f"[cache hit]  {ticker} — loading from {cache_path}")
        with open(cache_path, "r") as f:
            return json.load(f)

    print(f"[cache miss] {ticker} — fetching from API")

    # --- Build API request ---
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "outputsize": "compact",
        "datatype": "json",
        "apikey": config.API_KEY,
    }

    # --- Make the API call ---
    try:
        response = requests.get(config.BASE_URL, params=params, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise RuntimeError(f"Request timed out for ticker '{ticker}'.")
    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error for ticker '{ticker}': {e}")
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error for ticker '{ticker}': {e}")

    data = response.json()

    # --- Alpha Vantage-specific error checking ---
    if "Note" in data:
        raise RuntimeError(
            f"Alpha Vantage rate limit hit for '{ticker}'. "
            f"API message: {data['Note']}"
        )

    if "Information" in data:
        raise RuntimeError(
            f"Alpha Vantage returned an error for '{ticker}'. "
            f"API message: {data['Information']}"
        )

    if "Time Series (Daily)" not in data:
        raise RuntimeError(
            f"Unexpected response structure for '{ticker}'. "
            f"Keys found: {list(data.keys())}"
        )

    # --- Save to cache ---
    with open(cache_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"[saved]      {ticker} → {cache_path}")

    time.sleep(config.API_CALL_DELAY)

    return data


# --- Test API calls and caching ---
if __name__ == "__main__":
    import pprint

    TEST_TICKER = "TSLA"

    print("=" * 50)
    print(f"RUN 1 — expecting a cache miss for {TEST_TICKER}")
    print("=" * 50)
    data = fetch_daily_data(TEST_TICKER)
    meta = data.get("Meta Data", {})
    print(f"Meta Data: {pprint.pformat(meta)}")
    print(f"Top-level keys: {list(data.keys())}")

    print()
    print("=" * 50)
    print(f"RUN 2 — expecting a cache hit for {TEST_TICKER}")
    print("=" * 50)
    data_cached = fetch_daily_data(TEST_TICKER)
    print(f"Top-level keys: {list(data_cached.keys())}")
    print("Both runs returned same data:", data == data_cached)
