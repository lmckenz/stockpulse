# StockPulse

A multi-module Python application that fetches stock market data from Alpha Vantage, runs statistical analysis, and produces a formatted HTML report.

Built as a structured learning project focused on API integration, data pipelines, and multi-module architecture.

---

## What It Does

Given one or more stock ticker symbols, StockPulse:

1. Fetches daily historical price data from the Alpha Vantage API
2. Caches raw responses locally to avoid redundant API calls
3. Parses and normalizes the nested JSON into clean Python data structures
4. Computes six statistical analyses per ticker:
   - **Daily returns** — percentage change between consecutive closing prices
   - **Simple moving averages** — 20-day and 50-day SMA
   - **Volatility** — standard deviation of daily returns
   - **Cumulative return** — total gain/loss over the analysis period
   - **High/low range analysis** — most volatile trading days ranked by intraday range
   - **Correlation matrix** — how tickers move relative to each other (requires 2+ tickers)
5. Outputs a terminal summary and a self-contained HTML report

---

## Project Structure

```
stockpulse/
│
├── stockpulse/              # Python package
│   ├── __init__.py
│   ├── config.py            # API keys, constants, directory paths
│   ├── client.py            # API fetching + local caching
│   ├── parser.py            # Raw JSON → clean list of dicts
│   ├── analyzer.py          # Statistical computations
│   ├── reporter.py          # Jinja2 HTML report generation
│   └── display.py           # Terminal summary output
│
├── templates/
│   └── report.html          # Jinja2 HTML template
│
├── cache/                   # Cached API responses (git-ignored)
├── output/                  # Generated reports (git-ignored)
│
├── main.py                  # Entry point + CLI
├── requirements.txt
├── .env                     # API key (git-ignored)
├── .env.example             # Template for .env setup
├── .gitignore
├── AMENDMENTS.md            # Log of spec deviations
└── README.md
```

---

## Prerequisites

- **Python 3.10+** (uses `statistics.correlation`, added in 3.10)
- **Alpha Vantage API key** — free at [alphavantage.co](https://www.alphavantage.co/support/#api-key)

---

## Setup

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd stockpulse
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure your API key**

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

Then open `.env` and replace the placeholder with your actual Alpha Vantage API key:

```
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

> **Important:** Never commit `.env` to version control. It is already listed in `.gitignore`.

---

## Usage

All commands are run from the project root directory.

**Basic usage — analyze one or more tickers:**

```bash
python main.py AAPL MSFT GOOGL
```

This fetches data (or loads from cache), runs all analyses, prints a terminal summary, and generates an HTML report in `output/`.

**Force fresh API calls (bypass cache):**

```bash
python main.py AAPL --no-cache
```

**Terminal summary only (skip HTML report):**

```bash
python main.py AAPL MSFT --terminal-only
```

**HTML report only (skip terminal output):**

```bash
python main.py AAPL MSFT --report-only
```

**Custom output directory:**

```bash
python main.py AAPL MSFT --output-dir ./reports
```

**Full CLI reference:**

| Argument | Description |
|---|---|
| `TICKER` (positional, 1+) | Stock ticker symbols to analyze |
| `--output-dir PATH` | Directory for the HTML report (default: `output/`) |
| `--no-cache` | Force fresh API calls, ignoring cached data |
| `--report-only` | Generate HTML report only, skip terminal display |
| `--terminal-only` | Print terminal summary only, skip HTML report |

---

## API Rate Limits

Alpha Vantage's free tier allows **25 requests per day** and **5 per minute**. StockPulse mitigates this in two ways:

- **Local caching:** Every API response is saved to `cache/` as a JSON file. Subsequent runs for the same ticker load from cache instead of hitting the API.
- **Automatic throttling:** A 12-second delay is applied between API calls to stay within the per-minute limit.

A 3-ticker run costs 3 API calls. If you have cached data from a previous run, it costs 0. Use `--no-cache` only when you need fresh data.

---

## Output

**Terminal summary** — a quick-glance table printed to stdout showing cumulative return, volatility, and latest SMA values for each ticker, followed by per-ticker detail blocks and the correlation matrix.

**HTML report** — a self-contained `.html` file saved to `output/` (or a custom path via `--output-dir`). Open it in any browser. It includes:

- Summary table with headline metrics
- Per-ticker sections with metric cards, top volatile days, recent daily returns, and aligned SMA tables
- Color-coded correlation matrix (green = high correlation, yellow = moderate, red = low)

---

## Tech Stack

| Category | Tool | Purpose |
|---|---|---|
| Language | Python 3.10+ | Core language |
| HTTP | `requests` | API calls |
| Templating | `jinja2` | HTML report generation |
| Configuration | `python-dotenv` | Load API key from `.env` |
| Statistics | `statistics` (stdlib) | `stdev`, `correlation` |
| CLI | `argparse` (stdlib) | Command-line interface |
| Logging | `logging` (stdlib) | Structured pipeline logs |
| Caching | `json` (stdlib) | Local file-based caching |

---

## Architecture

Data flows in one direction through the pipeline. No module reaches back upstream.

```
main.py (orchestrator)
  │
  ├── config.py ─────────── loads API key, constants, paths
  ├── client.py ─────────── fetches raw JSON (or loads from cache)
  ├── parser.py ─────────── normalizes into list of dicts
  ├── analyzer.py ────────── computes all statistical metrics
  ├── display.py ─────────── prints terminal summary
  └── reporter.py ────────── renders HTML report via Jinja2
```

Modules communicate through well-defined data contracts. See `AMENDMENTS.md` for documented deviations from the original specification.

---

## Known Limitations

- **Free tier data depth:** Alpha Vantage's free tier returns approximately 100 trading days with `outputsize=compact`. Full history requires a premium key.
- **Single-ticker correlation:** The correlation matrix requires 2+ tickers. With a single ticker, it is omitted from both terminal and HTML output.
- **No real-time data:** StockPulse analyzes daily closing prices, not intraday or streaming data.

---

## License

This project is licensed under the MIT License. For more details, see the LICENSE file attached.
