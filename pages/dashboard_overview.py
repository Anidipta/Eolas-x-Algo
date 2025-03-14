import streamlit as st
import plotly.express as px
import pandas as pd
from pages.utils import *
from pages.api_functions import *

def show_dashboard_overview(api_base_url, cache_duration):
    """Display dashboard overview page"""
    st.markdown("<h1 class='main-header'>Crypto Trading Insights Dashboard</h1>", unsafe_allow_html=True)
    
    # Load data for the dashboard
    trading_pairs = fetch_trading_pairs(api_base_url, limit=5)
    ai_tokens = fetch_ai_tokens(api_base_url, limit=5)
    market_trends = fetch_market_trends(api_base_url)
    trade_signals = fetch_trade_signals(api_base_url, limit=5)
    
    # Dashboard metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if market_trends and 'market_metrics' in market_trends:
            direction = market_trends['market_metrics']['market_direction']
            avg_change = market_trends['market_metrics'].get('avg_top20_change', 0)
            st.metric("Market Direction", 
                     direction.title(), 
                     f"{avg_change:.2f}%",
                     delta_color="normal" if avg_change > 0 else "inverse")
        else:
            st.metric("Market Direction", "Unknown", "0%")

    with col2:
        if trading_pairs:
            best_pair = trading_pairs[0]
            st.metric("Best Grid Trading Pair", 
                     best_pair['symbol'], 
                     f"{best_pair['estimated_profit_potential']}% potential")
        else:
            st.metric("Best Grid Trading Pair", "N/A", "0%")
    
    with col3:
        if ai_tokens:
            best_ai = max(ai_tokens, key=lambda x: x.get('price_change_24h', 0))
            st.metric("Top AI Token", 
                     best_ai['symbol'], 
                     f"{best_ai.get('price_change_24h', 0):.2f}%")
        else:
            st.metric("Top AI Token", "N/A", "0%")
    
    with col4:
        if trade_signals:
            buy_signals = sum(1 for s in trade_signals if s['signal'] == 'buy')
            sell_signals = sum(1 for s in trade_signals if s['signal'] == 'sell')
            signal_ratio = "Bullish" if buy_signals > sell_signals else "Bearish" if sell_signals > buy_signals else "Neutral"
            st.metric("Signal Sentiment", signal_ratio, f"{buy_signals}/{sell_signals} (Buy/Sell)")
        else:
            st.metric("Signal Sentiment", "Unknown", "0/0 (Buy/Sell)")
    
    # Market insights
    st.markdown("<h2 class='sub-header'>Market Insights</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        if market_trends and 'insights' in market_trends:
            for insight in market_trends['insights']:
                st.markdown(f"• {insight}")
        else:
            st.markdown("• No market insights available")
    
    with col2:
        if market_trends and 'market_metrics' in market_trends and 'hot_sectors' in market_trends['market_metrics']:
            hot_sectors = market_trends['market_metrics']['hot_sectors']
            if hot_sectors:
                # Prepare data for chart
                df = pd.DataFrame({
                    'Sector': [s['name'] for s in hot_sectors],
                    'Performance': [s['avg_change'] for s in hot_sectors]
                })
                
                fig = px.bar(
                    df, 
                    x='Sector', 
                    y='Performance',
                    title="Sector Performance",
                    color='Performance',
                    color_continuous_scale=['red', 'lightgray', 'green'],
                    labels={'Performance': '24h Change (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Top trading pairs
    st.markdown("<h2 class='sub-header'>Top Grid Trading Pairs</h2>", unsafe_allow_html=True)
    
    if trading_pairs:
        df = pd.DataFrame(trading_pairs[:5])
        
        cols = st.columns(5)
        for i, (_, pair) in enumerate(df.iterrows()):
            with cols[i]:
                st.markdown(f"**{pair['symbol']}**")
                st.markdown(f"Volatility: {pair['avg_hourly_volatility']}%")
                st.markdown(f"Profit Potential: {pair['estimated_profit_potential']}%")
                st.markdown(f"Volume: {format_large_number(pair['volume_24h'])}")
    else:
        st.markdown("No grid trading pairs available")
    
    # Latest trading signals
    st.markdown("<h2 class='sub-header'>Latest Trading Signals</h2>", unsafe_allow_html=True)
    
    if trade_signals:
        signal_df = pd.DataFrame(trade_signals[:5])
        
        cols = st.columns(len(signal_df))
        for i, (_, signal) in enumerate(signal_df.iterrows()):
            with cols[i]:
                signal_class = f"signal-{signal['signal']}"
                st.markdown(f"**{signal['symbol']}**")
                st.markdown(f"<span class='{signal_class}'>{signal['signal'].upper()}</span>", unsafe_allow_html=True)
                st.markdown(f"Confidence: {signal['confidence'] * 100:.1f}%")
                st.markdown(f"Price: ${signal['current_price']:.4f}")
                st.markdown(f"1h Change: {signal['price_change_1h']}%")
    else:
        st.markdown("No trading signals available")