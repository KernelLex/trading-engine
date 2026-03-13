
from typing import Any, List, Dict
import duckdb
import pandas as pd
from utils.config import DUCKDB_PATH

class DBQueries:
    def __init__(self, db_path: str = DUCKDB_PATH):
        self.db_path = db_path
        
    def _get_connection(self):
        # We need a fresh connection per request or a pool
        # DuckDB in concurrent setting can be tricky if using read/write
        # For our dashboard, it's mostly read-only, so we'll use read_only=True if possible
        # However, to be safe and simple with the existing DB path:
        return duckdb.connect(self.db_path, read_only=True)

    def _execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        try:
            with self._get_connection() as conn:
                df = conn.execute(query, params).fetchdf()
                # Convert timestamps to strings for JSON serialization
                for col in df.select_dtypes(include=['datetime64[ns]']).columns:
                    df[col] = df[col].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
                # Replace NaNs with None
                df = df.where(pd.notnull(df), None)
                return df.to_dict(orient='records')
        except Exception as e:
            print(f"DB Error: {e}")
            return []

    def get_market_sentiment(self) -> Dict[str, Any]:
        """Fetch sector trends and recent news/social sentiment"""
        # Sector Sentiment trend (last 30 days roughly)
        sector_query = """
            SELECT sector, DATE_TRUNC('day', timestamp) as date,
                   AVG(avg_sentiment_score) as sentiment
            FROM sector_sentiment
            GROUP BY 1, 2
            ORDER BY 2 DESC, 1
            LIMIT 100
        """
        sector_sentiment = self._execute_query(sector_query)

        # Recent News
        news_query = """
            SELECT headline, sentiment_label, sentiment_score, timestamp
            FROM news_sentiment
            ORDER BY timestamp DESC
            LIMIT 50
        """
        news_sentiment = self._execute_query(news_query)

        # Recent Social
        social_query = """
            SELECT subreddit, sentiment_label, sentiment_score, timestamp
            FROM social_sentiment_scores
            ORDER BY timestamp DESC
            LIMIT 50
        """
        social_sentiment = self._execute_query(social_query)

        return {
            "sector_sentiment": sector_sentiment,
            "news_sentiment": news_sentiment,
            "social_sentiment": social_sentiment
        }

    def get_macro_events(self) -> Dict[str, Any]:
        """Fetch macro indicators and market events"""
        macro_query = """
            SELECT series_id, indicator_name, date, value
            FROM macro_indicators
            ORDER BY date DESC
            LIMIT 100
        """
        macro = self._execute_query(macro_query)

        events_query = """
            SELECT event_type, timestamp, related_tickers, confidence_score
            FROM market_events
            ORDER BY timestamp DESC
            LIMIT 50
        """
        events = self._execute_query(events_query)

        return {
            "macro_indicators": macro,
            "market_events": events
        }

    def get_research_hypotheses(self) -> List[Dict[str, Any]]:
        query = """
            SELECT hypothesis_id, title, confidence_score, trigger_conditions, expected_direction, supporting_signals, sector, holding_period
            FROM research_hypotheses
            ORDER BY timestamp DESC
            LIMIT 50
        """
        return self._execute_query(query)

    def get_trading_strategies(self) -> List[Dict[str, Any]]:
        query = """
            SELECT strategy_id, strategy_name, asset_scope, entry_conditions, exit_conditions, risk_rules, confidence_score, status
            FROM trading_strategies
            ORDER BY timestamp_created DESC
            LIMIT 50
        """
        return self._execute_query(query)

    def get_backtest_performance(self) -> List[Dict[str, Any]]:
        query = """
            SELECT br.backtest_id, br.strategy_id, br.start_date, br.end_date, 
                   br.total_return, br.sharpe_ratio, br.max_drawdown, br.win_rate,
                   ts.strategy_name
            FROM backtest_results br
            JOIN trading_strategies ts ON br.strategy_id = ts.strategy_id
            ORDER BY br.created_at DESC
            LIMIT 50
        """
        return self._execute_query(query)

    def get_strategy_explanations(self) -> List[Dict[str, Any]]:
        query = """
            SELECT se.explanation_id, se.strategy_id, se.timestamp, se.explanation_text, 
                   se.confidence_score, se.dominant_market_factors, se.shap_values, se.key_signals,
                   ts.strategy_name
            FROM strategy_explanations se
            JOIN trading_strategies ts ON se.strategy_id = ts.strategy_id
            ORDER BY se.timestamp DESC
            LIMIT 50
        """
        res = self._execute_query(query)
        # Parse JSON strings to objects where needed for the frontend
        import json
        for row in res:
            try:
                row['dominant_market_factors'] = json.loads(row.get('dominant_market_factors') or '{}')
                row['shap_values'] = json.loads(row.get('shap_values') or '{}')
                row['key_signals'] = json.loads(row.get('key_signals') or '[]')
            except:
                pass
        return res

    def get_trade_simulations(self, strategy_id: str) -> Dict[str, Any]:
        # Get trades
        trades_query = """
            SELECT trade_id, asset, entry_timestamp, exit_timestamp, entry_price, exit_price, pnl, holding_period
            FROM trade_logs
            WHERE strategy_id = ?
            ORDER BY entry_timestamp ASC
        """
        trades = self._execute_query(trades_query, (strategy_id,))
        
        # Get price data for that asset during the trade period (approx)
        price_data = []
        if trades:
            asset = trades[0]['asset']
            import pandas as pd
            start = pd.to_datetime(trades[0]['entry_timestamp']) - pd.Timedelta(days=10)
            end = pd.to_datetime(trades[-1]['entry_timestamp']) + pd.Timedelta(days=10)
            
            price_query = """
                SELECT date, close
                FROM stock_prices
                WHERE ticker = ? AND date >= ? AND date <= ?
                ORDER BY date ASC
            """
            price_data = self._execute_query(price_query, (asset, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')))

        return {
            "trades": trades,
            "prices": price_data
        }
