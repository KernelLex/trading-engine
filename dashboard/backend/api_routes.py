from fastapi import APIRouter, HTTPException
from dashboard.backend.db_queries import DBQueries

router = APIRouter()
db = DBQueries()

@router.get("/sentiment")
def get_sentiment():
    try:
        return db.get_market_sentiment()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/macro-events")
def get_macro_events():
    try:
        return db.get_macro_events()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hypotheses")
def get_hypotheses():
    try:
        return db.get_research_hypotheses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/strategies")
def get_strategies():
    try:
        return db.get_trading_strategies()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtests")
def get_backtests():
    try:
        return db.get_backtest_performance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/explanations")
def get_explanations():
    try:
        return db.get_strategy_explanations()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades/{strategy_id}")
def get_trades(strategy_id: str):
    try:
        return db.get_trade_simulations(strategy_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
