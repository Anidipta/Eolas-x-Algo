import streamlit as st
import requests
from datetime import datetime
import time

# Helper functions
from pages.utils import *

# Set page configuration
st.set_page_config(
    page_title="Crypto Trading Insights Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Endpoints
API_BASE_URL = "http://localhost:8000"  # FastAPI backend URL

# Define cache duration (in seconds)
CACHE_DURATION = 60

# Common styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #424242;
    }
    .signal-buy {
        color: #4CAF50;
        font-weight: bold;
    }
    .signal-sell {
        color: #F44336;
        font-weight: bold;
    }
    .signal-neutral {
        color: #9E9E9E;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Import pages
from pages.dashboard_overview import show_dashboard_overview
from pages.trading_pairs import show_trading_pairs
from pages.ai_tokens import show_ai_tokens
from pages.market_trends import show_market_trends
from pages.trade_signals import show_trade_signals

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select Page",
    ["Dashboard Overview", "Grid Trading Pairs", "AI Tokens", "Market Trends", "Trade Signals"]
)

# Auto-refresh data
if st.sidebar.checkbox("Auto-refresh data", value=True):
    refresh_interval = st.sidebar.slider("Refresh interval (seconds)", 30, 300, 60)
    
    # Create a placeholder for the last refresh timestamp
    refresh_placeholder = st.sidebar.empty()
    
    # Display the last refresh time
    last_refresh = datetime.now()
    refresh_placeholder.text(f"Last refresh: {last_refresh.strftime('%H:%M:%S')}")
    
    # Check if it's time to refresh
    if (datetime.now() - last_refresh).seconds >= refresh_interval:
        st.cache_data.clear()
        last_refresh = datetime.now()
        refresh_placeholder.text(f"Last refresh: {last_refresh.strftime('%H:%M:%S')}")

# Main content based on selected page
if page == "Dashboard Overview":
    show_dashboard_overview(API_BASE_URL, CACHE_DURATION)
elif page == "Grid Trading Pairs":
    show_trading_pairs(API_BASE_URL, CACHE_DURATION)
elif page == "AI Tokens":
    show_ai_tokens(API_BASE_URL, CACHE_DURATION)
elif page == "Market Trends":
    show_market_trends(API_BASE_URL, CACHE_DURATION)
elif page == "Trade Signals":
    show_trade_signals(API_BASE_URL, CACHE_DURATION)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 Crypto Trading Insights")