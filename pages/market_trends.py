import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pages.utils import *
from pages.api_functions import *

def show_market_trends(api_base_url, cache_duration):
    """Display market trends page"""
    st.markdown("<h1>Early Market Trend Detection</h1>", unsafe_allow_html=True)
    
    # Fetch market trends
    market_trends = fetch_market_trends(api_base_url)
    
    if market_trends and 'market_metrics' in market_trends:
        market_metrics = market_trends['market_metrics']
        insights = market_trends.get('insights', [])
        recommendation = market_trends.get('recommendation', 'neutral')
        
        # Market direction indicator
        st.markdown("<h2>Market Direction</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            direction = market_metrics['market_direction'].upper()
            direction_color = "green" if direction == "BULLISH" else "red" if direction == "BEARISH" else "gray"
            
            # Create a gauge chart for market direction
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=market_metrics['avg_top20_change'],
                delta={'reference': 0, 'position': "top"},
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [-10, 10], 'tickwidth': 1},
                    'bar': {'color': direction_color},
                    'bgcolor': "white",
                    'steps': [
                        {'range': [-10, -3], 'color': "rgba(255, 0, 0, 0.3)"},
                        {'range': [-3, 3], 'color': "rgba(200, 200, 200, 0.3)"},
                        {'range': [3, 10], 'color': "rgba(0, 255, 0, 0.3)"}
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': 0
                    }
                },
                title={
                    'text': f"{direction} ({market_metrics['avg_top20_change']:.2f}%)",
                    'font': {'size': 24, 'color': direction_color}
                }
            ))
            
            fig.update_layout(height=300, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        # Key metrics
        st.markdown("<h2>Key Market Metrics</h2>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Avg Top 20 Change", 
                f"{market_metrics['avg_top20_change']:.2f}%",
                delta=f"{market_metrics['avg_top20_change_24h']:.2f}%"
            )
        
        with col2:
            st.metric(
                "Market Breadth", 
                f"{market_metrics['market_breadth']:.2f}",
                delta=f"{market_metrics['market_breadth_24h']:.2f}"
            )
        
        with col3:
            st.metric(
                "Volume Trend", 
                f"{market_metrics['volume_trend']:.2f}%",
                delta=f"{market_metrics['volume_trend_24h']:.2f}%"
            )
        
        with col4:
            st.metric(
                "Fear & Greed Index", 
                f"{market_metrics['fear_greed_index']}",
                delta=f"{market_metrics['fear_greed_index_24h']}"
            )
        
        # Sector performance
        st.markdown("<h2>Sector Performance</h2>", unsafe_allow_html=True)
        
        if 'sector_performance' in market_trends:
            sector_df = pd.DataFrame(market_trends['sector_performance'])
            
            # Create a bar chart for sector performance
            fig = px.bar(
                sector_df,
                x='sector',
                y='performance',
                color='performance',
                color_continuous_scale=['red', 'yellow', 'green'],
                range_color=[-5, 5],
                title='Sector Performance (%)'
            )
            
            fig.update_layout(height=400, margin=dict(l=10, r=10, t=50, b=10))
            st.plotly_chart(fig, use_container_width=True)
        
        # Market Insights
        st.markdown("<h2>Market Insights</h2>", unsafe_allow_html=True)
        
        if insights:
            for insight in insights:
                st.info(insight)
        else:
            st.info("No market insights available at this time.")
        
        # Recommendation
        st.markdown("<h2>Recommendation</h2>", unsafe_allow_html=True)
        
        recommendation_color = {
            'bullish': 'green',
            'bearish': 'red',
            'neutral': 'gray'
        }.get(recommendation.lower(), 'gray')
        
        st.markdown(
            f"<div style='background-color: {recommendation_color}; padding: 20px; border-radius: 10px;'>"
            f"<h3 style='color: white; text-align: center;'>{recommendation.upper()}</h3>"
            "</div>",
            unsafe_allow_html=True
        )
        
        # Display trending assets
        if 'trending_assets' in market_trends:
            st.markdown("<h2>Trending Assets</h2>", unsafe_allow_html=True)
            
            trending_df = pd.DataFrame(market_trends['trending_assets'])
            
            if not trending_df.empty:
                fig = px.scatter(
                    trending_df,
                    x='volume_change',
                    y='price_change',
                    color='price_change',
                    color_continuous_scale=['red', 'yellow', 'green'],
                    range_color=[-10, 10],
                    hover_name='symbol',
                    size='market_cap',
                    title='Trending Assets (Volume vs Price Change)'
                )
                
                fig.update_layout(height=500, margin=dict(l=10, r=10, t=50, b=10))
                st.plotly_chart(fig, use_container_width=True)
                
                # Display table of trending assets
                st.dataframe(
                    trending_df[['symbol', 'price_change', 'volume_change', 'market_cap']],
                    use_container_width=True
                )
    else:
        st.error("Failed to fetch market trends data. Please try again later.")