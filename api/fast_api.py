# api/fast_api.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
from datetime import datetime, timedelta

# Initialize FastAPI
app = FastAPI(title="Crypto Grid Trading API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase initialization error: {e}")

# Database instance
db = firestore.client()

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    uid: Optional[str] = None

class UserSignup(BaseModel):
    email: str
    password: str
    name: str

class UserLogin(BaseModel):
    email: str
    password: str

class GridConfig(BaseModel):
    symbol: str
    grid_count: int = 10
    investment: float
    upper_bound: Optional[float] = None
    lower_bound: Optional[float] = None
    auto_trade: bool = False

# Authentication dependency
async def get_current_user(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Routes
@app.post("/api/signup", response_model=Token)
async def signup(user: UserSignup):
    try:
        # Create user in Firebase Auth
        user_record = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.name
        )
        
        # Create user document in Firestore
        db.collection("users").document(user_record.uid).set({
            "email": user.email,
            "name": user.name,
            "created_at": firestore.SERVER_TIMESTAMP,
            "settings": {
                "notification_enabled": True,
                "auto_trade_enabled": False,
                "telegram_chat_id": None
            }
        })
        
        # Create custom token
        custom_token = auth.create_custom_token(user_record.uid)
        
        return {
            "access_token": custom_token.decode("utf-8"),
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/api/login", response_model=Token)
async def login(user: UserLogin):
    try:
        # Get user by email
        user_record = auth.get_user_by_email(user.email)
        
        # Note: We can't verify password here as Firebase Auth doesn't expose this functionality
        # In a real app, you'd use Firebase Authentication REST API directly
        
        # Create custom token
        custom_token = auth.create_custom_token(user_record.uid)
        
        return {
            "access_token": custom_token.decode("utf-8"),
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid credentials"
        )

@app.get("/api/market/top-pairs")
async def get_top_pairs():
    from api.binance_api import fetch_top_pairs
    return fetch_top_pairs()

@app.get("/api/market/ai-tokens")
async def get_ai_tokens():
    from api.coingecko_api import fetch_ai_tokens
    return fetch_ai_tokens()

@app.get("/api/market/grid-opportunities")
async def get_grid_opportunities():
    from api.binance_api import analyze_grid_opportunities
    return analyze_grid_opportunities()

@app.get("/api/market/order-book/{symbol}")
async def get_order_book(symbol: str):
    from api.binance_api import get_order_book_analysis
    return get_order_book_analysis(symbol)

@app.get("/api/social/sentiment/{symbol}")
async def get_social_sentiment(symbol: str):
    from api.social_sentiment import analyze_social_sentiment
    return analyze_social_sentiment(symbol)

@app.post("/api/grid/calculate")
async def calculate_grid(config: GridConfig):
    from api.grid_trading import calculate_grid_levels
    from api.binance_api import fetch_top_pairs
    
    # Get current price and volatility
    pairs = fetch_top_pairs()
    pair_data = next((p for p in pairs if p['symbol'] == config.symbol), None)
    
    if not pair_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol {config.symbol} not found"
        )
    
    price = pair_data['price']
    volatility = pair_data['volatility']
    
    # Calculate grid levels
    grid_data = calculate_grid_levels(
        config.symbol, 
        price, 
        volatility, 
        config.grid_count
    )
    
    return grid_data

@app.post("/api/grid/backtest")
async def backtest_grid(config: GridConfig):
    from api.grid_trading import backtest_grid_strategy
    from api.binance_api import BinanceAPI
    
    # Get historical data
    api = BinanceAPI()
    symbol = config.symbol + "USDT" if not config.symbol.endswith("USDT") else config.symbol
    klines = api.get_klines(symbol, interval="1h", limit=500)
    
    # Convert to dataframe
    df = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    # Backtest strategy
    backtest_result = backtest_grid_strategy(
        config.symbol,
        df,
        config.grid_count,
        config.investment
    )
    
    return backtest_result

@app.post("/api/grid/save")
async def save_grid_config(config: GridConfig, user=Depends(get_current_user)):
    try:
        # Calculate grid levels
        from api.grid_trading import calculate_grid_levels
        from api.binance_api import fetch_top_pairs
        
        # Get current price and volatility
        pairs = fetch_top_pairs()
        pair_data = next((p for p in pairs if p['symbol'] == config.symbol), None)
        
        if not pair_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Symbol {config.symbol} not found"
            )
        
        price = pair_data['price']
        volatility = pair_data['volatility']
        
        # Calculate grid levels
        grid_data = calculate_grid_levels(
            config.symbol, 
            price, 
            volatility, 
            config.grid_count
        )
        
        # Save to database
        db.collection("users").document(user['uid']).collection("grid_configs").add({
            "symbol": config.symbol,
            "grid_count": config.grid_count,
            "investment": config.investment,
            "upper_bound": grid_data['upper_bound'],
            "lower_bound": grid_data['lower_bound'],
            "grid_levels": grid_data['grid_levels'],
            "auto_trade": config.auto_trade,
            "created_at": firestore.SERVER_TIMESTAMP,
            "status": "active" if config.auto_trade else "manual"
        })
        
        return {"message": "Grid configuration saved successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)