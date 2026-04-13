import statistics


# ---------------------------------------------------------------------------
# Individual computation functions
# ---------------------------------------------------------------------------

def compute_daily_returns(parsed_entries):
    """
    Compute daily percentage returns from consecutive closing prices.

    Returns a list of (date, return) tuples where the date is the 'to' date
    (i.e. the day the return is attributed to).
    Result length is len(parsed_entries) - 1.
    """
    return [
        (today["date"], (today["close"] - yesterday["close"]) / yesterday["close"])
        for yesterday, today in zip(parsed_entries, parsed_entries[1:])
    ]


def compute_sma(parsed_entries, window):
    """
    Compute simple moving average of closing prices for a given window size.

    Returns a list of (date, sma_value) tuples. The date is the last day in
    each window — i.e. the date the SMA value is 'as of'.
    Result length is len(parsed_entries) - window + 1.
    """
    results = []
    for i in range(len(parsed_entries) - window + 1):
        window_slice = parsed_entries[i : i + window]
        avg = sum(entry["close"] for entry in window_slice) / window
        date = window_slice[-1]["date"]
        results.append((date, avg))
    return results


def compute_volatility(daily_returns):
    """
    Compute volatility as the standard deviation of daily return values.

    Expects daily_returns as a list of (date, return) tuples.
    Returns a single float. Requires at least 2 data points.
    """
    if len(daily_returns) < 2:
        raise ValueError("Need at least 2 daily returns to compute volatility.")
    return_values = [r for _, r in daily_returns]
    return statistics.stdev(return_values)


def compute_cumulative_return(parsed_entries):
    """
    Compute total percentage return from first to last closing price.

    Assumes parsed_entries is sorted ascending by date (guaranteed by parser.py).
    Returns a single float.
    """
    if len(parsed_entries) < 2:
        raise ValueError("Need at least 2 entries to compute cumulative return.")
    initial_close = parsed_entries[0]["close"]
    final_close = parsed_entries[-1]["close"]
    return (final_close - initial_close) / initial_close


def compute_high_low_ranges(parsed_entries):
    """
    Compute the intraday high-low range for each trading day.

    Returns a list of (date, range) tuples sorted by range descending —
    most volatile days appear first.
    """
    ranges = [
        (entry["date"], entry["high"] - entry["low"])
        for entry in parsed_entries
    ]
    return sorted(ranges, key=lambda x: x[1], reverse=True)


def compute_correlation(returns_a, returns_b):
    """
    Compute Pearson correlation coefficient between two daily return series.

    Handles date alignment explicitly: only dates present in both series are
    used. This correctly handles tickers with different trading histories
    (different IPO dates, halts, delistings).

    Both inputs are lists of (date, return) tuples.
    Returns a single float in the range [-1.0, 1.0].
    """
    dict_a = {date: ret for date, ret in returns_a}
    dict_b = {date: ret for date, ret in returns_b}

    shared_dates = sorted(set(dict_a.keys()) & set(dict_b.keys()))

    if len(shared_dates) < 2:
        raise ValueError(
            f"Insufficient shared dates for correlation: found {len(shared_dates)}."
        )

    values_a = [dict_a[d] for d in shared_dates]
    values_b = [dict_b[d] for d in shared_dates]

    return statistics.correlation(values_a, values_b)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_analysis(ticker_data_dict):
    """
    Run the full analysis suite for one or more tickers.

    Args:
        ticker_data_dict: dict of {ticker (str): parsed_entries (list of dicts)}
            Each parsed_entries list must conform to the parser.py contract:
            [{"date": str, "open": float, "high": float, "low": float,
              "close": float, "volume": int}, ...]

    Returns:
        {
            "results": {
                ticker: {
                    "daily_returns":     list of (date, float),
                    "sma_20":            list of (date, float),
                    "sma_50":            list of (date, float),
                    "volatility":        float,
                    "cumulative_return": float,
                    "high_low_ranges":   list of (date, float), sorted desc,
                }
            },
            "correlation_matrix": {
                ticker_a: {ticker_b: float}
            }
        }
    """
    results = {}

    # Pass 1: compute all per-ticker metrics
    for ticker, parsed_entries in ticker_data_dict.items():
        daily_returns = compute_daily_returns(parsed_entries)
        results[ticker] = {
            "daily_returns":     daily_returns,
            "sma_20":            compute_sma(parsed_entries, 20),
            "sma_50":            compute_sma(parsed_entries, 50),
            "volatility":        compute_volatility(daily_returns),
            "cumulative_return": compute_cumulative_return(parsed_entries),
            "high_low_ranges":   compute_high_low_ranges(parsed_entries),
        }

    # Pass 2: build full N×N correlation matrix (includes self-correlation = 1.0)
    tickers = list(results.keys())
    correlation_matrix = {}

    for ticker_a in tickers:
        correlation_matrix[ticker_a] = {}
        for ticker_b in tickers:
            correlation_matrix[ticker_a][ticker_b] = compute_correlation(
                results[ticker_a]["daily_returns"],
                results[ticker_b]["daily_returns"],
            )

    return {
        "results": results,
        "correlation_matrix": correlation_matrix,
    }


