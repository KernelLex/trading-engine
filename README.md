# Market Intelligence Layer

An AI-driven financial research platform that collects, normalises, and stores multi-source market data, generates trading hypotheses via NLP and LLM agents, and converts them into structured algorithmic strategies.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                             │
│  Yahoo Finance  │  NewsAPI  │  FRED API  │  Reddit API       │
└───────┬─────────┴─────┬─────┴──────┬──────┴──────┬───────────┘
        │               │            │             │
        ▼               ▼            ▼             ▼
┌──────────────────────────────────────────────────────────────┐
│           PHASE 1 — INGESTION MODULES                        │
│  stock_collector │ news_collector │ macro_collector │ social  │
└───────┬─────────┴─────┬─────────┴──────┬──────────┴──┬──────┘
        ▼               ▼               ▼              ▼
┌──────────────────────────────────────────────────────────────┐
│           PHASE 2 — NLP INTELLIGENCE                         │
│  FinBERT sentiment │ Event detection │ Sector aggregation    │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│           PHASE 3 — AI RESEARCH AGENT                        │
│  Signal summary → LLM hypothesis generation → Rank → Filter │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────┐
│           PHASE 4 — STRATEGY DISCOVERY ENGINE                │
│  Template match → LLM strategy build → Validate → Rank      │
└──────────────────────────┬───────────────────────────────────┘
                           ▼
                    ┌──────────────┐
                    │    DuckDB    │
                    │  11 tables   │
                    └──────────────┘
```

## Quick Start

### 1. Prerequisites

- Python 3.10+
- `pip` package manager

### 2. Install Dependencies

```bash
cd market_research_ai
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
# Copy the template and fill in your keys
cp .env.example .env
```

Edit `.env` with your keys:

| Key | Required | Where to get it |
|---|---|---|
| `NEWSAPI_KEY` | Yes | [newsapi.org/register](https://newsapi.org/register) |
| `FRED_API_KEY` | Yes | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `REDDIT_CLIENT_ID` | No | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) |
| `REDDIT_CLIENT_SECRET` | No | Same as above |
| `OPENAI_API_KEY` | Yes* | [platform.openai.com](https://platform.openai.com/api-keys) |

> **Note:** Yahoo Finance requires no API key. Reddit credentials are optional. OpenAI key is required for Phase 3 (research) and Phase 4 (strategy).

### 4. Run the Pipeline

```bash
# Full cycle: ingest → NLP → research → strategy
python -m pipeline.data_pipeline --once

# Individual phases
python -m pipeline.data_pipeline --once --ingest-only   # Phase 1 only
python -m pipeline.data_pipeline --nlp                   # Phase 2 only
python -m pipeline.data_pipeline --research              # Phase 3 only
python -m pipeline.data_pipeline --strategy              # Phase 4 only

# Scheduled mode (continuous)
python -m pipeline.data_pipeline --schedule
```

### 5. Check Results

Logs: `logs/market_research.log`. Database: `data/market_research.duckdb`.

```python
import duckdb
conn = duckdb.connect("data/market_research.duckdb")
print(conn.execute("SELECT COUNT(*) FROM stock_prices").fetchone())
print(conn.execute("SELECT COUNT(*) FROM research_hypotheses").fetchone())
print(conn.execute("SELECT COUNT(*) FROM trading_strategies").fetchone())
```

## Project Structure

```
market_research_ai/
├── .env                      # API keys (git-ignored)
├── requirements.txt          # Python dependencies
├── README.md
│
├── data_ingestion/           # Phase 1 — data collectors
│   ├── stock_collector.py
│   ├── news_collector.py
│   ├── macro_collector.py
│   └── social_collector.py
│
├── sentiment_engine/         # Phase 2 — NLP intelligence
│   ├── finbert_model.py
│   ├── news_sentiment.py
│   ├── reddit_sentiment.py
│   ├── event_detection.py
│   └── sector_aggregation.py
│
├── research_agent/           # Phase 3 — AI research agent
│   ├── agent.py
│   ├── signal_summarizer.py
│   ├── hypothesis_generator.py
│   ├── hypothesis_ranker.py
│   ├── hypothesis_filter.py
│   └── prompt_templates.py
│
├── strategy_engine/          # Phase 4 — strategy discovery
│   ├── __init__.py           # StrategyDiscoveryEngine orchestrator
│   ├── strategy_templates.py # 5 canonical strategy archetypes
│   ├── strategy_builder.py   # LLM-powered hypothesis→strategy
│   ├── strategy_parser.py    # JSON parsing & normalisation
│   ├── strategy_validator.py # Rule-based quality gate
│   └── strategy_ranker.py    # 5-dimension scoring & ranking
│
├── database/
│   ├── schema.sql            # DuckDB table definitions (all phases)
│   └── db_manager.py         # DB connection + insert/query helpers
│
├── pipeline/
│   └── data_pipeline.py      # Orchestration + scheduling + CLI
│
├── utils/
│   ├── config.py             # Centralised configuration
│   └── logger.py             # Rotating file logger
│
├── data/                     # DuckDB file (auto-created)
└── logs/                     # Log files (auto-created)
```

## Database Schema

| Table | Phase | Primary Key | Description |
|---|---|---|---|
| `stock_prices` | 1 | `(ticker, date)` | Daily OHLCV data |
| `news_articles` | 1 | `article_id` | Financial news headlines |
| `macro_indicators` | 1 | `(series_id, date)` | FRED macro time-series |
| `social_sentiment` | 1 | `post_id` | Reddit post data |
| `news_sentiment` | 2 | `article_id` | FinBERT sentiment scores |
| `social_sentiment_scores` | 2 | `post_id` | Engagement-weighted sentiment |
| `sector_sentiment` | 2 | `(sector, timestamp)` | Aggregated sector signals |
| `market_events` | 2 | `event_id` | Detected market events |
| `research_hypotheses` | 3 | `hypothesis_id` | LLM-generated trading hypotheses |
| `trading_strategies` | 4 | `strategy_id` | Structured algorithmic strategies |

## Phase 4 — Strategy Discovery Engine

### Strategy Templates

| Template | Trigger | Use Case |
|---|---|---|
| **Momentum** | Sustained price move + sentiment | Trend following |
| **Mean Reversion** | Oversold/overbought + divergence | Contrarian plays |
| **Event-Driven** | Market events (earnings, M&A) | Catalysts |
| **Macro Regime** | Rate/CPI/GDP shifts | Macro trades |
| **Sentiment Divergence** | News vs price disconnect | Sentiment alpha |

### Strategy Workflow

1. Pull active hypotheses from `research_hypotheses`
2. Match each to a strategy template (keyword heuristics)
3. Call OpenAI to convert hypothesis + template → structured strategy JSON
4. Parse and normalise LLM output
5. Validate: reject missing rules, conflicts, unbacktestable strategies
6. Rank by signal strength, clarity, macro/sentiment alignment, novelty
7. Store in `trading_strategies` table

### Scheduling

| Mode | Frequency |
|---|---|
| After research cycle | Default |
| Continuous | Every 6 hours (`STRATEGY_INTERVAL_MINUTES=360`) |
| On-demand | `python -m pipeline.data_pipeline --strategy` |
