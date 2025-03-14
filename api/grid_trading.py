
# api/grid_trading.py
import numpy as np
import pandas as pd
from datetime import datetime
import talib

def calculate_grid_levels(symbol, price, volatility, grid_count=10):
    """Calculate grid levels for a trading pair"""
    # Determine price range based on volatility
    price_range = volatility * 2  # 2x daily volatility for grid range
    
    # Calculate upper and lower bounds
    upper_bound = price * (1 + price_range / 100)
    lower_bound = price * (1 - price_range / 100)
    
    # Create grid levels
    grid_levels = np.linspace(lower_bound, upper_bound, grid_count)
    
    # Calculate expected profit
    expected_profit_per_grid = (upper_bound - lower_bound) / (grid_count - 1) / price * 100
    
    return {
        'symbol': symbol,
        'current_price': price,
        'upper_bound': upper_bound,
        'lower_bound': lower_bound,
        'grid_levels': grid_levels.tolist(),
        'grid_count': grid_count,
        'expected_profit_per_grid': expected_profit_per_grid,
        'total_expected_profit': expected_profit_per_grid * (grid_count - 1),
        'timestamp': datetime.now().timestamp()
    }

def backtest_grid_strategy(symbol, historical_data, grid_count=10, investment=1000.0):
    """Backtest grid trading strategy on historical data"""
    # Convert to dataframe if necessary
    if not isinstance(historical_data, pd.DataFrame):
        df = pd.DataFrame(historical_data)
    else:
        df = historical_data.copy()
    
    # Ensure we have required columns
    required_cols = ['open_time', 'open', 'high', 'low', 'close']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Convert price columns to numeric
    for col in ['open', 'high', 'low', 'close']:
        df[col] = pd.to_numeric(df[col])
    
    # Get price range
    price_min = df['low'].min()
    price_max = df['high'].max()
    
    # Create grid levels
    grid_levels = np.linspace(price_min, price_max, grid_count)
    
    # Simulate trading
    base_asset = 0
    quote_asset = investment
    trades = []
    
    for idx, row in df.iterrows():
        # Check if price crossed any grid levels
        for i, level in enumerate(grid_levels):
            # Buy order triggered
            if row['low'] <= level <= row['high'] and i < len(grid_levels) - 1:
                order_amount = investment / grid_count
                if quote_asset >= order_amount:
                    base_asset_bought = order_amount / level
                    quote_asset -= order_amount
                    base_asset += base_asset_bought
                    
                    trades.append({
                        'timestamp': row['open_time'],
                        'type': 'buy',
                        'price': level,
                        'amount': base_asset_bought,
                        'total': order_amount
                    })
            
            # Sell order triggered
            if row['low'] <= level <= row['high'] and i > 0:
                if base_asset > 0:
                    sell_amount = base_asset / (grid_count - i)
                    if sell_amount > 0:
                        quote_asset_gained = sell_amount * level
                        base_asset -= sell_amount
                        quote_asset += quote_asset_gained
                        
                        trades.append({
                            'timestamp': row['open_time'],
                            'type': 'sell',
                            'price': level,
                            'amount': sell_amount,
                            'total': quote_asset_gained
                        })
    
    # Calculate final value
    final_price = df['close'].iloc[-1]
    final_value = quote_asset + (base_asset * final_price)
    profit = final_value - investment
    profit_percentage = (profit / investment) * 100
    
    return {
        'symbol': symbol,
        'initial_investment': investment,
        'final_value': final_value,
        'profit': profit,
        'profit_percentage': profit_percentage,
        'trades': trades,
        'trade_count': len(trades),
        'grid_levels': grid_levels.tolist(),
        'timestamp': datetime.now().timestamp()
    }