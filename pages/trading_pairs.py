import streamlit as st
import pandas as pd
#import plotly.express as px
import plotly.graph_objects as go
from pages.utils import *
from pages.api_functions import *

def show_trading_pairs(api_base_url, cache_duration):
    """Display grid trading pairs page"""
    st.markdown("<h1 class='main-header'>Grid Trading Pair Screener</h1>", unsafe_allow_html=True)
    
    # Filters
    st.markdown("<h2 class='sub-header'>Filters</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_volatility = st.slider("Min Volatility (%)", 0.1, 10.0, 0.5, 0.1)
    with col2:
        max_volatility = st.slider("Max Volatility (%)", 1.0, 20.0, 5.0, 0.5)
    with col3:
        min_volume = st.slider("Min 24h Volume (USD)", 
                              100_000, 10_000_000, 1_000_000, 100_000,
                              format="$%d")
    
    # Fetch trading pairs
    trading_pairs = fetch_trading_pairs(
        api_base_url,
        min_volatility=min_volatility,
        max_volatility=max_volatility,
        min_volume=min_volume,
        limit=50
    )
    
    # Show results
    st.markdown("<h2 class='sub-header'>Grid Trading Opportunities</h2>", unsafe_allow_html=True)
    
    if trading_pairs:
        # Show top pair details
        top_pair = trading_pairs[0]
        
        st.markdown(f"### Best Grid Trading Pair: {top_pair['symbol']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Price", f"${top_pair['current_price']:.4f}")
            st.metric("Volatility", f"{top_pair['avg_hourly_volatility']:.2f}%")
        
        with col2:
            st.metric("24h Volume", format_large_number(top_pair['volume_24h']))
            st.metric("Range Width", f"{top_pair['range_width_percent']:.2f}%")
        
        with col3:
            st.metric("Profit Potential", f"{top_pair['estimated_profit_potential']:.2f}%")
            st.metric("Recommended Grids", f"{top_pair['suggested_grid_levels']}")
        
        # Create a visualization of the grid levels
        price_range = [top_pair['price_range_low'], top_pair['price_range_high']]
        current_price = top_pair['current_price']
        grid_levels = top_pair['suggested_grid_levels']
        
        # Calculate grid lines
        grid_prices = []
        price_step = (price_range[1] - price_range[0]) / grid_levels
        
        for i in range(grid_levels + 1):
            grid_prices.append(price_range[0] + i * price_step)
        
        # Create the plot
        fig = go.Figure()
        
        # Add price range area
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[price_range[0], price_range[0]],
            fill=None,
            mode='lines',
            line_color='rgba(0,0,0,0)',
            showlegend=False,
            hoverinfo='skip',
        ))
        
        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[price_range[1], price_range[1]],
            fill='tonexty',
            mode='lines',
            line_color='rgba(0,0,0,0)',
            fillcolor='rgba(173, 216, 230, 0.3)',
            showlegend=False,
            hoverinfo='skip',
        ))
        
        # Add grid lines
        for price in grid_prices:
            fig.add_shape(
                type="line",
                x0=0, y0=price,
                x1=1, y1=price,
                line=dict(color="rgba(70, 130, 180, 0.5)", width=1, dash="dash"),
            )
            
            # Add price labels
            fig.add_annotation(
                x=1.01,
                y=price,
                text=f"${price:.4f}",
                showarrow=False,
                xanchor='left',
            )
            
        # Add current price line
        fig.add_shape(
            type="line",
            x0=0, y0=current_price,
            x1=1, y1=current_price,
            line=dict(color="black", width=2),
        )
        
        fig.add_annotation(
            x=0,
            y=current_price,
            text=f"Current Price: ${current_price:.4f}",
            showarrow=False,
            xanchor='left',
            bgcolor="rgba(255, 255, 255, 0.8)",
        )
        
        # Update layout
        fig.update_layout(
            title=f"Grid Trading Visualization for {top_pair['symbol']}",
            height=400,
            showlegend=False,
            xaxis_visible=False,
            xaxis_showticklabels=False,
            margin=dict(l=20, r=100, t=50, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display the trading pairs table
        st.markdown("### All Grid Trading Pairs")
        
        df = pd.DataFrame(trading_pairs)
        
        # Format the data for display
        display_df = df[['symbol', 'current_price', 'avg_hourly_volatility', 
                        'range_width_percent', 'estimated_profit_potential', 'suggested_grid_levels']]
        
        display_df.columns = ['Symbol', 'Current Price', 'Avg Volatility (%)', 
                            'Range Width (%)', 'Profit Potential (%)', 'Grid Levels']
        
        st.dataframe(
            display_df.style.format({
                'Current Price': '${:.4f}',
                'Avg Volatility (%)': '{:.2f}',
                'Range Width (%)': '{:.2f}',
                'Profit Potential (%)': '{:.2f}'
            }),
            height=400,
            use_container_width=True
        )
        
        # Download button for CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Trading Pairs as CSV",
            data=csv,
            file_name=f"grid_trading_pairs_{pd.Timestamp.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv",
        )
    else:
        st.error("No grid trading pairs match your criteria. Try adjusting the filters.")