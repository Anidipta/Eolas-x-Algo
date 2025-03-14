# pages/dashboard.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests

def show():
    st.markdown("# Dashboard")
    
    # Check if user is authenticated
    if not st.session_state.authenticated:
        st.warning("Please login to access the dashboard.")
        st.stop()
    
    # Check if wallet is connected
    if not st.session_state.wallet_connected:
        with st.expander("Connect Your Wallet", expanded=True):
            st.markdown("### Connect Your Crypto Wallet")
            st.markdown("""
            Connect your wallet to enable trading features and automation.
            We support multiple wallet providers for your convenience.
            """)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("MetaMask", use_container_width=True):
                    # Simulate wallet connection
                    st.session_state.wallet_connected = True
                    st.session_state.wallet_address = "0x71C7656EC7ab88b098defB751B7401B5f6d8976F"
                    st.success("Wallet connected!")
                    st.rerun()
            with col2:
                if st.button("WalletConnect", use_container_width=True):
                    st.info("WalletConnect integration coming soon!")
            with col3:
                if st.button("Coinbase Wallet", use_container_width=True):
                    st.info("Coinbase Wallet integration coming soon!")
    
    # Main dashboard content
    if 'market_data' not in st.session_state or 'top_pairs' not in st.session_state.market_data:
        st.info("Loading market data...")
        # For demonstration, load some sample data
        from api.binance_api import fetch_top_pairs
        from api.coingecko_api import fetch_ai_tokens
        
        if 'market_data' not in st.session_state:
            st.session_state.market_data = {}
        
        st.session_state.market_data['top_pairs'] = fetch_top_pairs(limit=20)
        st.session_state.market_data['ai_tokens'] = fetch_ai_tokens()
    
    # Market Overview
    with st.container():
        st.subheader("Market Overview")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Fetch BTC and ETH data
        btc_data = next((x for x in st.session_state.market_data['top_pairs'] if x['symbol'] == 'BTC'), None)
        eth_data = next((x for x in st.session_state.market_data['top_pairs'] if x['symbol'] == 'ETH'), None)
        
        with col1:
            if btc_data:
                st.metric(
                    "Bitcoin (BTC)", 
                    f"${btc_data['price']:,.2f}", 
                    f"{btc_data['change_24h']:.2f}%"
                )
        
        with col2:
            if eth_data:
                st.metric(
                    "Ethereum (ETH)", 
                    f"${eth_data['price']:,.2f}", 
                    f"{eth_data['change_24h']:.2f}%"
                )
        
        with col3:
            # Calculate average sentiment from AI tokens
            if 'ai_tokens' in st.session_state.market_data:
                ai_tokens = st.session_state.market_data['ai_tokens']
                avg_ai_change = sum(token['change_24h'] for token in ai_tokens) / len(ai_tokens) if ai_tokens else 0
                st.metric(
                    "AI Tokens Average", 
                    f"{avg_ai_change:.2f}%", 
                    f"{avg_ai_change:.2f}%"
                )
        
        with col4:
            # Find best grid opportunity
            if 'top_pairs' in st.session_state.market_data:
                grid_opportunities = sorted(
                    st.session_state.market_data['top_pairs'], 
                    key=lambda x: x.get('grid_score', 0), 
                    reverse=True
                )
                if grid_opportunities:
                    best_grid = grid_opportunities[0]
                    st.metric(
                        "Best Grid Pair", 
                        f"{best_grid['symbol']}", 
                        f"Score: {best_grid.get('grid_score', 0)}"
                    )
    
    # Top Trading Pairs
    with st.container():
        st.subheader("Top Trading Pairs")
        
        if 'top_pairs' in st.session_state.market_data:
            # Create dataframe
            pairs_data = st.session_state.market_data['top_pairs']
            df = pd.DataFrame([
                {
                    'Symbol': pair['symbol'],
                    'Price (USD)': pair['price'],
                    '24h Change (%)': pair['change_24h'],
                    'Volume (USD)': pair['volume_24h'],
                    'Signal': pair['signal'],
                    'Grid Score': pair.get('grid_score', 0)
                }
                for pair in pairs_data
            ])
            
            # Display table with conditional formatting
            st.dataframe(
                df.style.background_gradient(subset=['Grid Score'], cmap='Blues')
                .applymap(lambda x: 'color: green' if x == 'BUY' else ('color: red' if x == 'SELL' else ''), subset=['Signal'])
                .format({'Price (USD)': '${:.2f}', '24h Change (%)': '{:.2f}%', 'Volume (USD)': '${:,.0f}'}),
                height=300,
                use_container_width=True
            )
    
    # Charts and Signals
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Price Action")
        
        # Create tabs for different timeframes
        tab1, tab2, tab3 = st.tabs(["BTC/USDT", "ETH/USDT", "Select Pair"])
        
        with tab1:
            if btc_data and 'klines' in btc_data:
                klines = pd.DataFrame(btc_data['klines'])
                
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=list(range(len(klines))),
                    open=klines['open'],
                    high=klines['high'],
                    low=klines['low'],
                    close=klines['close'],
                    name="BTCUSDT"
                ))
                
                fig.update_layout(
                    title="BTC/USDT Price",
                    yaxis_title="Price (USDT)",
                    xaxis_title="",
                    margin=dict(l=0, r=0, b=0, t=40),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            if eth_data and 'klines' in eth_data:
                klines = pd.DataFrame(eth_data['klines'])
                
                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=list(range(len(klines))),
                    open=klines['open'],
                    high=klines['high'],
                    low=klines['low'],
                    close=klines['close'],
                    name="ETHUSDT"
                ))
                
                fig.update_layout(
                    title="ETH/USDT Price",
                    yaxis_title="Price (USDT)",
                    xaxis_title="",
                    margin=dict(l=0, r=0, b=0, t=40),
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            if 'top_pairs' in st.session_state.market_data:
                pairs = [pair['symbol'] for pair in st.session_state.market_data['top_pairs']]
                selected_pair = st.selectbox("Select Pair", pairs)
                
                # Get selected pair data
                pair_data = next((x for x in st.session_state.market_data['top_pairs'] if x['symbol'] == selected_pair), None)
                
                if pair_data and 'klines' in pair_data:
                    klines = pd.DataFrame(pair_data['klines'])
                    
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=list(range(len(klines))),
                        open=klines['open'],
                        high=klines['high'],
                        low=klines['low'],
                        close=klines['close'],
                        name=f"{selected_pair}USDT"
                    ))
                    
                    fig.update_layout(
                        title=f"{selected_pair}/USDT Price",
                        yaxis_title="Price (USDT)",
                        xaxis_title="",
                        margin=dict(l=0, r=0, b=0, t=40),
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Trading Signals")
        
        # Display signals for top pairs
        if 'top_pairs' in st.session_state.market_data:
            signals = [
                {
                    'Symbol