# ---------------------------------------------------------------------------
# Standalone test — run from the project root: python stockpulse/analyzer.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import json
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

    from stockpulse.parser import parse_daily_data
    from stockpulse.config import CACHE_DIR

    TICKERS = ["AAPL", "MSFT", "XOM"]

    ticker_data = {}
    for ticker in TICKERS:
        cache_path = os.path.join(CACHE_DIR, f"{ticker}.json")
        if not os.path.exists(cache_path):
            print(f"[SKIP] No cache file found for {ticker} at {cache_path}")
            continue
        with open(cache_path, "r") as f:
            raw = json.load(f)
        ticker_data[ticker] = parse_daily_data(raw)
        print(f"[LOAD] {ticker}: {len(ticker_data[ticker])} entries loaded and parsed.")

    if len(ticker_data) < 2:
        print("Need at least 2 tickers in cache to run full test. Exiting.")
        raise SystemExit(1)

    analysis = run_analysis(ticker_data)
    results = analysis["results"]
    correlation_matrix = analysis["correlation_matrix"]

    print("\n--- HEADLINE METRICS ---")
    for ticker, metrics in results.items():
        n = len(ticker_data[ticker])
        print(f"\n{ticker}")
        print(f"  Entries:           {n}")
        print(f"  Daily returns:     {len(metrics['daily_returns'])} (expected {n - 1})")
        print(f"  SMA-20 length:     {len(metrics['sma_20'])} (expected {n - 20 + 1})")
        print(f"  SMA-50 length:     {len(metrics['sma_50'])} (expected {n - 50 + 1})")
        print(f"  Volatility:        {metrics['volatility']}")
        print(f"  Cumulative return: {metrics['cumulative_return']}")
        print(f"  Top volatile day:  {metrics['high_low_ranges'][0]}")

    print("\n--- CORRELATION MATRIX ---")
    tickers = list(results.keys())
    for ticker_a in tickers:
        for ticker_b in tickers:
            val = correlation_matrix[ticker_a][ticker_b]
            print(f"  {ticker_a} vs {ticker_b}: {val}")

    print("\n--- SANITY CHECKS ---")
    all_passed = True
    for ticker in tickers:
        self_corr = correlation_matrix[ticker][ticker]
        passed = abs(self_corr - 1.0) < 1e-9
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] Self-correlation {ticker}: {self_corr}")
        if not passed:
            all_passed = False

    for ticker, metrics in results.items():
        n = len(ticker_data[ticker])
        sma20_ok = len(metrics["sma_20"]) == n - 20 + 1
        sma50_ok = len(metrics["sma_50"]) == n - 50 + 1
        ret_ok   = len(metrics["daily_returns"]) == n - 1
        for label, passed in [("SMA-20 length", sma20_ok), ("SMA-50 length", sma50_ok), ("Returns length", ret_ok)]:
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {ticker} {label}")
            if not passed:
                all_passed = False

    print(f"\n{'All sanity checks passed.' if all_passed else 'One or more checks FAILED — see above.'}")


    print(f'results: \n{results}')