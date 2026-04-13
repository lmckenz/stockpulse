"""
display.py — Terminal output for StockPulse analysis results.

Responsibilities:
    - Format and print analysis results to stdout
    - Handle all number rounding for display (never mutates input data)
    - Produce a complete terminal report via display_all()

Note (Amendment 001): daily_returns, sma_20, and sma_50 are lists of
(date, float) tuples per the analyzer.py implementation. Float values
are extracted via index [1] throughout this module.

No file I/O, no HTML, no external libraries.
"""


def print_summary_table(results: dict) -> None:
    """Print a one-line-per-ticker summary table with headline metrics."""

    header_line = "=" * 69 #nice
    col_ticker  = "Ticker"
    col_cum_ret = "Cum. Return %"
    col_vol     = "Volatility %"
    col_sma20   = "SMA-20"
    col_sma50   = "SMA-50"

    print(f"\n{header_line}")
    print(f"  STOCKPULSE — SUMMARY")
    print(f"{header_line}")

    print(
        f"  {col_ticker:<8}"
        f"  {col_cum_ret:>14}"
        f"  {col_vol:>13}"
        f"  {col_sma20:>10}"
        f"  {col_sma50:>10}"
    )
    print(
        f"  {'--------':<8}"
        f"  {'---------------':>14}"
        f"  {'-------------':>13}"
        f"  {'----------':>10}"
        f"  {'----------':>10}"
    )

    ticker_data = results.get("results", {})
    for ticker, metrics in ticker_data.items():

        cum_ret_display = metrics["cumulative_return"] * 100
        vol_display     = metrics["volatility"] * 100

        sma20_list = metrics.get("sma_20", [])
        sma50_list = metrics.get("sma_50", [])

        # [1] extracts the float from the (date, float) tuple — Amendment 001
        sma20_display = f"{sma20_list[-1][1]:>10.2f}" if sma20_list else f"{'N/A':>10}"
        sma50_display = f"{sma50_list[-1][1]:>10.2f}" if sma50_list else f"{'N/A':>10}"

        print(
            f"  {ticker:<8}"
            f"  {cum_ret_display:>14.2f}"
            f"  {vol_display:>13.2f}"
            f"  {sma20_display}"
            f"  {sma50_display}"
        )

    print(f"{header_line}\n")


def print_ticker_detail(ticker: str, ticker_results: dict) -> None:
    """Print a detailed metric block for a single ticker."""

    divider = "-" * 60

    cum_ret_display = ticker_results["cumulative_return"] * 100
    vol_display     = ticker_results["volatility"] * 100

    sma20_list = ticker_results.get("sma_20", [])
    sma50_list = ticker_results.get("sma_50", [])
    returns    = ticker_results.get("daily_returns", [])
    hl_ranges  = ticker_results.get("high_low_ranges", [])

    # [1] extracts the float from the (date, float) tuple — Amendment 001
    sma20_str = f"{sma20_list[-1][1]:.2f}" if sma20_list else "N/A"
    sma50_str = f"{sma50_list[-1][1]:.2f}" if sma50_list else "N/A"

    print(f"\n{divider}")
    print(f"  {ticker} — Detailed Analysis")
    print(f"{divider}")

    print(f"  {'Cumulative Return':<20}: {cum_ret_display:>10.2f} %")
    print(f"  {'Volatility':<20}: {vol_display:>10.2f} %")
    print(f"  {'Latest SMA-20':<20}: {sma20_str:>10}")
    print(f"  {'Latest SMA-50':<20}: {sma50_str:>10}")

    inferred_data_points = len(returns) + 1
    print(f"  {'Data points':<20}: {inferred_data_points:>10}")

    if returns:
        # [1] extracts the float from the (date, float) tuple — Amendment 001
        first_ret = returns[0][1] * 100
        last_ret  = returns[-1][1] * 100
        print(
            f"  {'Daily Returns':<20}: {len(returns):>6} values"
            f"  (first: {first_ret:.2f} %,  last: {last_ret:.2f} %)"
        )
    else:
        print(f"  {'Daily Returns':<20}: N/A")

    print(f"\n  Top 5 High/Low Range Days:")
    top_ranges = hl_ranges[:5]
    if top_ranges:
        for date_str, range_val in top_ranges:
            print(f"    {date_str}      range: {range_val:>8.2f}")
    else:
        print(f"    No range data available.")

    print(f"{divider}")


def print_correlation_matrix(correlation_matrix: dict) -> None:
    """Print the correlation matrix as a cleanly aligned grid."""

    if not correlation_matrix:
        print("\n  No correlation data available (requires 2+ tickers).\n")
        return

    header_line = "=" * 60
    tickers = list(correlation_matrix.keys())

    col_width = max(max(len(t) for t in tickers), 8) + 2

    print(f"\n{header_line}")
    print(f"  CORRELATION MATRIX")
    print(f"{header_line}")

    header = f"  {' ' * col_width}" + "".join(f"{t:>{col_width}}" for t in tickers)
    print(header)

    for row_ticker in tickers:
        row_label  = f"  {row_ticker:<{col_width}}"
        row_values = ""
        for col_ticker in tickers:
            value = correlation_matrix[row_ticker][col_ticker]
            row_values += f"{value:>{col_width}.4f}"
        print(row_label + row_values)

    print(f"{header_line}\n")


def display_all(results: dict) -> None:
    """
    Produce a complete terminal report from the full results dict.

    Calls print_summary_table, then per-ticker detail blocks,
    then the correlation matrix.

    Parameters
    ----------
    results : dict
        The dict returned by analyzer.run_analysis().
        Expected shape:
            {
                "results": {
                    "AAPL": { cumulative_return, volatility, sma_20,
                              sma_50, daily_returns, high_low_ranges },
                    ...
                },
                "correlation_matrix": {
                    "AAPL": { "AAPL": 1.0, "MSFT": 0.87, ... },
                    ...
                }
            }
    """
    ticker_data        = results.get("results", {})
    correlation_matrix = results.get("correlation_matrix", {})

    print_summary_table(results)

    for ticker, ticker_results in ticker_data.items():
        print_ticker_detail(ticker, ticker_results)

    print_correlation_matrix(correlation_matrix)


if __name__ == "__main__":
    import os
    import json
    import sys

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from stockpulse import parser, analyzer

    TICKERS_TO_TEST = ["AAPL", "MSFT", "XOM"]
    CACHE_DIR = os.path.join(project_root, "cache")

    ticker_parsed_data = {}
    for ticker in TICKERS_TO_TEST:
        cache_path = os.path.join(CACHE_DIR, f"{ticker}.json")
        if not os.path.exists(cache_path):
            print(f"[SKIP] No cached file found for {ticker} at {cache_path}")
            continue
        with open(cache_path, "r") as f:
            raw_json = json.load(f)
        parsed = parser.parse_daily_data(raw_json)
        ticker_parsed_data[ticker] = parsed
        print(f"[OK]   Loaded {len(parsed)} records for {ticker}")

    if not ticker_parsed_data:
        print("No cached data found. Run client.py first to populate the cache.")
        sys.exit(1)

    results = analyzer.run_analysis(ticker_parsed_data)
    display_all(results)
    