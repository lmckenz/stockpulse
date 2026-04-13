# main.py
import argparse
import logging
import sys

from stockpulse import client, parser, analyzer, reporter, display


def build_parser():
    p = argparse.ArgumentParser(
        prog="stockpulse",
        description="Fetch, analyze, and report on stock market data.",
    )
    p.add_argument(
        "tickers",
        nargs="+",
        metavar="TICKER",
        help="One or more stock ticker symbols (e.g. AAPL MSFT GOOGL).",
    )
    p.add_argument(
        "--output-dir",
        metavar="PATH",
        default=None,
        help="Directory to write the HTML report. Defaults to config.OUTPUT_DIR.",
    )
    p.add_argument(
        "--no-cache",
        action="store_true",
        help="Force fresh API calls even if cached data exists.",
    )
    p.add_argument(
        "--report-only",
        action="store_true",
        help="Generate the HTML report only. Skip terminal display.",
    )
    p.add_argument(
        "--terminal-only",
        action="store_true",
        help="Print terminal summary only. Skip HTML report generation.",
    )
    return p


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    parser_cli = build_parser()
    args = parser_cli.parse_args()

    logger.info("Starting StockPulse — tickers: %s", ", ".join(args.tickers))

    # --- Fetch ---
    raw_data = {}
    for ticker in args.tickers:
        logger.info("Fetching data for %s (use_cache=%s)", ticker, not args.no_cache)
        raw = client.fetch_daily_data(ticker, use_cache=not args.no_cache)
        if raw is None:
            logger.warning("No data returned for %s — skipping", ticker)
            continue
        raw_data[ticker] = raw
        logger.info("Fetch complete for %s", ticker)

    if not raw_data:
        logger.error("No data was retrieved for any ticker — exiting")
        sys.exit(1)

    # --- Parse ---
    parsed_data = {}
    for ticker, raw in raw_data.items():
        logger.info("Parsing data for %s", ticker)
        parsed_data[ticker] = parser.parse_daily_data(raw)
        logger.info("Parse complete for %s — %d records", ticker, len(parsed_data[ticker]))

    # --- Analyze ---
    logger.info("Running analysis")
    analysis = analyzer.run_analysis(parsed_data)
    logger.info("Analysis complete")

    # --- Output ---
    if not args.report_only:
        logger.info("Rendering terminal summary")
        display.display_all(analysis)

    if not args.terminal_only:
        logger.info("Generating HTML report")
        reporter.generate_report(analysis, output_dir=args.output_dir)
        logger.info("HTML report written")

    logger.info("StockPulse complete")


if __name__ == "__main__":
    main()

    