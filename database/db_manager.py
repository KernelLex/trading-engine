"""
Database manager for the Market Intelligence Layer.

Wraps a DuckDB connection and provides typed insert helpers for each table.
Uses INSERT OR IGNORE semantics (via ON CONFLICT DO NOTHING) to handle
duplicate records idempotently.

Phase 3 additions: helpers for research_hypotheses and bulk signal queries.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Any

import duckdb

from utils.config import DUCKDB_PATH, SCHEMA_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Thin wrapper around a DuckDB connection for the market-research DB."""

    def __init__(self, db_path: str | None = None) -> None:
        self.db_path = db_path or DUCKDB_PATH
        self._conn: duckdb.DuckDBPyConnection | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    def connect(self) -> None:
        """Open (or create) the DuckDB database file."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = duckdb.connect(self.db_path)
        logger.info("Connected to DuckDB at %s", self.db_path)

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
            logger.info("DuckDB connection closed.")

    @property
    def conn(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self.connect()
        return self._conn  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Schema initialisation
    # ------------------------------------------------------------------
    def initialize(self) -> None:
        """Run schema.sql to create tables (idempotent)."""
        schema_sql = Path(SCHEMA_PATH).read_text(encoding="utf-8")
        # DuckDB needs statements executed one at a time
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                self.conn.execute(stmt)
        logger.info("Database schema initialised.")

    # ==================================================================
    # PHASE 1 — Insert helpers
    # ==================================================================
    def insert_stock_prices(self, records: list[dict[str, Any]]) -> int:
        """Insert OHLCV records.  Duplicates (ticker+date) are ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO stock_prices
                (ticker, date, open, high, low, close, volume, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["ticker"], r["date"],
                r.get("open"), r.get("high"), r.get("low"),
                r.get("close"), r.get("volume"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d stock-price records.", len(rows))
        return len(rows)

    def insert_news_articles(self, records: list[dict[str, Any]]) -> int:
        """Insert news articles.  Duplicates (article_id) are ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO news_articles
                (article_id, title, description, source_name, url,
                 published_at, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["article_id"], r.get("title"), r.get("description"),
                r.get("source_name"), r.get("url"),
                r.get("published_at"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d news-article records.", len(rows))
        return len(rows)

    def insert_macro_indicators(self, records: list[dict[str, Any]]) -> int:
        """Insert macro-indicator observations.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO macro_indicators
                (series_id, indicator_name, date, value, ingested_at)
            VALUES (?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["series_id"], r.get("indicator_name"), r["date"],
                r.get("value"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d macro-indicator records.", len(rows))
        return len(rows)

    def insert_social_sentiment(self, records: list[dict[str, Any]]) -> int:
        """Insert Reddit posts.  Duplicates (post_id) are ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO social_sentiment
                (post_id, subreddit, title, selftext, score,
                 num_comments, created_utc, ingested_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["post_id"], r.get("subreddit"), r.get("title"),
                r.get("selftext"), r.get("score"), r.get("num_comments"),
                r.get("created_utc"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d social-sentiment records.", len(rows))
        return len(rows)

    # ==================================================================
    # PHASE 2 — NLP Insert helpers
    # ==================================================================
    def insert_news_sentiment(self, records: list[dict[str, Any]]) -> int:
        """Insert news sentiment results.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO news_sentiment
                (article_id, timestamp, headline, sentiment_label,
                 sentiment_score, entities_detected, related_tickers,
                 processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["article_id"], r.get("timestamp"), r.get("headline"),
                r.get("sentiment_label"), r.get("sentiment_score"),
                r.get("entities_detected"), r.get("related_tickers"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d news-sentiment records.", len(rows))
        return len(rows)

    def insert_social_sentiment_scores(
        self, records: list[dict[str, Any]]
    ) -> int:
        """Insert Reddit sentiment scores.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO social_sentiment_scores
                (post_id, subreddit, timestamp, sentiment_label,
                 sentiment_score, engagement_score, tickers_detected,
                 processed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["post_id"], r.get("subreddit"), r.get("timestamp"),
                r.get("sentiment_label"), r.get("sentiment_score"),
                r.get("engagement_score"), r.get("tickers_detected"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d social-sentiment-score records.", len(rows))
        return len(rows)

    def insert_sector_sentiment(self, records: list[dict[str, Any]]) -> int:
        """Insert sector-level aggregated sentiment.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO sector_sentiment
                (sector, timestamp, avg_sentiment_score,
                 news_signal_strength, social_signal_strength, processed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["sector"], r["timestamp"], r.get("avg_sentiment_score"),
                r.get("news_signal_strength"),
                r.get("social_signal_strength"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d sector-sentiment records.", len(rows))
        return len(rows)

    def insert_market_events(self, records: list[dict[str, Any]]) -> int:
        """Insert detected market events.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO market_events
                (event_id, timestamp, event_type, related_tickers,
                 confidence_score, source_article_id, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = datetime.utcnow()
        rows = [
            (
                r["event_id"], r.get("timestamp"), r.get("event_type"),
                r.get("related_tickers"), r.get("confidence_score"),
                r.get("source_article_id"), now,
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d market-event records.", len(rows))
        return len(rows)

    # ==================================================================
    # PHASE 2 — Query helpers (fetch unprocessed rows)
    # ==================================================================
    def fetch_unprocessed_news(self) -> list[dict[str, Any]]:
        """Return news articles that have not yet been sentiment-scored."""
        sql = """
            SELECT a.article_id, a.title, a.description,
                   a.source_name, a.published_at
            FROM   news_articles a
            LEFT JOIN news_sentiment ns ON a.article_id = ns.article_id
            WHERE  ns.article_id IS NULL
        """
        rows = self.conn.execute(sql).fetchall()
        cols = ["article_id", "title", "description",
                "source_name", "published_at"]
        results = [dict(zip(cols, row)) for row in rows]
        logger.info("Found %d unprocessed news articles.", len(results))
        return results

    def fetch_unprocessed_social(self) -> list[dict[str, Any]]:
        """Return Reddit posts that have not yet been sentiment-scored."""
        sql = """
            SELECT s.post_id, s.subreddit, s.title, s.selftext,
                   s.score, s.num_comments, s.created_utc
            FROM   social_sentiment s
            LEFT JOIN social_sentiment_scores ss ON s.post_id = ss.post_id
            WHERE  ss.post_id IS NULL
        """
        rows = self.conn.execute(sql).fetchall()
        cols = ["post_id", "subreddit", "title", "selftext",
                "score", "num_comments", "created_utc"]
        results = [dict(zip(cols, row)) for row in rows]
        logger.info("Found %d unprocessed social posts.", len(results))
        return results

    def fetch_recent_news_sentiment(
        self, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Return news-sentiment rows from the last *hours* hours."""
        sql = """
            SELECT article_id, timestamp, headline, sentiment_label,
                   sentiment_score, entities_detected, related_tickers
            FROM   news_sentiment
            WHERE  processed_at >= CURRENT_TIMESTAMP - INTERVAL ? HOUR
        """
        rows = self.conn.execute(sql, [hours]).fetchall()
        cols = ["article_id", "timestamp", "headline", "sentiment_label",
                "sentiment_score", "entities_detected", "related_tickers"]
        return [dict(zip(cols, row)) for row in rows]

    def fetch_recent_social_sentiment(
        self, hours: int = 24
    ) -> list[dict[str, Any]]:
        """Return social-sentiment-score rows from the last *hours* hours."""
        sql = """
            SELECT post_id, subreddit, timestamp, sentiment_label,
                   sentiment_score, engagement_score, tickers_detected
            FROM   social_sentiment_scores
            WHERE  processed_at >= CURRENT_TIMESTAMP - INTERVAL ? HOUR
        """
        rows = self.conn.execute(sql, [hours]).fetchall()
        cols = ["post_id", "subreddit", "timestamp", "sentiment_label",
                "sentiment_score", "engagement_score", "tickers_detected"]
        return [dict(zip(cols, row)) for row in rows]

    # ==================================================================
    # PHASE 3 — Research Agent helpers
    # ==================================================================
    def insert_research_hypotheses(
        self, records: list[dict[str, Any]]
    ) -> int:
        """Insert research hypotheses.  Duplicates (hypothesis_id) ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO research_hypotheses
                (hypothesis_id, timestamp, title, hypothesis_text,
                 asset_scope, sector, trigger_conditions,
                 expected_direction, holding_period, confidence_score,
                 supporting_signals, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r["hypothesis_id"], r["timestamp"], r["title"],
                r["hypothesis_text"], r.get("asset_scope"),
                r.get("sector"), r.get("trigger_conditions"),
                r.get("expected_direction"), r.get("holding_period"),
                r.get("confidence_score"), r.get("supporting_signals"),
                r.get("status", "active"),
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d research-hypothesis records.", len(rows))
        return len(rows)

    def fetch_recent_hypotheses(
        self, hours: int = 48
    ) -> list[dict[str, Any]]:
        """Return recent hypotheses for deduplication checks."""
        sql = f"""
            SELECT hypothesis_id, title, hypothesis_text, asset_scope,
                   sector, expected_direction, holding_period,
                   confidence_score, status
            FROM   research_hypotheses
            WHERE  created_at >= CURRENT_TIMESTAMP - INTERVAL '{int(hours)} HOURS'
        """
        rows = self.conn.execute(sql).fetchall()
        cols = [
            "hypothesis_id", "title", "hypothesis_text", "asset_scope",
            "sector", "expected_direction", "holding_period",
            "confidence_score", "status",
        ]
        return [dict(zip(cols, row)) for row in rows]

    def fetch_signal_data(
        self, lookback_hours: int = 72
    ) -> dict[str, list[dict[str, Any]]]:
        """Pull recent rows from all six input tables for the research agent.

        Returns
        -------
        dict
            Keys: stock_prices, macro_indicators, news_sentiment,
                  social_sentiment_scores, sector_sentiment, market_events.
            Values: list of row-dicts.
        """
        result: dict[str, list[dict[str, Any]]] = {}

        # --- stock_prices (use date column) ---
        days = max(lookback_hours // 24, 1)
        sp_sql = f"""
            SELECT ticker, date, open, high, low, close, volume
            FROM   stock_prices
            WHERE  date >= CURRENT_DATE - INTERVAL '{int(days)} DAYS'
            ORDER BY ticker, date
        """
        sp_rows = self.conn.execute(sp_sql).fetchall()
        sp_cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
        result["stock_prices"] = [dict(zip(sp_cols, r)) for r in sp_rows]

        # --- macro_indicators ---
        mi_sql = f"""
            SELECT series_id, indicator_name, date, value
            FROM   macro_indicators
            WHERE  date >= CURRENT_DATE - INTERVAL '{int(days)} DAYS'
            ORDER BY series_id, date
        """
        mi_rows = self.conn.execute(mi_sql).fetchall()
        mi_cols = ["series_id", "indicator_name", "date", "value"]
        result["macro_indicators"] = [dict(zip(mi_cols, r)) for r in mi_rows]

        # --- news_sentiment ---
        ns_sql = f"""
            SELECT article_id, timestamp, headline, sentiment_label,
                   sentiment_score, entities_detected, related_tickers
            FROM   news_sentiment
            WHERE  processed_at >= CURRENT_TIMESTAMP - INTERVAL '{int(lookback_hours)} HOURS'
            ORDER BY timestamp DESC
        """
        ns_rows = self.conn.execute(ns_sql).fetchall()
        ns_cols = [
            "article_id", "timestamp", "headline", "sentiment_label",
            "sentiment_score", "entities_detected", "related_tickers",
        ]
        result["news_sentiment"] = [dict(zip(ns_cols, r)) for r in ns_rows]

        # --- social_sentiment_scores ---
        ss_sql = f"""
            SELECT post_id, subreddit, timestamp, sentiment_label,
                   sentiment_score, engagement_score, tickers_detected
            FROM   social_sentiment_scores
            WHERE  processed_at >= CURRENT_TIMESTAMP - INTERVAL '{int(lookback_hours)} HOURS'
            ORDER BY timestamp DESC
        """
        ss_rows = self.conn.execute(ss_sql).fetchall()
        ss_cols = [
            "post_id", "subreddit", "timestamp", "sentiment_label",
            "sentiment_score", "engagement_score", "tickers_detected",
        ]
        result["social_sentiment_scores"] = [
            dict(zip(ss_cols, r)) for r in ss_rows
        ]

        # --- sector_sentiment ---
        sec_sql = f"""
            SELECT sector, timestamp, avg_sentiment_score,
                   news_signal_strength, social_signal_strength
            FROM   sector_sentiment
            WHERE  processed_at >= CURRENT_TIMESTAMP - INTERVAL '{int(lookback_hours)} HOURS'
            ORDER BY sector, timestamp DESC
        """
        sec_rows = self.conn.execute(sec_sql).fetchall()
        sec_cols = [
            "sector", "timestamp", "avg_sentiment_score",
            "news_signal_strength", "social_signal_strength",
        ]
        result["sector_sentiment"] = [
            dict(zip(sec_cols, r)) for r in sec_rows
        ]

        # --- market_events ---
        me_sql = f"""
            SELECT event_id, timestamp, event_type, related_tickers,
                   confidence_score, source_article_id
            FROM   market_events
            WHERE  detected_at >= CURRENT_TIMESTAMP - INTERVAL '{int(lookback_hours)} HOURS'
            ORDER BY timestamp DESC
        """
        me_rows = self.conn.execute(me_sql).fetchall()
        me_cols = [
            "event_id", "timestamp", "event_type", "related_tickers",
            "confidence_score", "source_article_id",
        ]
        result["market_events"] = [dict(zip(me_cols, r)) for r in me_rows]

        logger.info(
            "Fetched signal data: %s",
            {k: len(v) for k, v in result.items()},
        )
        return result

    # ==================================================================
    # PHASE 4 — Strategy Discovery Engine helpers
    # ==================================================================
    def insert_trading_strategies(
        self, records: list[dict[str, Any]]
    ) -> int:
        """Insert trading strategies.  Duplicates (strategy_id) ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO trading_strategies
                (strategy_id, hypothesis_id, timestamp_created,
                 strategy_name, asset_scope, entry_conditions,
                 exit_conditions, holding_period, risk_rules,
                 position_sizing, volatility_filter,
                 confidence_score, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r["strategy_id"], r.get("hypothesis_id"),
                r["timestamp_created"], r["strategy_name"],
                r.get("asset_scope"), r["entry_conditions"],
                r["exit_conditions"], r.get("holding_period"),
                r.get("risk_rules"), r.get("position_sizing"),
                r.get("volatility_filter"), r.get("confidence_score"),
                r.get("status", "draft"),
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d trading-strategy records.", len(rows))
        return len(rows)

    def fetch_active_hypotheses(self) -> list[dict[str, Any]]:
        """Return hypotheses with status='active' not yet converted to strategies."""
        sql = """
            SELECT h.hypothesis_id, h.timestamp, h.title,
                   h.hypothesis_text, h.asset_scope, h.sector,
                   h.trigger_conditions, h.expected_direction,
                   h.holding_period, h.confidence_score,
                   h.supporting_signals, h.status
            FROM   research_hypotheses h
            LEFT JOIN trading_strategies ts
                ON h.hypothesis_id = ts.hypothesis_id
            WHERE  h.status = 'active'
              AND  ts.strategy_id IS NULL
            ORDER BY h.confidence_score DESC
        """
        rows = self.conn.execute(sql).fetchall()
        cols = [
            "hypothesis_id", "timestamp", "title", "hypothesis_text",
            "asset_scope", "sector", "trigger_conditions",
            "expected_direction", "holding_period", "confidence_score",
            "supporting_signals", "status",
        ]
        results = [dict(zip(cols, row)) for row in rows]
        logger.info("Found %d active unconverted hypotheses.", len(results))
        return results

    def fetch_recent_strategies(
        self, hours: int = 48
    ) -> list[dict[str, Any]]:
        """Return recent strategies for deduplication checks."""
        sql = f"""
            SELECT strategy_id, hypothesis_id, strategy_name,
                   asset_scope, entry_conditions, exit_conditions,
                   holding_period, confidence_score, status
            FROM   trading_strategies
            WHERE  created_at >= CURRENT_TIMESTAMP - INTERVAL '{int(hours)} HOURS'
        """
        rows = self.conn.execute(sql).fetchall()
        cols = [
            "strategy_id", "hypothesis_id", "strategy_name",
            "asset_scope", "entry_conditions", "exit_conditions",
            "holding_period", "confidence_score", "status",
        ]
        return [dict(zip(cols, row)) for row in rows]

    def update_hypothesis_status(
        self, hypothesis_id: str, status: str
    ) -> None:
        """Update the status of a research hypothesis (e.g. 'tested')."""
        sql = """
            UPDATE research_hypotheses
            SET    status = ?
            WHERE  hypothesis_id = ?
        """
        self.conn.execute(sql, [status, hypothesis_id])
        logger.debug(
            "Updated hypothesis %s status to '%s'.", hypothesis_id, status,
        )

    # ==================================================================
    # PHASE 5 — Backtesting Engine helpers
    # ==================================================================
    def insert_backtest_results(
        self, records: list[dict[str, Any]]
    ) -> int:
        """Insert backtest result summaries.  Duplicates (backtest_id) ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO backtest_results
                (backtest_id, strategy_id, start_date, end_date,
                 total_return, annualized_return, sharpe_ratio,
                 max_drawdown, win_rate, profit_factor,
                 number_of_trades, volatility, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r["backtest_id"], r["strategy_id"], r["start_date"],
                r["end_date"], r.get("total_return"),
                r.get("annualized_return"), r.get("sharpe_ratio"),
                r.get("max_drawdown"), r.get("win_rate"),
                r.get("profit_factor"), r.get("number_of_trades"),
                r.get("volatility"), r.get("status", "completed"),
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d backtest-result records.", len(rows))
        return len(rows)

    def insert_trade_logs(self, records: list[dict[str, Any]]) -> int:
        """Insert individual trade log records.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO trade_logs
                (trade_id, strategy_id, entry_timestamp, exit_timestamp,
                 asset, entry_price, exit_price, position_size,
                 pnl, holding_period)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r["trade_id"], r["strategy_id"], r["entry_timestamp"],
                r.get("exit_timestamp"), r["asset"], r["entry_price"],
                r.get("exit_price"), r.get("position_size"),
                r.get("pnl"), r.get("holding_period"),
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d trade-log records.", len(rows))
        return len(rows)

    def insert_strategy_performance(
        self, records: list[dict[str, Any]]
    ) -> int:
        """Insert strategy performance evaluations.  Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO strategy_performance
                (strategy_id, backtest_id, performance_score,
                 risk_score, consistency_score,
                 benchmark_outperformance, evaluation_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r["strategy_id"], r["backtest_id"],
                r.get("performance_score"), r.get("risk_score"),
                r.get("consistency_score"),
                r.get("benchmark_outperformance"),
                r.get("evaluation_notes"),
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d strategy-performance records.", len(rows))
        return len(rows)

    def fetch_validated_strategies(self) -> list[dict[str, Any]]:
        """Return strategies with status='validated' not yet backtested."""
        sql = """
            SELECT ts.strategy_id, ts.hypothesis_id,
                   ts.timestamp_created, ts.strategy_name,
                   ts.asset_scope, ts.entry_conditions,
                   ts.exit_conditions, ts.holding_period,
                   ts.risk_rules, ts.position_sizing,
                   ts.volatility_filter, ts.confidence_score, ts.status
            FROM   trading_strategies ts
            LEFT JOIN backtest_results br
                ON ts.strategy_id = br.strategy_id
            WHERE  ts.status = 'validated'
              AND  br.backtest_id IS NULL
            ORDER BY ts.confidence_score DESC
        """
        rows = self.conn.execute(sql).fetchall()
        cols = [
            "strategy_id", "hypothesis_id", "timestamp_created",
            "strategy_name", "asset_scope", "entry_conditions",
            "exit_conditions", "holding_period", "risk_rules",
            "position_sizing", "volatility_filter",
            "confidence_score", "status",
        ]
        results = [dict(zip(cols, row)) for row in rows]
        logger.info("Found %d validated un-backtested strategies.", len(results))
        return results

    def fetch_stock_prices_for_backtest(
        self,
        ticker: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return OHLCV data for a ticker within a date range."""
        conditions = ["ticker = ?"]
        params: list[Any] = [ticker]
        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)
        where = " AND ".join(conditions)
        sql = f"""
            SELECT ticker, date, open, high, low, close, volume
            FROM   stock_prices
            WHERE  {where}
            ORDER BY date ASC
        """
        rows = self.conn.execute(sql, params).fetchall()
        cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
        return [dict(zip(cols, row)) for row in rows]

    def update_strategy_status(
        self, strategy_id: str, status: str
    ) -> None:
        """Update the status of a trading strategy."""
        sql = """
            UPDATE trading_strategies
            SET    status = ?
            WHERE  strategy_id = ?
        """
        self.conn.execute(sql, [status, strategy_id])
        logger.debug(
            "Updated strategy %s status to '%s'.", strategy_id, status,
        )

    # ==================================================================
    # PHASE 6 — Explainability Engine helpers
    # ==================================================================
    def insert_strategy_explanations(
        self, records: list[dict[str, Any]]
    ) -> int:
        """Insert strategy explainability records. Duplicates ignored."""
        if not records:
            return 0
        sql = """
            INSERT OR IGNORE INTO strategy_explanations
                (explanation_id, strategy_id, backtest_id, timestamp,
                 key_signals, feature_importance, shap_values,
                 dominant_market_factors, explanation_text,
                 confidence_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        rows = [
            (
                r["explanation_id"], r["strategy_id"], r["backtest_id"],
                r["timestamp"], r.get("key_signals"),
                r.get("feature_importance"), r.get("shap_values"),
                r.get("dominant_market_factors"),
                r.get("explanation_text"), r.get("confidence_score"),
            )
            for r in records
        ]
        self.conn.executemany(sql, rows)
        logger.info("Inserted %d strategy-explanation records.", len(rows))
        return len(rows)
