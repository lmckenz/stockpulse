# parser.py


def parse_daily_data(raw_json):
    """
    Parse a raw Alpha Vantage TIME_SERIES_DAILY JSON response into a clean,
    sorted list of daily price dicts.

    Args:
        raw_json (dict): The full JSON response dict returned by client.py.

    Returns:
        list[dict]: Sorted list (ascending by date) of dicts with keys:
                    date (str), open (float), high (float), low (float),
                    close (float), volume (int)

    Raises:
        KeyError: If expected top-level or per-entry keys are missing.
        ValueError: If type coercion fails on a price or volume value.
    """
    TIME_SERIES_KEY = "Time Series (Daily)"

    # --- Validate top-level structure ---
    if TIME_SERIES_KEY not in raw_json:
        available_keys = list(raw_json.keys())
        raise KeyError(
            f"Expected key '{TIME_SERIES_KEY}' not found in API response. "
            f"Keys present: {available_keys}. "
            f"If you see 'Note' or 'Information', the API may have returned "
            f"a rate limit or error message."
        )

    time_series = raw_json[TIME_SERIES_KEY]

    # --- Map clean output names to Alpha Vantage's prefixed key names ---
    FIELD_MAP = {
        "open":   "1. open",
        "high":   "2. high",
        "low":    "3. low",
        "close":  "4. close",
        "volume": "5. volume",
    }

    parsed_entries = []

    for date_str, daily_values in time_series.items():

        # Validate all expected fields are present for this entry
        for clean_name, raw_key in FIELD_MAP.items():
            if raw_key not in daily_values:
                raise KeyError(
                    f"Missing expected field '{raw_key}' ('{clean_name}') "
                    f"for date '{date_str}'. "
                    f"Fields present: {list(daily_values.keys())}"
                )

        # Coerce all values to their correct types
        try:
            entry = {
                "date":   date_str,
                "open":   float(daily_values["1. open"]),
                "high":   float(daily_values["2. high"]),
                "low":    float(daily_values["3. low"]),
                "close":  float(daily_values["4. close"]),
                "volume": int(daily_values["5. volume"]),
            }
        except ValueError as e:
            raise ValueError(
                f"Type coercion failed for date '{date_str}': {e}. "
                f"Raw values: {daily_values}"
            )

        parsed_entries.append(entry)

    # Sort ascending by date (ISO 8601 strings sort lexicographically = chronologically)
    parsed_entries.sort(key=lambda entry: entry["date"])

    return parsed_entries


# --- Standalone test ---
if __name__ == "__main__":
    import json
    import os
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from stockpulse.config import CACHE_DIR

    # List available cached files so the developer can pick one
    cached_files = [f for f in os.listdir(CACHE_DIR) if f.endswith(".json")]
    if not cached_files:
        print("No cached files found in cache/. Run client.py first to fetch data.")
        exit(1)

    # Use the first cached file found
    test_file = cached_files[0]
    ticker = test_file.replace(".json", "")
    cache_path = os.path.join(CACHE_DIR, test_file)

    print(f"Loading cached data for: {ticker}")
    print(f"File: {cache_path}\n")

    with open(cache_path, "r") as f:
        raw_json = json.load(f)

    parsed = parse_daily_data(raw_json)

    print(f"Total entries parsed: {len(parsed)}\n")

    print("--- First 5 entries ---")
    for entry in parsed[:5]:
        print(entry)

    print("\n--- Last 5 entries ---")
    for entry in parsed[-5:]:
        print(entry)

    print("\n--- Type checks on first entry ---")
    first = parsed[0]
    for key, value in first.items():
        print(f"  {key}: {value!r}  →  {type(value).__name__}")
