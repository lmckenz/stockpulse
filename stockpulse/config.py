import os
from pathlib import Path
from dotenv import load_dotenv

# Anchor all paths to the project root (the directory containing this package).
# Using __file__ here means paths work correctly regardless of where the script
# is invoked from — as long as you run from the project root, which is the
# contract established in the spec.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from the project root into os.environ.
# override=False means existing environment variables take precedence —
# useful if a CI system or shell has already set the key.
load_dotenv(PROJECT_ROOT / ".env", override=False)

# --- API Configuration ---

API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

if not API_KEY:
    raise EnvironmentError(
        "ALPHA_VANTAGE_API_KEY is not set. "
        "Add it to your .env file in the project root."
    )

BASE_URL = "https://www.alphavantage.co/query"

API_CALL_DELAY = 12     # seconds between API calls (5 requests per min limit)

# --- Default Values ---

# Used when no tickers are passed via CLI. Handy for quick testing.
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL"]

# --- Directory Paths ---

CACHE_DIR = PROJECT_ROOT / "cache"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Ensure both directories exist at import time.
# exist_ok=True means no error if they're already there.
CACHE_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
