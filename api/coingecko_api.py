# api/coingecko_api.py
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

class CoinGeckoAPI:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = os.getenv("COINGECKO_API_KEY", "")
        self.headers = {"x-cg-pro-api-key": self.api_key} if self.api_key else {}
    
    def get_coin_list(self):
        endpoint = "/coins/list"
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
        if response.status_code == 429:  # Rate limit exceeded
            time.sleep(60)  # Wait for a minute and retry
            response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
        return response.json()
    
    def get_coin_markets(self, vs_currency='usd', category=None, order='market_cap_desc', per_page=100, page=1):
        endpoint = "/coins/markets"
        params = {
            "vs_currency": vs_currency,
            "order": order,
            "per_page": per_page,
            "page": page,
            "sparkline": "true",
            "price_change_percentage": "1h,24h,7d"
        }
        if category:
            params["category"] = category
            
        response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
        if response.status_code == 429:  # Rate limit exceeded
            time.sleep(60)  # Wait for a minute and retry
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
        return response.json()
    
    def get_coin_details(self, coin_id):
        endpoint = f"/coins/{coin_id}"
        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "true",
            "developer_data": "false"
        }
        response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
        if response.status_code == 429:  # Rate limit exceeded
            time.sleep(60)  # Wait for a minute and retry
            response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
        return response.json()

def fetch_ai_tokens():
    try:
        api = CoinGeckoAPI()
        
        # Get AI-related tokens
        ai_categories = ["artificial-intelligence", "ai-big-data"]
        ai_tokens = []
        
        for category in ai_categories:
            # Try to get data with pagination
            for page in range(1, 3):  # Get up to 200 tokens (2 pages)
                tokens = api.get_coin_markets(category=category, per_page=100, page=page)
                ai_tokens.extend(tokens)
                time.sleep(1)  # Be nice to the API
        
        # Process tokens
        result = []
        for token in ai_tokens:
            if token.get('id') and token.get('current_price'):
                # Get more details for selected tokens
                price_change_24h = token.get('price_change_percentage_24h', 0)
                
                # Add to results
                result.append({
                    'id': token['id'],
                    'symbol': token['symbol'].upper(),
                    'name': token['name'],
                    'price': token['current_price'],
                    'market_cap': token.get('market_cap', 0),
                    'change_1h': token.get('price_change_percentage_1h_in_currency', 0),
                    'change_24h': price_change_24h,
                    'change_7d': token.get('price_change_percentage_7d_in_currency', 0),
                    'sparkline': token.get('sparkline_in_7d', {}).get('price', []),
                    'image': token.get('image', ''),
                    'category': 'ai',
                    'timestamp': datetime.now().timestamp()
                })
        
        # Sort by market cap
        result = sorted(result, key=lambda x: x['market_cap'], reverse=True)
        return result[:50]  # Return top 50 AI tokens
    except Exception as e:
        print(f"Error fetching AI tokens: {e}")
        return []