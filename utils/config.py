"""
Configuration module for the Market Intelligence Layer.

Loads environment variables from .env and exposes all settings as module-level
constants.  Every other module imports from here instead of reading env vars
directly, so configuration is centralised in one place.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load .env from project root (one level above utils/)
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
NEWSAPI_KEY: str | None = os.getenv("NEWSAPI_KEY")
FRED_API_KEY: str | None = os.getenv("FRED_API_KEY")
REDDIT_CLIENT_ID: str | None = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET: str | None = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "market_research_ai/1.0")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------
DUCKDB_PATH: str = os.getenv("DUCKDB_PATH", "data/market_research.duckdb")
# Resolve relative paths against the project root
if not os.path.isabs(DUCKDB_PATH):
    DUCKDB_PATH = str(_PROJECT_ROOT / DUCKDB_PATH)

# ---------------------------------------------------------------------------
# Stock tickers to track
# ---------------------------------------------------------------------------
DEFAULT_TICKERS: list[str] = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",   # Blue-chip equities
    "^GSPC", "^DJI", "^IXIC",                    # Major US indices
]

# ---------------------------------------------------------------------------
# FRED macro series
# ---------------------------------------------------------------------------
FRED_SERIES: dict[str, str] = {
    "DFF":      "Federal Funds Rate",
    "CPIAUCSL": "Consumer Price Index (CPI)",
    "UNRATE":   "Unemployment Rate",
    "GDP":      "Gross Domestic Product",
}

# ---------------------------------------------------------------------------
# News search queries
# ---------------------------------------------------------------------------
NEWS_QUERIES: list[str] = [
    "stock market",
    "economy",
    "federal reserve",
    "inflation",
    "earnings report",
]

# ---------------------------------------------------------------------------
# Reddit subreddits to monitor
# ---------------------------------------------------------------------------
REDDIT_SUBREDDITS: list[str] = [
    "wallstreetbets",
    "stocks",
    "investing",
]

# ---------------------------------------------------------------------------
# Pipeline schedule
# ---------------------------------------------------------------------------
PIPELINE_INTERVAL_MINUTES: int = int(os.getenv("PIPELINE_INTERVAL_MINUTES", "60"))

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------
PROJECT_ROOT: Path = _PROJECT_ROOT
LOG_DIR: Path = _PROJECT_ROOT / "logs"
SCHEMA_PATH: Path = _PROJECT_ROOT / "database" / "schema.sql"

# ===========================================================================
# PHASE 2 — NLP Intelligence Configuration
# ===========================================================================

# ---------------------------------------------------------------------------
# FinBERT model settings
# ---------------------------------------------------------------------------
FINBERT_MODEL_NAME: str = os.getenv("FINBERT_MODEL_NAME", "ProsusAI/finbert")
SENTIMENT_BATCH_SIZE: int = int(os.getenv("SENTIMENT_BATCH_SIZE", "16"))

# ---------------------------------------------------------------------------
# NLP scheduling intervals (minutes)
# ---------------------------------------------------------------------------
NEWS_SENTIMENT_INTERVAL_MINUTES: int = int(
    os.getenv("NEWS_SENTIMENT_INTERVAL_MINUTES", "60")
)
REDDIT_SENTIMENT_INTERVAL_MINUTES: int = int(
    os.getenv("REDDIT_SENTIMENT_INTERVAL_MINUTES", "30")
)
SECTOR_AGGREGATION_INTERVAL_MINUTES: int = int(
    os.getenv("SECTOR_AGGREGATION_INTERVAL_MINUTES", "1440")
)

# ---------------------------------------------------------------------------
# Known tickers for regex-based detection
# ---------------------------------------------------------------------------
KNOWN_TICKERS: set[str] = {
    # Mega-cap tech
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA", "NVDA",
    "NFLX", "AMD", "INTC", "CRM", "ORCL", "ADBE", "AVGO", "QCOM",
    "CSCO", "IBM", "TXN", "MU", "AMAT", "LRCX", "KLAC", "SNPS",
    # Finance / banking
    "JPM", "BAC", "WFC", "GS", "MS", "C", "USB", "PNC", "BK", "SCHW",
    "AXP", "COF", "SPGI", "MCO", "ICE", "CME", "BLK", "TROW",
    # Energy
    "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY",
    "HAL", "DVN", "FANG", "HES", "BKR",
    # Healthcare / pharma
    "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "DHR",
    "BMY", "AMGN", "GILD", "ISRG", "MDT", "SYK", "REGN", "VRTX",
    # Consumer
    "WMT", "PG", "KO", "PEP", "COST", "HD", "MCD", "NKE", "SBUX",
    "TGT", "LOW", "DIS", "CMCSA", "ABNB", "BKNG", "MAR", "UBER",
    # Industrial / other
    "BA", "CAT", "HON", "UPS", "FDX", "LMT", "RTX", "GE", "MMM",
    "DE", "EMR", "ITW",
    # Crypto-adjacent / fintech
    "COIN", "SQ", "PYPL", "V", "MA",
    # ETFs (commonly discussed)
    "SPY", "QQQ", "IWM", "DIA", "VOO", "VTI", "ARKK", "XLF", "XLE",
    "XLK", "XLV", "GLD", "SLV", "TLT",
}

# ---------------------------------------------------------------------------
# Sector → ticker mapping for aggregation
# ---------------------------------------------------------------------------
SECTOR_MAPPING: dict[str, list[str]] = {
    "Technology": [
        "AAPL", "MSFT", "GOOGL", "GOOG", "META", "NVDA", "AMD", "INTC",
        "CRM", "ORCL", "ADBE", "AVGO", "QCOM", "CSCO", "IBM", "TXN",
        "MU", "AMAT", "LRCX", "KLAC", "SNPS", "NFLX", "TSLA",
    ],
    "Banking": [
        "JPM", "BAC", "WFC", "GS", "MS", "C", "USB", "PNC", "BK",
        "SCHW", "AXP", "COF", "SPGI", "MCO", "ICE", "CME", "BLK", "TROW",
    ],
    "Energy": [
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY",
        "HAL", "DVN", "FANG", "HES", "BKR",
    ],
    "Healthcare": [
        "JNJ", "UNH", "PFE", "ABBV", "MRK", "LLY", "TMO", "ABT", "DHR",
        "BMY", "AMGN", "GILD", "ISRG", "MDT", "SYK", "REGN", "VRTX",
    ],
    "Consumer": [
        "WMT", "PG", "KO", "PEP", "COST", "HD", "MCD", "NKE", "SBUX",
        "TGT", "LOW", "DIS", "CMCSA", "ABNB", "BKNG", "MAR", "UBER",
        "AMZN",
    ],
    "Industrial": [
        "BA", "CAT", "HON", "UPS", "FDX", "LMT", "RTX", "GE", "MMM",
        "DE", "EMR", "ITW",
    ],
    "Fintech": [
        "COIN", "SQ", "PYPL", "V", "MA",
    ],
}

# Build reverse mapping: ticker → sector
TICKER_TO_SECTOR: dict[str, str] = {}
for _sector, _tickers in SECTOR_MAPPING.items():
    for _t in _tickers:
        TICKER_TO_SECTOR[_t] = _sector

# ---------------------------------------------------------------------------
# Event detection keyword patterns
# ---------------------------------------------------------------------------
EVENT_KEYWORDS: dict[str, list[str]] = {
    "earnings": [
        "earnings", "quarterly results", "revenue beat", "revenue miss",
        "EPS beat", "EPS miss", "earnings report", "earnings call",
        "profit warning", "guidance", "quarterly earnings",
        "beats estimates", "misses estimates", "fiscal quarter",
    ],
    "merger_acquisition": [
        "merger", "acquisition", "acquires", "acquired", "takeover",
        "buyout", "deal", "bid for", "merging with", "M&A",
        "hostile takeover", "tender offer", "all-stock deal",
        "all-cash deal", "strategic acquisition",
    ],
    "policy_change": [
        "regulation", "regulatory", "policy change", "new regulation",
        "deregulation", "antitrust", "sanctions", "tariff", "trade war",
        "executive order", "legislation", "government policy",
        "SEC ruling", "FTC", "DOJ",
    ],
    "interest_rate": [
        "interest rate", "rate hike", "rate cut", "fed rate",
        "federal funds rate", "basis points", "monetary policy",
        "FOMC", "fed meeting", "rate decision", "dovish", "hawkish",
        "quantitative easing", "quantitative tightening", "taper",
    ],
}

# ===========================================================================
# PHASE 3 — AI Research Agent Configuration
# ===========================================================================

# ---------------------------------------------------------------------------
# LLM settings (OpenAI)
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

# ---------------------------------------------------------------------------
# Research agent schedule & parameters
# ---------------------------------------------------------------------------
RESEARCH_INTERVAL_MINUTES: int = int(
    os.getenv("RESEARCH_INTERVAL_MINUTES", "240")
)
RESEARCH_LOOKBACK_HOURS: int = int(
    os.getenv("RESEARCH_LOOKBACK_HOURS", "72")
)
HYPOTHESIS_MIN_CONFIDENCE: float = float(
    os.getenv("HYPOTHESIS_MIN_CONFIDENCE", "0.5")
)
MAX_HYPOTHESES_PER_RUN: int = int(
    os.getenv("MAX_HYPOTHESES_PER_RUN", "10")
)

# ===========================================================================
# PHASE 4 — Strategy Discovery Engine Configuration
# ===========================================================================

# ---------------------------------------------------------------------------
# Strategy engine schedule & parameters
# ---------------------------------------------------------------------------
STRATEGY_INTERVAL_MINUTES: int = int(
    os.getenv("STRATEGY_INTERVAL_MINUTES", "360")
)
STRATEGY_MIN_CONFIDENCE: float = float(
    os.getenv("STRATEGY_MIN_CONFIDENCE", "0.4")
)
MAX_STRATEGIES_PER_RUN: int = int(
    os.getenv("MAX_STRATEGIES_PER_RUN", "15")
)

# ===========================================================================
# PHASE 5 — Automated Backtesting Engine Configuration
# ===========================================================================

# ---------------------------------------------------------------------------
# Backtesting schedule & parameters
# ---------------------------------------------------------------------------
BACKTEST_INTERVAL_MINUTES: int = int(
    os.getenv("BACKTEST_INTERVAL_MINUTES", "1440")
)
BACKTEST_INITIAL_CAPITAL: float = float(
    os.getenv("BACKTEST_INITIAL_CAPITAL", "100000")
)
BACKTEST_TRANSACTION_COST_PCT: float = float(
    os.getenv("BACKTEST_TRANSACTION_COST_PCT", "0.0005")
)
BACKTEST_SLIPPAGE_PCT: float = float(
    os.getenv("BACKTEST_SLIPPAGE_PCT", "0.0002")
)
BACKTEST_MIN_TRADES: int = int(
    os.getenv("BACKTEST_MIN_TRADES", "10")
)
BACKTEST_BENCHMARK_TICKER: str = os.getenv(
    "BACKTEST_BENCHMARK_TICKER", "^GSPC"
)
