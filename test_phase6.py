"""
Test script for Phase 6 Explainability Engine.
"""
import uuid
from database.db_manager import DatabaseManager
from explainability_engine.strategy_explainer import StrategyExplainer

def run_test():
    db = DatabaseManager()
    db.initialize()
    
    # Insert some mock price data so feature_builder doesn't fail immediately
    db.insert_stock_prices([
        {"ticker": "AAPL", "date": f"2026-03-{i:02d}", "open": 150+i, "high": 155+i, "low": 145+i, "close": 152+i, "volume": 1000000}
        for i in range(1, 15)
    ])
    
    # Mock a completed backtest result
    mock_strategy_id = str(uuid.uuid4())
    mock_backtest_id = str(uuid.uuid4())
    
    mock_result = {
        "status": "completed",
        "strategy_id": mock_strategy_id,
        "backtest_id": mock_backtest_id,
        "start_date": "2026-03-01",
        "end_date": "2026-03-14",
        "trades": [
            {"trade_id": str(uuid.uuid4()), "strategy_id": mock_strategy_id, "asset": "AAPL", "entry_timestamp": "2026-03-05T10:00:00", "pnl": 10.5},
            {"trade_id": str(uuid.uuid4()), "strategy_id": mock_strategy_id, "asset": "AAPL", "entry_timestamp": "2026-03-08T10:00:00", "pnl": -2.5},
            {"trade_id": str(uuid.uuid4()), "strategy_id": mock_strategy_id, "asset": "AAPL", "entry_timestamp": "2026-03-10T10:00:00", "pnl": 15.0},
            {"trade_id": str(uuid.uuid4()), "strategy_id": mock_strategy_id, "asset": "AAPL", "entry_timestamp": "2026-03-11T10:00:00", "pnl": 5.0},
            {"trade_id": str(uuid.uuid4()), "strategy_id": mock_strategy_id, "asset": "AAPL", "entry_timestamp": "2026-03-12T10:00:00", "pnl": 20.0},
        ],
        "metrics": {"total_return": 0.05, "annualized_return": 0.5},
        "benchmark": {"outperformance": 0.02}
    }
    
    # Generate explanation
    explainer = StrategyExplainer(db)
    explanation = explainer.generate_explanation(mock_result)
    
    if explanation:
        print("\n--- Generated Explanation ---")
        print(explanation["explanation_text"])
        print("\nConfidence Score:", explanation["confidence_score"])
        print("Dominant Factors:", explanation["dominant_market_factors"])
        
        # Save it
        db.insert_strategy_explanations([explanation])
        
        # Verify it's in the DB
        res = db.conn.execute("SELECT * FROM strategy_explanations WHERE backtest_id = ?", [mock_backtest_id]).fetchone()
        if res:
            print("\nSUCCESS: Found explanation in strategy_explanations table.")
        else:
            print("\nFAILURE: Did not find explanation in table.")
    else:
        print("\nFAILURE: Explainer returned None.")

if __name__ == "__main__":
    run_test()
