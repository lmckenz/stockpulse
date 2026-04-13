# stockpulse/reporter.py

from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from stockpulse import config
from pathlib import Path


def generate_report(analysis, output_dir=None):
    """
    Render the Jinja2 HTML template with analysis data and write to output_dir.

    Args:
        analysis:   the wrapper dict returned by run_analysis(), with keys
                    "results" and "correlation_matrix"
        output_dir: path to the output folder. Defaults to config.OUTPUT_DIR.

    Returns:
        str: the absolute path of the generated HTML file
    """
    if output_dir is None:
        output_dir = config.OUTPUT_DIR

    # Unpack the wrapper dict — Amendment 002
    results = analysis["results"]
    correlation_matrix = analysis["correlation_matrix"]

    # Locate templates/ using the project root from config
    templates_dir = config.PROJECT_ROOT / "templates"

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("report.html")

    # Pre-process aligned SMA table per ticker
    sma_tables = {}
    for ticker, data in results.items():
        sma_20_dict = {date: val for date, val in data.get("sma_20", [])}
        sma_50_dict = {date: val for date, val in data.get("sma_50", [])}
        shared_dates = sorted(set(sma_20_dict) & set(sma_50_dict))
        sma_tables[ticker] = [
            (date, sma_20_dict[date], sma_50_dict[date])
            for date in shared_dates
        ]

    # Timestamp for header and filename
    now = datetime.now()
    generated_at = now.strftime("%Y-%m-%d %H:%M:%S")
    date_slug = now.strftime("%Y-%m-%d_%H%M%S")

    context = {
        "generated_at": generated_at,
        "tickers": list(results.keys()),
        "results": results,
        "correlation_matrix": correlation_matrix,
        "sma_tables": sma_tables,
    }

    html_output = template.render(**context)

    # config.OUTPUT_DIR.mkdir() is called at import time, but output_dir
    # might be a custom path passed in from the CLI, so we still create it.
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"report_{date_slug}.html"
    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_output)

    print(f"[reporter] Report written to: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(config.PROJECT_ROOT))

    from stockpulse.client import fetch_daily_data
    from stockpulse.parser import parse_daily_data
    from stockpulse.analyzer import run_analysis

    ticker_data = {}
    for ticker in config.DEFAULT_TICKERS:
        print(f"[test] Loading {ticker}...")
        raw = fetch_daily_data(ticker)
        ticker_data[ticker] = parse_daily_data(raw)

    print("[test] Running analysis...")
    analysis = run_analysis(ticker_data)

    path = generate_report(analysis)
    print(f"[test] Done. Open in browser:\n       {path}")

    

    