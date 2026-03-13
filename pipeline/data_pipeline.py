"""
Data pipeline orchestrator for the Market Intelligence Layer.

Phase 5 additions: Automated Backtesting Engine integration.

Instantiates all collectors, the database manager, the Phase 2 NLP
sentiment engine components, the Phase 3 AI Research Agent,
the Phase 4 Strategy Discovery Engine, and the Phase 5 Backtesting Engine,
then drives ingestion, analysis, research, strategy, and backtesting cycles.
Supports both one-shot execution and continuous scheduling via ``schedule``.

Usage
-----
One-shot full cycle (ingest + NLP)::

    python -m pipeline.data_pipeline --once

Ingest-only::

    python -m pipeline.data_pipeline --once --ingest-only

NLP-only (sentiment + events + sector aggregation)::

    python -m pipeline.data_pipeline --nlp

Research-only (generate hypotheses from existing data)::

    python -m pipeline.data_pipeline --research

Strategy-only (convert hypotheses to strategies)::

    python -m pipeline.data_pipeline --strategy

Backtest-only (run backtests on validated strategies)::

    python -m pipeline.data_pipeline --backtest

Scheduled (continuous)::

    python -m pipeline.data_pipeline --schedule
"""

from __future__ import annotations

import argparse

import time
from datetime import datetime
from typing import Any

import schedule

