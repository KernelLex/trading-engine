import duckdb
import uuid
from datetime import datetime
import json

def insert_mock_strategies():
    conn = duckdb.connect('data/market_research.duckdb')
    
    # Check if we already mocked them
    count = conn.execute("SELECT count(*) FROM trading_strategies").fetchone()[0]
    if count > 0:
        print("Strategies already exist.")
        return

    strategies = [
        {
            "strategy_id": str(uuid.uuid4()),
            "hypothesis_id": str(uuid.uuid4()),  # Fake
            "timestamp_created": datetime.utcnow().isoformat(),
            "strategy_name": "Tech Momentum Bounce",
            "asset_scope": "AAPL",
            "entry_conditions": json.dumps([{"type": "momentum", "metric": "returns_5d", "operator": ">", "value": 0}]),
            "exit_conditions": json.dumps([{"type": "time_based", "holding_period_days": 3}]),
            "holding_period": "3D",
            "risk_rules": json.dumps({"stop_loss_pct": 0.05, "take_profit_pct": 0.1}),
            "position_sizing": json.dumps({"type": "fixed", "value": 0.1}),
            "volatility_filter": json.dumps({"status": "active"}),
            "confidence_score": 0.85,
            "status": "validated",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "strategy_id": str(uuid.uuid4()),
            "hypothesis_id": str(uuid.uuid4()),  # Fake
            "timestamp_created": datetime.utcnow().isoformat(),
            "strategy_name": "Market Reversion Scalp",
            "asset_scope": "SPY",
            "entry_conditions": json.dumps([{"type": "mean_reversion", "metric": "rsi_14", "operator": ">", "value": 70}]),
            "exit_conditions": json.dumps([{"type": "mean_reversion", "metric": "rsi_14", "operator": "<", "value": 50}]),
            "holding_period": "1W",
            "risk_rules": json.dumps({"stop_loss_pct": 0.02, "take_profit_pct": 0.04}),
            "position_sizing": json.dumps({"type": "kelly", "fraction": 0.5}),
            "volatility_filter": json.dumps({}),
            "confidence_score": 0.75,
            "status": "validated",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "strategy_id": str(uuid.uuid4()),
            "hypothesis_id": str(uuid.uuid4()),  # Fake
            "timestamp_created": datetime.utcnow().isoformat(),
            "strategy_name": "Sentiment Divergence MSFT",
            "asset_scope": "MSFT",
            "entry_conditions": json.dumps([{"type": "sentiment", "source": "news", "metric": "sentiment_score", "operator": ">", "value": 0.6}]),
            "exit_conditions": json.dumps([{"type": "momentum", "metric": "returns_1d", "operator": "<", "value": 0}]),
            "holding_period": "1W",
            "risk_rules": json.dumps({"stop_loss_pct": 0.08, "take_profit_pct": 0.15}),
            "position_sizing": json.dumps({"type": "fixed", "value": 0.2}),
            "volatility_filter": json.dumps({}),
            "confidence_score": 0.90,
            "status": "validated",
            "created_at": datetime.utcnow().isoformat()
        }
    ]
    
    conn.executemany(
        """
        INSERT INTO trading_strategies (
            strategy_id, hypothesis_id, timestamp_created, strategy_name, 
            asset_scope, entry_conditions, exit_conditions, holding_period,
            risk_rules, position_sizing, volatility_filter, 
            confidence_score, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                s["strategy_id"], s["hypothesis_id"], s["timestamp_created"], s["strategy_name"],
                s["asset_scope"], s["entry_conditions"], s["exit_conditions"], s["holding_period"],
                s["risk_rules"], s["position_sizing"], s["volatility_filter"],
                s["confidence_score"], s["status"], s["created_at"]
            )
            for s in strategies
        ]
    )
    
    print("Inserted 3 mock strategies.")

if __name__ == '__main__':
    insert_mock_strategies()
