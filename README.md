# Trading Strategy Engine — AI-Driven Financial Research Platform

An end-to-end, AI-powered quantitative trading platform that ingests multi-source market data, runs NLP sentiment analysis, generates trading hypotheses via LLM agents, converts them to structured algorithmic strategies, backtests them, and explains their performance — all surfaced through a live React dashboard.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│  Yahoo Finance  │  NewsAPI  │  FRED API  │  Reddit (optional)    │
└────────┬────────┴─────┬─────┴─────┬──────┴──────┬───────────────┘
         │              │           │             │
         ▼              ▼           ▼             ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 1 — DATA INGESTION                                        │
│  stock_collector │ news_collector │ macro_collector │ social      │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 2 — NLP INTELLIGENCE                                      │
│  FinBERT sentiment │ Event detection │ Sector aggregation        │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 3 — AI RESEARCH AGENT                                     │
│  Signal summary → LLM hypothesis generation → Rank → Filter     │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 4 — STRATEGY DISCOVERY ENGINE                             │
│  Template match → LLM strategy build → Validate → Rank          │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 5 — AUTOMATED BACKTESTING ENGINE                          │
│  Signal interpreter → Trade executor → Portfolio sim → Metrics  │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  PHASE 6 — EXPLAINABLE AI DECISION ENGINE                        │
│  Feature builder → SHAP analysis → Signal attribution → Text    │
└──────────────────────────┬───────────────────────────────────────┘
                           ▼
      ┌────────────────────────────────────┐
      │  DuckDB · 12 tables · auto-created │
      └────────────────────────────────────┘
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│  DASHBOARD                                                       │
│  FastAPI backend (port 8000) + React/Vite frontend (port 5173)  │
│  Panels: Sentiment · Intelligence · Hypotheses · Strategies      │
│          Backtest Performance · Explainable AI · Trade Sim      │
└──────────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Prerequisites

- Python 3.10+
- Node.js 18+

### 2. Install Python Dependencies

```bash
cd market_research_ai
pip install -r requirements.txt
```

### 3. Configure API Keys

Edit the `.env` file (already included as a template):

