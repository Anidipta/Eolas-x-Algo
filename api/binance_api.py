# api/binance_api.py
import os
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime
import talib

class BinanceAPI:
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
    
    def get_exchange_info(self):
        endpoint = "/api/v3/exchangeInfo"
        response = requests.get(f"{self.base_url}{endpoint}")
        return response.json()
    
    def get_ticker_24hr(self):
        endpoint = "/api/v3/ticker/24hr"
        response = requests.get(f"{self.base_url}{endpoint}")
        return response.json()
    
    def get_klines(self, symbol, interval, limit=500):
        endpoint = "/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        return response.json()
    
    def get_order_book(self, symbol, limit=100):
        endpoint = "/api/v3/depth"
        params = {
            "symbol": symbol,
            "limit": limit
        }
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        return response.json()

def fetch_top_pairs(limit=20):
    try:
        api = BinanceAPI()
        tickers = api.get_ticker_24hr()
        
        # Convert to dataframe
        df = pd.DataFrame(tickers)
        
        # Filter USDT pairs
        df_usdt = df[df['symbol'].str.endswith('USDT')]
        
        # Calculate metrics
        df_usdt['priceChangePercent'] = pd.to_numeric(df_usdt['priceChangePercent'])
        df_usdt['quoteVolume'] = pd.to_numeric(df_usdt['quoteVolume'])
        df_usdt['count'] = pd.to_numeric(df_usdt['count'])
        
        # Get top pairs by volume
        top_volume = df_usdt.sort_values('quoteVolume', ascending=False).head(limit)
        
        # Extract relevant data
        result = []
        for _, row in top_volume.iterrows():
            symbol = row['symbol']
            
            # Get klines for technical analysis
            klines = api.get_klines(symbol, interval="4h", limit=100)
            
            if klines:
                klines_df = pd.DataFrame(klines, columns=[
                    'open_time', 'open', 'high', 'low', 'close', 'volume',
                    'close_time', 'quote_asset_volume', 'number_of_trades',
                    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
                ])
                
                # Convert to numeric
                for col in ['open', 'high', 'low', 'close', 'volume']:
                    klines_df[col] = pd.to_numeric(klines_df[col])
                
                # Calculate technical indicators
                klines_df['rsi'] = talib.RSI(klines_df['close'], timeperiod=14)
                klines_df['macd'], klines_df['macd_signal'], klines_df['macd_hist'] = talib.MACD(
                    klines_df['close'], fastperiod=12, slowperiod=26, signalperiod=9
                )
                klines_df['upper_band'], klines_df['middle_band'], klines_df['lower_band'] = talib.BBANDS(
                    klines_df['close'], timeperiod=20
                )
                
                # Calculate volatility
                klines_df['volatility'] = (klines_df['high'] - klines_df['low']) / klines_df['low'] * 100
                
                # Determine if good for grid trading (medium volatility)
                avg_volatility = klines_df['volatility'].mean()
                grid_score = 0
                if 1.5 <= avg_volatility <= 5:
                    grid_score = 5
                elif 1 <= avg_volatility < 1.5 or 5 < avg_volatility <= 8:
                    grid_score = 3
                else:
                    grid_score = 1
                
                # Get current signal
                latest = klines_df.iloc[-1]
                signal = "NEUTRAL"
                if latest['rsi'] < 30:
                    signal = "BUY"
                elif latest['rsi'] > 70:
                    signal = "SELL"
                elif latest['macd'] > latest['macd_signal']:
                    signal = "BUY"
                elif latest['macd'] < latest['macd_signal']:
                    signal = "SELL"
                
                # Add to results
                result.append({
                    'symbol': symbol[:-4],  # Remove USDT
                    'price': float(row['lastPrice']),
                    'change_24h': float(row['priceChangePercent']),
                    'volume_24h': float(row['quoteVolume']),
                    'rsi': latest['rsi'],
                    'signal': signal,
                    'grid_score': grid_score,
                    'volatility': avg_volatility,
                    'klines': klines_df.tail(30).to_dict('records'),
                    'timestamp': datetime.now().timestamp()
                })
        
        return result
    except Exception as e:
        print(f"Error fetching top pairs: {e}")
        return []

def analyze_grid_opportunities():
    pairs = fetch_top_pairs(limit=50)
    grid_pairs = sorted(pairs, key=lambda x: x['grid_score'], reverse=True)
    return grid_pairs[:10]  # Return top 10 grid opportunities

# api/binance_api.py (continued)
def get_order_book_analysis(symbol):
    try:
        api = BinanceAPI()
        symbol = symbol + "USDT" if not symbol.endswith("USDT") else symbol
        order_book = api.get_order_book(symbol, limit=500)
        
        # Convert to dataframe
        bids_df = pd.DataFrame(order_book['bids'], columns=['price', 'quantity'])
        asks_df = pd.DataFrame(order_book['asks'], columns=['price', 'quantity'])
        
        # Convert to numeric
        bids_df['price'] = pd.to_numeric(bids_df['price'])
        bids_df['quantity'] = pd.to_numeric(bids_df['quantity'])
        asks_df['price'] = pd.to_numeric(asks_df['price'])
        asks_df['quantity'] = pd.to_numeric(asks_df['quantity'])
        
        # Calculate total volume
        bids_df['volume'] = bids_df['price'] * bids_df['quantity']
        asks_df['volume'] = asks_df['price'] * asks_df['quantity']
        
        # Calculate key metrics
        spread = asks_df['price'].min() - bids_df['price'].max()
        spread_percentage = spread / asks_df['price'].min() * 100
        
        bid_sum = bids_df['volume'].sum()
        ask_sum = asks_df['volume'].sum()
        buy_sell_ratio = bid_sum / ask_sum if ask_sum > 0 else 0
        
        # Identify support and resistance levels (price levels with large volumes)
        support_levels = bids_df.groupby('price')['quantity'].sum().sort_values(ascending=False).head(5)
        resistance_levels = asks_df.groupby('price')['quantity'].sum().sort_values(ascending=False).head(5)
        
        # Condense data for visualization
        bid_levels = bids_df.groupby(pd.cut(bids_df['price'], 20))['volume'].sum().reset_index()
        ask_levels = asks_df.groupby(pd.cut(asks_df['price'], 20))['volume'].sum().reset_index()
        
        return {
            'spread': spread,
            'spread_percentage': spread_percentage,
            'buy_sell_ratio': buy_sell_ratio,
            'support_levels': [{'price': price, 'quantity': qty} for price, qty in support_levels.items()],
            'resistance_levels': [{'price': price, 'quantity': qty} for price, qty in resistance_levels.items()],
            'bid_distribution': [{'range': str(row['price']), 'volume': row['volume']} for _, row in bid_levels.iterrows()],
            'ask_distribution': [{'range': str(row['price']), 'volume': row['volume']} for _, row in ask_levels.iterrows()],
            'timestamp': datetime.now().timestamp()
        }
    except Exception as e:
        print(f"Error analyzing order book: {e}")
        return {}