import streamlit as st
import requests

@st.cache_data(ttl=60)
def fetch_trading_pairs(api_base_url, min_volatility=0.5, max_volatility=5.0, min_volume=1000000, limit=20):
    """Fetch trading pairs from the API"""
    try:
        response = requests.get(
            f"{api_base_url}/trading-pairs",
            params={
                "min_volatility": min_volatility,
                "max_volatility": max_volatility, 
                "min_volume": min_volume,
                "limit": limit
            }
        )
        return response.json()["pairs"]
    except Exception as e:
        st.error(f"Error fetching trading pairs: {str(e)}")
        return []

@st.cache_data(ttl=60)
def fetch_ai_tokens(api_base_url, min_market_cap=1000000, limit=20):
    """Fetch AI tokens from the API"""
    try:
        response = requests.get(
            f"{api_base_url}/ai-tokens",
            params={"min_market_cap": min_market_cap, "limit": limit}
        )
        return response.json()["tokens"]
    except Exception as e:
        st.error(f"Error fetching AI tokens: {str(e)}")
        return []

@st.cache_data(ttl=60)
def fetch_market_trends(api_base_url):
    """Fetch market trends from the API"""
    try:
        response = requests.get(f"{api_base_url}/market-trends")
        return response.json()["trends"]
    except Exception as e:
        st.error(f"Error fetching market trends: {str(e)}")
        return {}

@st.cache_data(ttl=60)
def fetch_trade_signals(api_base_url, pairs=None, limit=10):
    """Fetch trade signals from the API"""
    try:
        params = {"limit": limit}
        if pairs:
            params["pairs"] = ",".join(pairs)
            
        response = requests.get(f"{api_base_url}/trade-signals", params=params)
        return response.json()["signals"]
    except Exception as e:
        st.error(f"Error fetching trade signals: {str(e)}")
        return []