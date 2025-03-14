import streamlit as st
import pandas as pd
import plotly.express as px
from pages.utils import *
from pages.api_functions import *

def show_ai_tokens(api_base_url, cache_duration):
    """Display AI tokens tracking page"""
    st.markdown("<h1 class='main-header'>AI Token Tracking</h1>", unsafe_allow_html=True)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        min_market_cap = st.select_slider(
            "Minimum Market Cap",
            options=[1_000_000, 5_000_000, 10_000_000, 50_000_000, 100_000_000, 500_000_000],
            value=10_000_000,
            format_func=lambda x: format_large_number(x)
        )
    
    with col2:
        token_count = st.slider("Number of tokens to display", 5, 50, 20)
    
    # Fetch AI tokens
    ai_tokens = fetch_ai_tokens(api_base_url, min_market_cap=min_market_cap, limit=token_count)
    
    if ai_tokens:
        # Create dataframe
        df = pd.DataFrame(ai_tokens)
        
        # Performance overview
        st.markdown("<h2 class='sub-header'>AI Token Performance</h2>", unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Performance chart
            performance_df = df[['symbol', 'price_change_24h']].sort_values('price_change_24h', ascending=False)
            
            fig = px.bar(
                performance_df,
                x='symbol',
                y='price_change_24h',
                title='24h Price Change (%)',
                labels={'symbol': 'Token', 'price_change_24h': '24h Change (%)'},
                color='price_change_24h',
                color_continuous_scale=['red', 'lightgray', 'green'],
                range_color=[-10, 10]
            )
            
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Key metrics
            pos_tokens = len([t for t in ai_tokens if t.get('price_change_24h', 0) > 0])
            neg_tokens = len([t for t in ai_tokens if t.get('price_change_24h', 0) < 0])
            
            st.metric(
                "Overall AI Token Sentiment",
                "Bullish" if pos_tokens > neg_tokens else "Bearish" if neg_tokens > pos_tokens else "Neutral",
                f"{pos_tokens}/{neg_tokens} (Positive/Negative)"
            )
            
            avg_change = sum(t.get('price_change_24h', 0) for t in ai_tokens) / len(ai_tokens)
            st.metric("Average 24h Change", f"{avg_change:.2f}%")
            
            # Best and worst performers
            best_token = max(ai_tokens, key=lambda x: x.get('price_change_24h', 0))
            worst_token = min(ai_tokens, key=lambda x: x.get('price_change_24h', 0))
            
            st.metric(
                "Best Performer",
                best_token['symbol'],
                f"{best_token.get('price_change_24h', 0):.2f}%",
                delta_color="normal"
            )
            
            st.metric(
                "Worst Performer",
                worst_token['symbol'],
                f"{worst_token.get('price_change_24h', 0):.2f}%", 
                delta_color="inverse"
            )
        
        # Market cap comparison
        st.markdown("<h2 class='sub-header'>Market Cap Distribution</h2>", unsafe_allow_html=True)
        
        market_cap_fig = px.treemap(
            df,
            path=['symbol'],
            values='market_cap',
            color='price_change_24h',
            color_continuous_scale=['red', 'lightgray', 'green'],
            range_color=[-10, 10],
            title='AI Token Market Cap Distribution',
            hover_data=['current_price', 'price_change_24h']
        )
        
        market_cap_fig.update_layout(height=500)
        st.plotly_chart(market_cap_fig, use_container_width=True)
        
        # Token details table
        st.markdown("<h2 class='sub-header'>AI Token Details</h2>", unsafe_allow_html=True)
        
        display_df = df[['symbol', 'name', 'current_price', 'price_change_24h', 'market_cap', 'volume_24h']]
        display_df.columns = ['Symbol', 'Name', 'Current Price', '24h Change (%)', 'Market Cap', '24h Volume']
        
        st.dataframe(
            display_df.style.format({
                'Current Price': '${:.4f}',
                '24h Change (%)': '{:.2f}',
                'Market Cap': '${:,.0f}',
                '24h Volume': '${:,.0f}'
            }),
            height=400,
            use_container_width=True
        )
        
        # Download button for CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download AI Tokens as CSV",
            data=csv,
            file_name=f"ai_tokens_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )
    else:
        st.error("No AI tokens data available")