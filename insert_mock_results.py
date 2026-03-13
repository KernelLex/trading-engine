import duckdb
import uuid
from datetime import datetime
import json

def insert_mock_results():
    conn = duckdb.connect('data/market_research.duckdb')
    
    # 1. Get the first strategy
    strategy = conn.execute("SELECT strategy_id, asset_scope FROM trading_strategies LIMIT 1").fetchone()
    if not strategy:
        print("No strategies found.")
        return
        
    strategy_id, asset = strategy
    
    # Check if backtests already exist
    count = conn.execute("SELECT count(*) FROM backtest_results WHERE strategy_id=?", [strategy_id]).fetchone()[0]
    if count > 0:
        print(f"Backtest already exists for {strategy_id}.")
        return

    backtest_id = str(uuid.uuid4())
    explanation_id = str(uuid.uuid4())
    
    # Insert backtest_results
    conn.execute("""
        INSERT INTO backtest_results (
            backtest_id, strategy_id, start_date, end_date, 
            total_return, annualized_return, sharpe_ratio, max_drawdown, 
            win_rate, profit_factor, number_of_trades, volatility, 
            status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        backtest_id, strategy_id, '2026-01-01', '2026-03-10',
        0.15, 0.60, 1.8, -0.05,
        0.65, 1.5, 12, 0.12,
        'completed', datetime.utcnow().isoformat()
    ])
    
    # Insert trade_logs
    trades = [
        (str(uuid.uuid4()), strategy_id, "2026-01-10T10:00:00", "2026-01-13T10:00:00", asset, 150.0, 155.0, 5.0, 3, datetime.utcnow().isoformat()),
        (str(uuid.uuid4()), strategy_id, "2026-01-20T10:00:00", "2026-01-23T10:00:00", asset, 153.0, 151.0, -2.0, 3, datetime.utcnow().isoformat()),
        (str(uuid.uuid4()), strategy_id, "2026-02-05T10:00:00", "2026-02-08T10:00:00", asset, 160.0, 168.0, 8.0, 3, datetime.utcnow().isoformat()),
        (str(uuid.uuid4()), strategy_id, "2026-02-15T10:00:00", "2026-02-18T10:00:00", asset, 165.0, 169.0, 4.0, 3, datetime.utcnow().isoformat()),
        (str(uuid.uuid4()), strategy_id, "2026-03-01T10:00:00", "2026-03-04T10:00:00", asset, 170.0, 165.0, -5.0, 3, datetime.utcnow().isoformat())
    ]
    
    conn.executemany("""
        INSERT INTO trade_logs (
            trade_id, strategy_id, entry_timestamp, exit_timestamp,
            asset, entry_price, exit_price, pnl, holding_period, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, trades)
    
    # Insert strategy_explanations
    explanation_text = "Over 12 trades, this strategy was generally profitable. Its performance was primarily driven by positive momentum following strong earnings surprises. SHAP analysis indicates that short-term moving average crossovers provided the strongest predictive power."
    
    conn.execute("""
        INSERT INTO strategy_explanations (
            explanation_id, strategy_id, backtest_id, timestamp,
            key_signals, feature_importance, shap_values, 
            dominant_market_factors, explanation_text, confidence_score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        explanation_id, strategy_id, backtest_id, datetime.utcnow().isoformat(),
        json.dumps(["momentum_5d", "earnings_surprise"]),
        json.dumps({"momentum_5d": 0.4, "earnings_surprise": 0.3, "rsi_14": 0.1}),
        json.dumps({"momentum_5d": 0.25, "earnings_surprise": 0.15, "rsi_14": 0.05}),
        json.dumps({"Tech Sector Momentum": 0.6, "Macro Growth": 0.2}),
        explanation_text, 0.88, datetime.utcnow().isoformat()
    ])
    
    print("Successfully inserted mock backtests, trades, and explanations.")

if __name__ == '__main__':
    insert_mock_results()
