from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from typing import List, Dict, Any, Optional
import data_fetcher
import trading_logic

app = FastAPI(
    title="Crypto Trading Insights API",
    description="API for cryptocurrency trading insights and signals",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Crypto Trading Insights API",
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/trading-pairs")
async def get_trading_pairs(
    min_volatility: float = Query(0.5, description="Minimum volatility percentage"),
    max_volatility: float = Query(5.0, description="Maximum volatility percentage"),
    min_volume: float = Query(1000000, description="Minimum 24h volume in USD"),
    limit: int = Query(20, description="Number of results to return")
):
    try:
        pairs = await trading_logic.identify_grid_trading_pairs(
            min_volatility=min_volatility,
            max_volatility=max_volatility,
            min_volume=min_volume,
            limit=limit
        )
        return {
            "timestamp": datetime.now().isoformat(),
            "pairs": pairs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trading pairs: {str(e)}")

@app.get("/ai-tokens")
async def get_ai_tokens(
    min_market_cap: int = Query(1000000, description="Minimum market cap in USD"),
    limit: int = Query(20, description="Number of results to return")
):
    try:
        tokens = await data_fetcher.get_ai_tokens(min_market_cap=min_market_cap, limit=limit)
        return {
            "timestamp": datetime.now().isoformat(),
            "tokens": tokens
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching AI tokens: {str(e)}")

@app.get("/market-trends")
async def get_market_trends():
    try:
        trends = await trading_logic.detect_market_trends()
        return {
            "timestamp": datetime.now().isoformat(),
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting market trends: {str(e)}")

@app.get("/trade-signals")
async def get_trade_signals(
    pairs: Optional[str] = Query(None, description="Comma-separated list of trading pairs (e.g., BTCUSDT,ETHUSDT)"),
    limit: int = Query(10, description="Number of signals to return")
):
    try:
        pair_list = pairs.split(",") if pairs else None
        signals = await trading_logic.generate_trade_signals(pairs=pair_list, limit=limit)
        return {
            "timestamp": datetime.now().isoformat(),
            "signals": signals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating trade signals: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)