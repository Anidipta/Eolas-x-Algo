import aiohttp
import asyncio
import pandas as pd
import logging
from typing import Dict, List, Any, Optional
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoints
BINANCE_API_BASE = "https://api.binance.com/api/v3"
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"

# Cache configuration
CACHE_EXPIRY = 60  # seconds
cache = {}

async def fetch_with_cache(url: str, expiry: int = CACHE_EXPIRY) -> Dict:
    """Fetch data with caching to avoid API rate limits"""
    current_time = time.time()
    
    if url in cache and current_time - cache[url]["timestamp"] < expiry:
        return cache[url]["data"]
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    logger.error(f"API request failed: {url}, Status: {response.status}")
                    return {}
                data = await response.json()
                cache[url] = {"data": data, "timestamp": current_time}
                return data
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {str(e)}")
            return {}

async def get_binance_tickers() -> List[Dict]:
    """Get 24hr ticker data for all symbols from Binance"""
    url = f"{BINANCE_API_BASE}/ticker/24hr"
    data = await fetch_with_cache(url)
    return data if isinstance(data, list) else []

async def get_binance_klines(symbol: str, interval: str = "1h", limit: int = 100) -> List[List]:
    """Get kline/candlestick data for a symbol"""
    url = f"{BINANCE_API_BASE}/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = await fetch_with_cache(url)
    return data if isinstance(data, list) else []

async def get_coingecko_coins() -> List[Dict]:
    """Get list of coins from CoinGecko"""
    url = f"{COINGECKO_API_BASE}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1"
    data = await fetch_with_cache(url)
    return data if isinstance(data, list) else []

async def get_ai_tokens(min_market_cap: int = 1000000, limit: int = 20) -> List[Dict]:
    """Get AI-related tokens with market data"""
    ai_keywords = ["ai", "artificial", "intelligence", "machine", "learning", "neural", 
                  "data", "predict", "cognitive", "brain", "deep", "smart"]
    
    all_coins = await get_coingecko_coins()
    
    # Filter for AI-related tokens
    ai_tokens = []
    for coin in all_coins:
        name = (coin.get('name', '') or '').lower()
        symbol = (coin.get('symbol', '') or '').lower()
        description = (coin.get('description', '') or '').lower()
        
        # Check if any AI keyword is in the name, symbol or description
        is_ai_related = any(keyword in name or keyword in symbol or 
                          (description and keyword in description) 
                          for keyword in ai_keywords)
        
        if is_ai_related and coin.get('market_cap', 0) > min_market_cap:
            # Get 24h price change from CoinGecko
            price_change = coin.get('price_change_percentage_24h', 0)
            
            ai_tokens.append({
                'id': coin.get('id'),
                'symbol': coin.get('symbol', '').upper(),
                'name': coin.get('name'),
                'current_price': coin.get('current_price', 0),
                'market_cap': coin.get('market_cap', 0),
                'price_change_24h': price_change,
                'volume_24h': coin.get('total_volume', 0),
                'image': coin.get('image', '')
            })
    
    # Sort by market cap and limit results
    ai_tokens.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
    return ai_tokens[:limit]

async def get_trading_pair_data(symbols: List[str] = None) -> Dict[str, Dict]:
    """Get comprehensive data for trading pairs"""
    all_tickers = await get_binance_tickers()
    
    if not symbols:
        # If no symbols provided, get top pairs by volume
        all_tickers.sort(key=lambda x: float(x.get('quoteVolume', 0)), reverse=True)
        symbols = [ticker['symbol'] for ticker in all_tickers[:30] if ticker['symbol'].endswith('USDT')]
    
    result = {}
    for symbol in symbols:
        # Get ticker data
        ticker_data = next((item for item in all_tickers if item['symbol'] == symbol), {})
        
        if not ticker_data:
            continue
            
        # Get recent klines for price history
        klines = await get_binance_klines(symbol, "1h", 24)
        
        # Convert klines to a more usable format
        prices = []
        volumes = []
        
        for k in klines:
            if len(k) > 7:  # Ensure we have enough data
                prices.append(float(k[4]))  # Close price
                volumes.append(float(k[5]))  # Volume
        
        # Calculate volatility
        if len(prices) > 1:
            price_changes = [abs(prices[i] - prices[i-1])/prices[i-1]*100 for i in range(1, len(prices))]
            avg_volatility = sum(price_changes) / len(price_changes)
        else:
            avg_volatility = 0
            
        # Prepare the result
        result[symbol] = {
            'symbol': symbol,
            'last_price': float(ticker_data.get('lastPrice', 0)),
            'price_change_24h': float(ticker_data.get('priceChangePercent', 0)),
            'high_24h': float(ticker_data.get('highPrice', 0)),
            'low_24h': float(ticker_data.get('lowPrice', 0)),
            'volume_24h': float(ticker_data.get('quoteVolume', 0)),
            'hourly_volatility': avg_volatility,
            'price_history': prices,
            'volume_history': volumes
        }
    
    return result