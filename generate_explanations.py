import json
import logging
from database.db_manager import DatabaseManager
from explainability_engine.strategy_explainer import StrategyExplainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = DatabaseManager()
    db.initialize()
    
    explainer = StrategyExplainer(db)
    
    # Fetch all completed backtests
    backtests = db.conn.execute("SELECT * FROM backtest_results WHERE status='completed'").fetchall()
    cols = [d[0] for d in db.conn.description]
    backtest_dicts = [dict(zip(cols, b)) for b in backtests]
    
    logger.info(f"Found {len(backtest_dicts)} completed backtests.")
    
    for bt in backtest_dicts:
        # Check if explanation already exists
        exists = db.conn.execute(
            "SELECT 1 FROM strategy_explanations WHERE backtest_id=?", [bt['backtest_id']]
        ).fetchone()
        if exists:
            logger.info(f"Explanation already exists for backtest {bt['backtest_id']}. Skipping.")
            continue
        
        # Load trades from trade_logs table (they're stored separately, not in the backtest_results row)
        trades_rows = db.conn.execute(
            "SELECT * FROM trade_logs WHERE strategy_id=? ORDER BY entry_timestamp ASC",
            [bt['strategy_id']]
        ).fetchall()
        trade_cols = [d[0] for d in db.conn.description]
        bt['trades'] = [dict(zip(trade_cols, t)) for t in trades_rows]
        
        # Ensure expected fields are present
        bt.setdefault('start_date', str(bt.get('start_date', '')))
        bt.setdefault('end_date', str(bt.get('end_date', '')))
        bt.setdefault('metrics', {
            'total_return': bt.get('total_return', 0),
            'annualized_return': bt.get('annualized_return', 0)
        })
        bt.setdefault('benchmark', {'outperformance': 0})
            
        logger.info(f"Generating explanation for strategy {bt['strategy_id']} ({len(bt['trades'])} trades)...")
        try:
            explanation = explainer.generate_explanation(bt)
            if explanation:
                db.insert_strategy_explanations([explanation])
                logger.info("Successfully generated and inserted explanation.")
            else:
                logger.warning("Failed to generate explanation (returned None).")
        except Exception as e:
            logger.error(f"Error explaining strategy: {e}")

if __name__ == '__main__':
    main()
