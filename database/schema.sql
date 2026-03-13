-- =========================================================================
-- Market Intelligence Layer — Database Schema  (DuckDB)
-- =========================================================================
-- All tables use CREATE TABLE IF NOT EXISTS so the script is idempotent.
-- =========================================================================

-- =====================  PHASE 1 — DATA INGESTION  ========================

-- Stock price OHLCV data (daily granularity)
CREATE TABLE IF NOT EXISTS stock_prices (
    ticker       VARCHAR   NOT NULL,
    date         DATE      NOT NULL,
    open         DOUBLE,
    high         DOUBLE,
    low          DOUBLE,
    close        DOUBLE,
    volume       BIGINT,
    ingested_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, date)
);

-- Financial news articles
CREATE TABLE IF NOT EXISTS news_articles (
    article_id   VARCHAR   PRIMARY KEY,   -- SHA-256 hash of url
    title        VARCHAR,
    description  VARCHAR,
    source_name  VARCHAR,
    url          VARCHAR,
    published_at TIMESTAMP,
    ingested_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Macroeconomic indicator time-series from FRED
CREATE TABLE IF NOT EXISTS macro_indicators (
    series_id      VARCHAR   NOT NULL,      -- e.g. 'DFF', 'CPIAUCSL'
    indicator_name VARCHAR,
    date           DATE      NOT NULL,
    value          DOUBLE,
    ingested_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (series_id, date)
);

-- Reddit / social-media sentiment posts
CREATE TABLE IF NOT EXISTS social_sentiment (
    post_id       VARCHAR   PRIMARY KEY,
    subreddit     VARCHAR,
    title         VARCHAR,
    selftext      VARCHAR,
    score         INTEGER,
    num_comments  INTEGER,
    created_utc   TIMESTAMP,
    ingested_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==================  PHASE 2 — NLP INTELLIGENCE  =========================

-- Per-article sentiment scores produced by FinBERT
CREATE TABLE IF NOT EXISTS news_sentiment (
    article_id       VARCHAR   PRIMARY KEY,
    timestamp        TIMESTAMP,
    headline         VARCHAR,
    sentiment_label  VARCHAR,          -- positive / neutral / negative
    sentiment_score  DOUBLE,           -- model confidence [-1, 1]
    entities_detected VARCHAR,         -- JSON array of entities
    related_tickers   VARCHAR,         -- JSON array of ticker symbols
    processed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Per-post engagement-weighted sentiment from Reddit
CREATE TABLE IF NOT EXISTS social_sentiment_scores (
    post_id          VARCHAR   PRIMARY KEY,
    subreddit        VARCHAR,
    timestamp        TIMESTAMP,
    sentiment_label  VARCHAR,
    sentiment_score  DOUBLE,
    engagement_score DOUBLE,           -- score * log(1 + num_comments)
    tickers_detected VARCHAR,          -- JSON array of ticker symbols
    processed_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated sector-level sentiment signals
CREATE TABLE IF NOT EXISTS sector_sentiment (
    sector               VARCHAR   NOT NULL,
    timestamp            TIMESTAMP NOT NULL,
    avg_sentiment_score  DOUBLE,
    news_signal_strength DOUBLE,
    social_signal_strength DOUBLE,
    processed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (sector, timestamp)
);

-- Detected market events (earnings, M&A, policy, rate decisions)
CREATE TABLE IF NOT EXISTS market_events (
    event_id         VARCHAR   PRIMARY KEY,
    timestamp        TIMESTAMP,
    event_type       VARCHAR,          -- earnings / merger_acquisition / policy_change / interest_rate
    related_tickers  VARCHAR,          -- JSON array of ticker symbols
    confidence_score DOUBLE,
    source_article_id VARCHAR,
    detected_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =================  PHASE 3 — AI RESEARCH AGENT  =========================

-- LLM-generated trading hypotheses
CREATE TABLE IF NOT EXISTS research_hypotheses (
    hypothesis_id      VARCHAR   PRIMARY KEY,
    timestamp          TIMESTAMP NOT NULL,
    title              VARCHAR   NOT NULL,
    hypothesis_text    VARCHAR   NOT NULL,
    asset_scope        VARCHAR,          -- ticker(s), index, sector ETF, or macro asset class
    sector             VARCHAR,
    trigger_conditions VARCHAR,          -- JSON: structured conditions that triggered the hypothesis
    expected_direction VARCHAR,          -- bullish / bearish / relative outperformance / mean reversion
    holding_period     VARCHAR,          -- e.g. intraday, 3D, 1W, 1M
    confidence_score   DOUBLE,           -- 0.0 to 1.0
    supporting_signals VARCHAR,          -- JSON: evidence summary
    status             VARCHAR   DEFAULT 'active',  -- active / archived / tested
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============  PHASE 4 — STRATEGY DISCOVERY ENGINE  ====================

-- Structured algorithmic trading strategies derived from research hypotheses
CREATE TABLE IF NOT EXISTS trading_strategies (
    strategy_id        VARCHAR   PRIMARY KEY,
    hypothesis_id      VARCHAR,              -- FK to research_hypotheses
    timestamp_created  TIMESTAMP NOT NULL,
    strategy_name      VARCHAR   NOT NULL,
    asset_scope        VARCHAR,              -- ticker(s), sector ETF, index, or macro asset class
    entry_conditions   VARCHAR   NOT NULL,   -- JSON: array of structured entry rules
    exit_conditions    VARCHAR   NOT NULL,   -- JSON: array of structured exit rules
    holding_period     VARCHAR,              -- e.g. intraday, 3D, 1W, 1M
    risk_rules         VARCHAR,              -- JSON: stop_loss, max_exposure, etc.
    position_sizing    VARCHAR,              -- JSON: sizing methodology and parameters
    volatility_filter  VARCHAR,              -- JSON: volatility regime conditions
    confidence_score   DOUBLE,               -- 0.0 to 1.0 composite ranking score
    status             VARCHAR   DEFAULT 'draft',  -- draft / validated / rejected / promoted
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===============  PHASE 5 — AUTOMATED BACKTESTING ENGINE  =================

-- Per-strategy backtest summary results
CREATE TABLE IF NOT EXISTS backtest_results (
    backtest_id        VARCHAR   PRIMARY KEY,
    strategy_id        VARCHAR   NOT NULL,
    start_date         DATE      NOT NULL,
    end_date           DATE      NOT NULL,
    total_return       DOUBLE,
    annualized_return  DOUBLE,
    sharpe_ratio       DOUBLE,
    max_drawdown       DOUBLE,
    win_rate           DOUBLE,
    profit_factor      DOUBLE,
    number_of_trades   INTEGER,
    volatility         DOUBLE,
    status             VARCHAR   DEFAULT 'completed',
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual simulated trade records
CREATE TABLE IF NOT EXISTS trade_logs (
    trade_id           VARCHAR   PRIMARY KEY,
    strategy_id        VARCHAR   NOT NULL,
    entry_timestamp    TIMESTAMP NOT NULL,
    exit_timestamp     TIMESTAMP,
    asset              VARCHAR   NOT NULL,
    entry_price        DOUBLE    NOT NULL,
    exit_price         DOUBLE,
    position_size      DOUBLE,
    pnl                DOUBLE,
    holding_period     INTEGER,           -- days
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Composite strategy performance evaluation
CREATE TABLE IF NOT EXISTS strategy_performance (
    strategy_id             VARCHAR   NOT NULL,
    backtest_id             VARCHAR   NOT NULL,
    performance_score       DOUBLE,
    risk_score              DOUBLE,
    consistency_score       DOUBLE,
    benchmark_outperformance DOUBLE,
    evaluation_notes        VARCHAR,
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (strategy_id, backtest_id)
);

-- ===============  PHASE 6 — EXPLAINABLE AI DECISION ENGINE  =================

-- Explainability insights derived from backtest performance
CREATE TABLE IF NOT EXISTS strategy_explanations (
    explanation_id          VARCHAR   PRIMARY KEY,
    strategy_id             VARCHAR   NOT NULL,
    backtest_id             VARCHAR   NOT NULL,
    timestamp               TIMESTAMP NOT NULL,
    key_signals             VARCHAR,          -- JSON array of top contributing signals
    feature_importance      VARCHAR,          -- JSON mapping features to importance scores
    shap_values             VARCHAR,          -- JSON mapping features to SHAP values
    dominant_market_factors VARCHAR,          -- JSON of macro/sector drivers
    explanation_text        VARCHAR,          -- Human-readable summary of the explanation
    confidence_score        DOUBLE,           -- 0.0 to 1.0 based on signal strength/consistency
    created_at              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