from data_ingestion.stock_collector import StockCollector
from data_ingestion.news_collector import NewsCollector
from data_ingestion.macro_collector import MacroCollector
from data_ingestion.social_collector import SocialCollector
from database.db_manager import DatabaseManager
from sentiment_engine.finbert_model import FinBERTAnalyzer
from sentiment_engine.news_sentiment import NewsSentimentProcessor
from sentiment_engine.reddit_sentiment import RedditSentimentProcessor
from sentiment_engine.event_detection import EventDetector
from sentiment_engine.sector_aggregation import SectorAggregator
from research_agent.agent import ResearchAgent
from strategy_engine import StrategyDiscoveryEngine
from backtesting_engine import BacktestEngine
from utils.config import (
    PIPELINE_INTERVAL_MINUTES,
    NEWS_SENTIMENT_INTERVAL_MINUTES,
    REDDIT_SENTIMENT_INTERVAL_MINUTES,
    SECTOR_AGGREGATION_INTERVAL_MINUTES,
    RESEARCH_INTERVAL_MINUTES,
    STRATEGY_INTERVAL_MINUTES,
    BACKTEST_INTERVAL_MINUTES,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class DataPipeline:
    """Orchestrates data collection, NLP analysis, research, and storage."""

    def __init__(self) -> None:
        # Phase 1 — Data ingestion
        self.db = DatabaseManager()
        self.stock_collector = StockCollector()
        self.news_collector = NewsCollector()
        self.macro_collector = MacroCollector()
        self.social_collector = SocialCollector()

        # Phase 2 — NLP sentiment engine (shared FinBERT instance)
        self._analyzer = FinBERTAnalyzer()
        self.news_sentiment = NewsSentimentProcessor(self.db, self._analyzer)
        self.reddit_sentiment = RedditSentimentProcessor(self.db, self._analyzer)
        self.event_detector = EventDetector(self.db)
        self.sector_aggregator = SectorAggregator(self.db)

        # Phase 3 — AI Research Agent
        self._research_agent: ResearchAgent | None = None

        # Phase 4 — Strategy Discovery Engine
        self._strategy_engine: StrategyDiscoveryEngine | None = None

        # Phase 5 — Backtesting Engine
        self._backtest_engine: BacktestEngine | None = None

    # ==================================================================
    # PHASE 1 — Data ingestion
    # ==================================================================
    def run_full_ingestion(self) -> dict[str, Any]:
        """Execute one complete ingestion cycle across all sources.

        Returns
        -------
        dict
            Summary counts per source and overall duration.
        """
        start = datetime.utcnow()
        logger.info("=" * 60)
        logger.info("Starting full ingestion cycle at %s", start.isoformat())
        logger.info("=" * 60)

        # Ensure DB schema exists
        self.db.initialize()

        summary: dict[str, int] = {}

        # 1 ── Stock prices ────────────────────────────────────────────
        summary["stock_prices"] = self._ingest_stocks()

        # 2 ── Financial news ──────────────────────────────────────────
        summary["news_articles"] = self._ingest_news()

        # 3 ── Macro indicators ────────────────────────────────────────
        summary["macro_indicators"] = self._ingest_macro()

        # 4 ── Social sentiment (optional) ─────────────────────────────
        summary["social_sentiment"] = self._ingest_social()

        elapsed = (datetime.utcnow() - start).total_seconds()
        logger.info("-" * 60)
        logger.info("Ingestion cycle complete in %.1f s", elapsed)
        for source, count in summary.items():
            logger.info("  %-20s  %d records", source, count)
        logger.info("=" * 60)

        return {**summary, "elapsed_seconds": elapsed}

    # ------------------------------------------------------------------
    # Per-source helpers (each wrapped in try/except)
    # ------------------------------------------------------------------
    def _ingest_stocks(self) -> int:
        try:
            logger.info("[1/4] Collecting stock prices …")
            records = self.stock_collector.collect_all(period="1mo")
            return self.db.insert_stock_prices(records)
        except Exception as exc:
            logger.error("Stock ingestion failed: %s", exc)
            return 0

    def _ingest_news(self) -> int:
        try:
            logger.info("[2/4] Collecting news articles …")
            records = self.news_collector.collect_all()
            return self.db.insert_news_articles(records)
        except Exception as exc:
            logger.error("News ingestion failed: %s", exc)
            return 0

    def _ingest_macro(self) -> int:
        try:
            logger.info("[3/4] Collecting macro indicators …")
            records = self.macro_collector.collect_all()
            return self.db.insert_macro_indicators(records)
        except Exception as exc:
            logger.error("Macro ingestion failed: %s", exc)
            return 0

    def _ingest_social(self) -> int:
        try:
            logger.info("[4/4] Collecting social sentiment …")
            records = self.social_collector.collect_all()
            return self.db.insert_social_sentiment(records)
        except Exception as exc:
            logger.error("Social ingestion failed: %s", exc)
            return 0

    # ==================================================================
    # PHASE 2 — NLP Sentiment Analysis
    # ==================================================================
    def run_sentiment_analysis(self) -> dict[str, Any]:
        """Execute one complete NLP analysis cycle.

        Steps:
        1. News sentiment scoring (FinBERT)
        2. Reddit sentiment scoring (FinBERT + engagement weighting)
        3. Event detection (keyword pattern matching)
        4. Sector-level aggregation

        Returns
        -------
        dict
            Summary counts per NLP component and overall duration.
        """
        start = datetime.utcnow()
        logger.info("=" * 60)
        logger.info(
            "Starting NLP analysis cycle at %s", start.isoformat()
        )
        logger.info("=" * 60)

        # Ensure DB schema exists
        self.db.initialize()

        summary: dict[str, int] = {}

        # 1 ── News sentiment ──────────────────────────────────────────
        summary["news_sentiment"] = self._run_news_sentiment()

        # 2 ── Reddit sentiment ────────────────────────────────────────
        summary["reddit_sentiment"] = self._run_reddit_sentiment()

        # 3 ── Event detection ─────────────────────────────────────────
        summary["market_events"] = self._run_event_detection()

        # 4 ── Sector aggregation ──────────────────────────────────────
        summary["sector_sentiment"] = self._run_sector_aggregation()

        elapsed = (datetime.utcnow() - start).total_seconds()
        logger.info("-" * 60)
        logger.info("NLP analysis cycle complete in %.1f s", elapsed)
        for component, count in summary.items():
            logger.info("  %-20s  %d records", component, count)
        logger.info("=" * 60)

        return {**summary, "elapsed_seconds": elapsed}

    # ------------------------------------------------------------------
    # Per-component helpers
    # ------------------------------------------------------------------
    def _run_news_sentiment(self) -> int:
        try:
            logger.info("[NLP 1/4] Scoring news sentiment …")
            return self.news_sentiment.process_all()
        except Exception as exc:
            logger.error("News sentiment processing failed: %s", exc)
            return 0

    def _run_reddit_sentiment(self) -> int:
        try:
            logger.info("[NLP 2/4] Scoring Reddit sentiment …")
            return self.reddit_sentiment.process_all()
        except Exception as exc:
            logger.error("Reddit sentiment processing failed: %s", exc)
            return 0

    def _run_event_detection(self) -> int:
        try:
            logger.info("[NLP 3/4] Detecting market events …")
            return self.event_detector.detect_events()
        except Exception as exc:
            logger.error("Event detection failed: %s", exc)
            return 0

    def _run_sector_aggregation(self) -> int:
        try:
            logger.info("[NLP 4/4] Aggregating sector sentiment …")
            return self.sector_aggregator.aggregate()
        except Exception as exc:
            logger.error("Sector aggregation failed: %s", exc)
            return 0

    # ==================================================================
    # PHASE 3 — AI Research Agent
    # ==================================================================
    def run_research_agent(self) -> dict[str, Any]:
        """Execute one research agent cycle.

        Generates, ranks, filters, and persists trading hypotheses
        from the current structured data.
        """
        start = datetime.utcnow()
        logger.info("=" * 60)
        logger.info(
            "Starting research agent cycle at %s", start.isoformat()
        )
        logger.info("=" * 60)

        self.db.initialize()
        summary = self._run_research()

        elapsed = (datetime.utcnow() - start).total_seconds()
        logger.info("-" * 60)
        logger.info("Research agent cycle complete in %.1f s", elapsed)
        logger.info("  Accepted hypotheses: %d", summary.get("accepted", 0))
        logger.info("=" * 60)
        return {**summary, "elapsed_seconds": elapsed}

    def _run_research(self) -> dict[str, Any]:
        try:
            logger.info("[Research] Generating trading hypotheses …")
            if self._research_agent is None:
                self._research_agent = ResearchAgent(db=self.db)
            return self._research_agent.run()
        except Exception as exc:
            logger.error("Research agent failed: %s", exc)
            return {"accepted": 0, "error": str(exc)}

    # ==================================================================
    # PHASE 4 — Strategy Discovery Engine
    # ==================================================================
    def run_strategy_discovery(self) -> dict[str, Any]:
        """Execute one strategy discovery cycle.

        Converts active research hypotheses into structured
        algorithmic trading strategies.
        """
        start = datetime.utcnow()
        logger.info("=" * 60)
        logger.info(
            "Starting strategy discovery at %s", start.isoformat()
        )
        logger.info("=" * 60)

        self.db.initialize()
        summary = self._run_strategy_discovery()

        elapsed = (datetime.utcnow() - start).total_seconds()
        logger.info("-" * 60)
        logger.info("Strategy discovery complete in %.1f s", elapsed)
        logger.info(
            "  Strategies created: %d", summary.get("inserted", 0)
        )
        logger.info("=" * 60)
        return {**summary, "elapsed_seconds": elapsed}

    def _run_strategy_discovery(self) -> dict[str, Any]:
        try:
            logger.info("[Strategy] Converting hypotheses to strategies …")
            if self._strategy_engine is None:
                self._strategy_engine = StrategyDiscoveryEngine(db=self.db)
            return self._strategy_engine.run()
        except Exception as exc:
            logger.error("Strategy discovery failed: %s", exc)
            return {"inserted": 0, "error": str(exc)}

    # ==================================================================
    # PHASE 5 — Automated Backtesting Engine
    # ==================================================================
    def run_backtesting(self) -> dict[str, Any]:
        """Execute one backtesting cycle.

        Evaluates validated strategies against historical data
        and computes performance metrics.
        """
        start = datetime.utcnow()
        logger.info("=" * 60)
        logger.info(
            "Starting backtesting engine at %s", start.isoformat()
        )
        logger.info("=" * 60)

        self.db.initialize()
        summary = self._run_backtesting()

        elapsed = (datetime.utcnow() - start).total_seconds()
        logger.info("-" * 60)
        logger.info("Backtesting complete in %.1f s", elapsed)
        logger.info(
            "  Backtests completed: %d",
            summary.get("backtests_completed", 0),
        )
        logger.info("=" * 60)
        return {**summary, "elapsed_seconds": elapsed}

    def _run_backtesting(self) -> dict[str, Any]:
        try:
            logger.info("[Backtest] Evaluating validated strategies …")
            if self._backtest_engine is None:
                self._backtest_engine = BacktestEngine(db=self.db)
            return self._backtest_engine.run()
        except Exception as exc:
            logger.error("Backtesting failed: %s", exc)
            return {"backtests_completed": 0, "error": str(exc)}

    # ==================================================================
    # Combined cycle
    # ==================================================================
    def run_full_cycle(self) -> dict[str, Any]:
        """Run full ingestion → NLP → research → strategy → backtest."""
        ingestion = self.run_full_ingestion()
        nlp = self.run_sentiment_analysis()
        research = self.run_research_agent()
        strategy = self.run_strategy_discovery()
        backtest = self.run_backtesting()
        return {
            "ingestion": ingestion, "nlp": nlp,
            "research": research, "strategy": strategy,
            "backtest": backtest,
        }

    # ==================================================================
    # Scheduling
    # ==================================================================
    def run_scheduled(self) -> None:
        """Run ingestion + NLP on repeating schedules (blocks forever).

        Schedule breakdown:
        - Data ingestion:     every PIPELINE_INTERVAL_MINUTES (default 60m)
        - News sentiment:     every NEWS_SENTIMENT_INTERVAL_MINUTES (60m)
        - Reddit sentiment:   every REDDIT_SENTIMENT_INTERVAL_MINUTES (30m)
        - Sector aggregation: every SECTOR_AGGREGATION_INTERVAL_MINUTES (1440m = daily)
        """
        logger.info("Setting up scheduled pipeline:")
        logger.info(
            "  Data ingestion:      every %d min", PIPELINE_INTERVAL_MINUTES
        )
        logger.info(
            "  News sentiment:      every %d min",
            NEWS_SENTIMENT_INTERVAL_MINUTES,
        )
        logger.info(
            "  Reddit sentiment:    every %d min",
            REDDIT_SENTIMENT_INTERVAL_MINUTES,
        )
        logger.info(
            "  Sector aggregation:  every %d min",
            SECTOR_AGGREGATION_INTERVAL_MINUTES,
        )
        logger.info(
            "  Research agent:      every %d min",
            RESEARCH_INTERVAL_MINUTES,
        )
        logger.info(
            "  Strategy discovery:  every %d min",
            STRATEGY_INTERVAL_MINUTES,
        )
        logger.info(
            "  Backtesting engine:  every %d min",
            BACKTEST_INTERVAL_MINUTES,
        )
        logger.info("Press Ctrl+C to stop.\n")

        # Ensure DB schema exists
        self.db.initialize()

        # Run everything once immediately on start
        self.run_full_cycle()

        # Register individual schedules
        schedule.every(PIPELINE_INTERVAL_MINUTES).minutes.do(
            self.run_full_ingestion
        )
        schedule.every(NEWS_SENTIMENT_INTERVAL_MINUTES).minutes.do(
            self._run_news_sentiment
        )
        schedule.every(REDDIT_SENTIMENT_INTERVAL_MINUTES).minutes.do(
            self._run_reddit_sentiment
        )
        schedule.every(SECTOR_AGGREGATION_INTERVAL_MINUTES).minutes.do(
            self._run_sector_aggregation
        )
        # Event detection runs after each news-sentiment pass
        schedule.every(NEWS_SENTIMENT_INTERVAL_MINUTES).minutes.do(
            self._run_event_detection
        )
        # Research agent
        schedule.every(RESEARCH_INTERVAL_MINUTES).minutes.do(
            self._run_research
        )
        # Strategy discovery
        schedule.every(STRATEGY_INTERVAL_MINUTES).minutes.do(
            self._run_strategy_discovery
        )
        # Backtesting engine
        schedule.every(BACKTEST_INTERVAL_MINUTES).minutes.do(
            self._run_backtesting
        )

        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user.")
        finally:
            self.db.close()


# ======================================================================
# CLI entry-point
# ======================================================================
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Market Intelligence Layer — Data Pipeline (Phase 1-5)"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--once",
        action="store_true",
        help="Run a single full cycle (ingest + NLP + research + strategy + backtest) and exit.",
    )
    group.add_argument(
        "--schedule",
        action="store_true",
        help="Run on repeating schedules (see config for intervals).",
    )
    group.add_argument(
        "--nlp",
        action="store_true",
        help="Run only the NLP sentiment analysis (no data ingestion).",
    )
    group.add_argument(
        "--research",
        action="store_true",
        help="Run only the AI research agent (hypothesis generation).",
    )
    group.add_argument(
        "--strategy",
        action="store_true",
        help="Run only strategy discovery (hypothesis → strategy conversion).",
    )
    group.add_argument(
        "--backtest",
        action="store_true",
        help="Run only backtesting on validated strategies.",
    )

    parser.add_argument(
        "--ingest-only",
        action="store_true",
        help="With --once: skip NLP and research, only run data ingestion.",
    )

    args = parser.parse_args()

    pipeline = DataPipeline()

    if args.once:
        if args.ingest_only:
            pipeline.run_full_ingestion()
        else:
            pipeline.run_full_cycle()
        pipeline.db.close()
    elif args.nlp:
        pipeline.run_sentiment_analysis()
        pipeline.db.close()
    elif args.research:
        pipeline.run_research_agent()
        pipeline.db.close()
    elif args.strategy:
        pipeline.run_strategy_discovery()
        pipeline.db.close()
    elif args.backtest:
        pipeline.run_backtesting()
        pipeline.db.close()
    else:
        pipeline.run_scheduled()


if __name__ == "__main__":
    main()