| Key | Required | Where to get it |
|---|---|---|
| `NEWSAPI_KEY` | ✅ | [newsapi.org/register](https://newsapi.org/register) |
| `FRED_API_KEY` | ✅ | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| `OPENAI_API_KEY` | ✅ | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `REDDIT_CLIENT_ID` | ⬜ | [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) *(optional)* |
| `REDDIT_CLIENT_SECRET` | ⬜ | Same as above *(optional)* |

> **Note:** Reddit credentials are optional — social sentiment will be skipped. Yahoo Finance requires no key.

### 4. Run the Data Pipeline

```bash
# Full cycle (ingest → NLP → research → strategy → backtest)
python -m pipeline.data_pipeline --once

# Run individual phases
python -m pipeline.data_pipeline --research   # Phase 3: LLM hypothesis generation
python -m pipeline.data_pipeline --strategy   # Phase 4: LLM strategy discovery
python -m pipeline.data_pipeline --backtest   # Phase 5: Backtesting engine

# After backtesting, generate AI explanations
python generate_explanations.py

# Continuous scheduled mode
python -m pipeline.data_pipeline --schedule
```

### 5. Start the Dashboard

**Terminal 1 — Backend API:**
```bash
python -m uvicorn dashboard.backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 — Frontend:**
```bash
cd dashboard/frontend
npm install
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Project Structure

```
market_research_ai/
├── .env                          # API keys (git-ignored)
├── requirements.txt              # Python dependencies
├── generate_explanations.py      # Run Explainability Engine on backtests
│
├── data_ingestion/               # Phase 1 — data collectors
│   ├── stock_collector.py        # Yahoo Finance OHLCV
│   ├── news_collector.py         # NewsAPI headlines
│   ├── macro_collector.py        # FRED macro indicators
│   └── social_collector.py      # Reddit posts (optional)
│
├── sentiment_engine/             # Phase 2 — NLP intelligence
│   ├── finbert_model.py          # FinBERT inference wrapper
│   ├── news_sentiment.py         # Per-article sentiment scoring
│   ├── reddit_sentiment.py       # Reddit engagement sentiment
│   ├── event_detection.py        # Earnings / M&A / policy events
│   └── sector_aggregation.py    # Sector-level signal aggregation
│
├── research_agent/               # Phase 3 — AI research agent
│   ├── agent.py                  # Orchestrator
│   ├── signal_summarizer.py      # Market snapshot builder
│   ├── hypothesis_generator.py   # OpenAI LLM hypothesis generation
│   ├── hypothesis_ranker.py      # Confidence ranking
│   ├── hypothesis_filter.py      # Quality filtering
│   └── prompt_templates.py       # LLM prompt templates
│
├── strategy_engine/              # Phase 4 — strategy discovery
│   ├── __init__.py               # StrategyDiscoveryEngine orchestrator
│   ├── strategy_templates.py     # 5 canonical strategy archetypes
│   ├── strategy_builder.py       # LLM hypothesis → strategy JSON
│   ├── strategy_parser.py        # JSON parsing & normalisation
│   ├── strategy_validator.py     # Rule-based quality gate
│   └── strategy_ranker.py        # 5-dimension scoring & ranking
│
├── backtesting_engine/           # Phase 5 — automated backtesting
│   ├── __init__.py               # BacktestEngine orchestrator
│   ├── backtest_runner.py        # Per-strategy backtest coordination
│   ├── strategy_interpreter.py   # JSON conditions → signal functions
│   ├── trade_executor.py         # Signal → trades
│   ├── portfolio_simulator.py    # Position sizing, P&L simulation
│   └── performance_metrics.py   # Sharpe, drawdown, win rate, etc.
│
├── explainability_engine/        # Phase 6 — explainable AI
│   ├── strategy_explainer.py     # End-to-end explanation pipeline
│   ├── feature_builder.py        # Feature matrix from trades & prices
│   ├── shap_analyzer.py          # SHAP value computation
│   ├── signal_attribution.py     # Signal → dominant factor mapping
│   └── explanation_ranker.py    # Confidence scoring
│
├── dashboard/
│   ├── backend/
│   │   ├── app.py                # FastAPI application & route definitions
│   │   └── db_queries.py         # Dashboard-specific DB queries
│   └── frontend/                 # React + Vite + TypeScript
│       └── src/
│           ├── App.tsx            # Main dashboard layout
│           ├── api/client.ts      # API fetch functions
│           ├── types.ts           # Shared TypeScript types
│           └── components/panels/
│               ├── MarketSentimentMonitor.tsx
│               ├── MarketIntelligencePanel.tsx
│               ├── ResearchHypothesesPanel.tsx
│               ├── StrategyDiscoveryPanel.tsx
│               ├── BacktestPerformance.tsx
│               ├── ExplainableAIInsights.tsx
│               └── TradeSimulationViewer.tsx
│
├── database/
│   ├── schema.sql                # DuckDB table definitions (all 6 phases)
│   └── db_manager.py             # DB connection + insert/query helpers
│
├── pipeline/
│   └── data_pipeline.py          # Orchestration + scheduling + CLI
│
├── utils/
│   ├── config.py                 # Centralised config (reads .env)
│   └── logger.py                 # Rotating file + console logger
│
├── data/                         # DuckDB file (auto-created, git-ignored)
└── logs/                         # Log files (auto-created, git-ignored)
```

---

## Database Schema

| Table | Phase | Description |
|---|---|---|
| `stock_prices` | 1 | Daily OHLCV data from Yahoo Finance |
| `news_articles` | 1 | Financial news headlines from NewsAPI |
| `macro_indicators` | 1 | FRED macro time-series (CPI, GDP, Fed Funds, etc.) |
| `social_sentiment` | 1 | Reddit posts (optional) |
| `news_sentiment` | 2 | FinBERT sentiment scores per article |
| `social_sentiment_scores` | 2 | Engagement-weighted Reddit sentiment |
| `sector_sentiment` | 2 | Aggregated sector-level sentiment signals |
| `market_events` | 2 | Detected earnings / M&A / policy events |
| `research_hypotheses` | 3 | LLM-generated trading hypotheses |
| `trading_strategies` | 4 | Structured, backtestable algorithmic strategies |
| `backtest_results` | 5 | Strategy performance metrics (Sharpe, drawdown, etc.) |
| `trade_logs` | 5 | Individual simulated trade records |
| `strategy_performance` | 5 | Composite strategy performance evaluation |
| `strategy_explanations` | 6 | SHAP values, signal attribution, and narrative text |

---

## Dashboard Panels

| Panel | Data Source | What it shows |
|---|---|---|
| **Market Sentiment Monitor** | `news_sentiment`, `sector_sentiment` | FinBERT sentiment trends by sector |
| **Market Intelligence** | `macro_indicators`, `market_events` | FRED macro indicators and event feed |
| **Research Hypotheses** | `research_hypotheses` | LLM-generated hypothesis cards with confidence scores |
| **Strategy Discovery** | `trading_strategies` | Active strategies with entry/exit rules |
| **Backtest Performance** | `backtest_results` | Sharpe ratio, max drawdown, win rate, return charts |
| **Explainable AI Insights** | `strategy_explanations` | SHAP feature importance and narrative explanation |
| **Trade Simulation Viewer** | `trade_logs` | Individual trades plotted against the price chart |

---

## API Endpoints

All served from **http://localhost:8000/api**

| Endpoint | Description |
|---|---|
| `GET /sentiment` | Sector sentiment data |
| `GET /macro` | Macro indicators + market events |
| `GET /hypotheses` | Research hypotheses list |
| `GET /strategies` | Trading strategies list |
| `GET /backtests` | Backtest results |
| `GET /explanations` | Strategy explanations |
| `GET /trade-simulation/{id}` | Trades + price data for a strategy |

---

## Strategy Templates

| Template | Trigger | Use Case |
|---|---|---|
| **Momentum** | Sustained price move + positive sentiment | Trend following |
| **Mean Reversion** | Overbought/oversold + divergence | Contrarian plays |
| **Event-Driven** | Market events (earnings, M&A) | Catalyst trading |
| **Macro Regime** | Rate / CPI / GDP shifts | Macro-driven trades |
| **Sentiment Divergence** | News vs price disconnect | Sentiment alpha |

---

## Key Technologies

| Layer | Technology |
|---|---|
| Data ingestion | `yfinance`, `requests` (NewsAPI, FRED, Reddit) |
| NLP / Sentiment | `transformers` (FinBERT), `torch` |
| LLM agents | `openai` (GPT-3.5-turbo / GPT-4o) |
| Backtesting | Pure Python — no external backtest library |
| Explainability | `shap`, `scikit-learn`, `pandas` |
| Database | `duckdb` |
| Backend API | `fastapi`, `uvicorn` |
| Frontend | React 18, Vite, TypeScript, Recharts, Tailwind CSS |
| Scheduling | `schedule` (Python) |
