import sys
import logging
from database.db_manager import DatabaseManager
from explainability_engine.strategy_explainer import StrategyExplainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = DatabaseManager()
    db.initialize()
    
    explainer = StrategyExplainer(db)
    
    # Fetch all backtests
    backtests = db.conn.execute("SELECT * FROM backtest_results WHERE status='completed'").fetchall()
    cols = [d[0] for d in db.conn.description]
    backtest_dicts = [dict(zip(cols, b)) for b in backtests]
    
    logger.info(f"Found {len(backtest_dicts)} completed backtests.")
    
    for bt in backtest_dicts:
        # Load trades (it's JSON in the DB)
        import json
        if isinstance(bt['trades'], str):
            bt['trades'] = json.loads(bt['trades'])
        
        # Check if explanation already exists
        exists = db.conn.execute("SELECT 1 FROM strategy_explanations WHERE backtest_id=?", [bt['backtest_id']]).fetchone()
        if exists:
            logger.info(f"Explanation already exists for backtest {bt['backtest_id']}. Skipping.")
            continue
            
        logger.info(f"Generating explanation for strategy {bt['strategy_id']}...")
        try:
            explanation = explainer.generate_explanation(bt)
            if explanation:
                db.insert_strategy_explanations([explanation])
                logger.info(f"Successfully generated and inserted explanation.")
            else:
                logger.warning("Failed to generate explanation (returned None).")
        except Exception as e:
            logger.error(f"Error explaining strategy: {e}")

if __name__ == '__main__':
    main()
