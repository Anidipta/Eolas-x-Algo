import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import logging
import data_fetcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define AI token list for market trend analysis
AI_TOKEN_LIST = [
    "FETUSDT", "OCEANUSDT", "AGIXUSDT", "RNDR", "ALICEUSDT", "GMTUSDT", 
    "ROSEUSDT", "ACHUSDT", "FLMUSDT", "HIGHUSDT"
]

async def identify_grid_trading_pairs(
    min_volatility: float = 0.5,
    max_volatility: float = 5.0,
    min_volume: float = 1000000,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Identify pairs suitable for grid trading based on volatility and volume
    """
    try:
        # Get all ticker data from Binance
        tickers = await data_fetcher.get_binance_tickers()
        
        # Filter for USDT pairs only
        usdt_pairs = [t for t in tickers if t['symbol'].endswith('USDT')]
        
        pair_data = []
        for pair in usdt_pairs:
            symbol = pair['symbol']
            
            # Get detailed kline data for volatility analysis
            klines = await data_fetcher.get_binance_klines(symbol, "1h", 24)
            
            if not klines or len(klines) < 12:  # Ensure we have enough data
                continue
                
            # Calculate hourly volatility from the last 24 hours
            df = pd.DataFrame(klines, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 
                                             'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
                                             'taker_buy_quote_volume', 'ignore'])
            
            # Convert string values to float
            for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
                df[col] = df[col].astype(float)
            
            # Calculate hourly volatility
            df['volatility'] = (df['high'].astype(float) - df['low'].astype(float)) / df['low'].astype(float) * 100
            avg_volatility = df['volatility'].mean()
            
            # Get 24h volume
            volume_24h = float(pair['quoteVolume'])
            
            # Calculate price range for grid trading
            current_price = float(pair['lastPrice'])
            price_range_low = min(df['low'].astype(float))
            price_range_high = max(df['high'].astype(float))
            
            # Calculate grid trading metrics
            range_width = (price_range_high - price_range_low) / price_range_low * 100
            suggested_grids = max(5, min(20, int(range_width / 0.5)))
            
            # Filter based on criteria
            if (min_volatility <= avg_volatility <= max_volatility and 
                volume_24h >= min_volume):
                
                pair_data.append({
                    'symbol': symbol,
                    'current_price': current_price,
                    'avg_hourly_volatility': round(avg_volatility, 2),
                    'volume_24h': volume_24h,
                    'price_range_low': price_range_low,
                    'price_range_high': price_range_high,
                    'range_width_percent': round(range_width, 2),
                    'suggested_grid_levels': suggested_grids,
                    'estimated_profit_potential': round(range_width * 0.8, 2),  # 80% of the range as potential profit
                })
        
        # Sort by estimated profit potential
        pair_data.sort(key=lambda x: x['estimated_profit_potential'], reverse=True)
        
        return pair_data[:limit]
        
    except Exception as e:
        logger.error(f"Error identifying grid trading pairs: {str(e)}")
        return []

async def detect_market_trends() -> Dict[str, Any]:
    """
    Detect early market trends based on key indicators
    """
    try:
        # Get overall market data from CoinGecko
        coins = await data_fetcher.get_coingecko_coins()
        
        # Get top coins data
        top_coins = coins[:20]
        
        # Get AI tokens for sector analysis
        ai_tokens = await data_fetcher.get_ai_tokens(limit=15)
        
        # Calculate overall market metrics
        market_metrics = {
            'top_gainers': sorted([{
                'symbol': coin['symbol'].upper(),
                'price_change_24h': coin.get('price_change_percentage_24h', 0)
            } for coin in top_coins if coin.get('price_change_percentage_24h', 0) > 0], 
            key=lambda x: x['price_change_24h'], reverse=True)[:5],
            
            'top_losers': sorted([{
                'symbol': coin['symbol'].upper(),
                'price_change_24h': coin.get('price_change_percentage_24h', 0)
            } for coin in top_coins if coin.get('price_change_percentage_24h', 0) < 0], 
            key=lambda x: x['price_change_24h'])[:5],
            
            'avg_top20_change': np.mean([coin.get('price_change_percentage_24h', 0) for coin in top_coins]),
            'avg_ai_token_change': np.mean([token.get('price_change_24h', 0) for token in ai_tokens]),
            'market_direction': 'bullish' if np.mean([coin.get('price_change_percentage_24h', 0) for coin in top_coins]) > 0 else 'bearish',
            'hot_sectors': _identify_hot_sectors(coins)
        }
        
        # Generate market insights
        insights = []
        
        if market_metrics['avg_top20_change'] > 3:
            insights.append("Strong bullish momentum in top cryptocurrencies")
        elif market_metrics['avg_top20_change'] < -3:
            insights.append("Significant bearish pressure across top cryptocurrencies")
            
        if market_metrics['avg_ai_token_change'] > market_metrics['avg_top20_change'] + 2:
            insights.append("AI tokens outperforming the broader market - sector rotation detected")
        elif market_metrics['avg_ai_token_change'] < market_metrics['avg_top20_change'] - 2:
            insights.append("AI tokens underperforming the broader market")
            
        # Add insights about hot sectors
        if market_metrics['hot_sectors']:
            top_sector = market_metrics['hot_sectors'][0]
            insights.append(f"{top_sector['name']} sector showing strength with {top_sector['avg_change']:.1f}% average gain")
        
        return {
            'market_metrics': market_metrics,
            'insights': insights,
            'recommendation': _generate_market_recommendation(market_metrics)
        }
        
    except Exception as e:
        logger.error(f"Error detecting market trends: {str(e)}")
        return {'market_metrics': {}, 'insights': ['Error analyzing market trends'], 'recommendation': 'neutral'}

def _identify_hot_sectors(coins: List[Dict]) -> List[Dict]:
    """
    Identify which sectors are performing well
    """
    # Define sectors and their keywords
    sectors = {
        'AI & Data': ['ai', 'data', 'neural', 'intelligence', 'machine', 'predict', 'learn'],
        'DeFi': ['defi', 'finance', 'yield', 'swap', 'lend', 'borrow', 'staking'],
        'Gaming': ['game', 'play', 'nft', 'metaverse', 'virtual', 'realm'],
        'Layer 1': ['layer', 'blockchain', 'consensus', 'scalable', 'protocol'],
        'Layer 2': ['layer2', 'rollup', 'scaling', 'optimistic', 'zkrollup']
    }
    
    # Assign coins to sectors and calculate performance
    sector_performance = {}
    for sector_name, keywords in sectors.items():
        sector_coins = []
        for coin in coins:
            coin_name = coin.get('name', '').lower()
            coin_desc = coin.get('description', '').lower() if 'description' in coin else ''
            
            if any(keyword in coin_name or keyword in coin_desc for keyword in keywords):
                price_change = coin.get('price_change_percentage_24h', 0)
                if price_change is not None:
                    sector_coins.append(price_change)
        
        if sector_coins:
            avg_change = sum(sector_coins) / len(sector_coins)
            sector_performance[sector_name] = {
                'name': sector_name,
                'avg_change': avg_change,
                'coin_count': len(sector_coins)
            }
    
    # Convert to list and sort by performance
    result = [v for k, v in sector_performance.items()]
    result.sort(key=lambda x: x['avg_change'], reverse=True)
    
    return result

def _generate_market_recommendation(market_metrics: Dict) -> str:
    """
    Generate a market recommendation based on metrics
    """
    avg_change = market_metrics.get('avg_top20_change', 0)
    
    if avg_change > 5:
        return "strongly_bullish"
    elif avg_change > 2:
        return "bullish"
    elif avg_change < -5:
        return "strongly_bearish"
    elif avg_change < -2:
        return "bearish"
    else:
        return "neutral"

async def generate_trade_signals(pairs: Optional[List[str]] = None, limit: int = 10) -> List[Dict]:
    """
    Generate trading signals based on technical analysis
    """
    try:
        # Get trading pair data
        pair_data = await data_fetcher.get_trading_pair_data(pairs)
        
        signals = []
        for symbol, data in pair_data.items():
            try:
                # Convert price history to pandas Series for analysis
                if len(data['price_history']) < 20:
                    continue
                    
                prices = pd.Series(data['price_history'])
                
                # Calculate some basic indicators
                sma_fast = prices.rolling(window=7).mean().iloc[-1]
                sma_slow = prices.rolling(window=20).mean().iloc[-1]
                
                current_price = prices.iloc[-1]
                prev_price = prices.iloc[-2] 
                
                # Generate signal based on moving averages crossover
                signal = "neutral"
                confidence = 0.5
                
                if sma_fast > sma_slow and prices.iloc[-1] > sma_fast:
                    signal = "buy"
                    confidence = min(0.95, 0.5 + (sma_fast - sma_slow) / current_price)
                elif sma_fast < sma_slow and prices.iloc[-1] < sma_fast:
                    signal = "sell"
                    confidence = min(0.95, 0.5 + (sma_slow - sma_fast) / current_price)
                
                # Calculate momentum
                momentum = (current_price - prices.iloc[-6]) / prices.iloc[-6] * 100
                
                # Add volume analysis
                volume_change = (data['volume_history'][-1] - data['volume_history'][-2]) / data['volume_history'][-2] * 100 if data['volume_history'][-2] > 0 else 0
                
                # Adjust confidence based on volume confirmation
                if (signal == "buy" and volume_change > 10) or (signal == "sell" and volume_change < -10):
                    confidence = min(0.95, confidence + 0.1)
                
                signals.append({
                    'symbol': symbol,
                    'signal': signal,
                    'confidence': round(confidence, 2),
                    'current_price': current_price,
                    'price_change_1h': round((current_price - prev_price) / prev_price * 100, 2),
                    'momentum': round(momentum, 2),
                    'fast_ma': round(sma_fast, 8),
                    'slow_ma': round(sma_slow, 8),
                    'volume_change': round(volume_change, 2)
                })
                
            except Exception as e:
                logger.error(f"Error generating signal for {symbol}: {str(e)}")
                continue
        
        # Sort by confidence (highest first)
        signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return signals[:limit]
        
    except Exception as e:
        logger.error(f"Error generating trade signals: {str(e)}")
        return []
