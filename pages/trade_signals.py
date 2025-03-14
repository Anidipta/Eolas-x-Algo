import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import datetime

def show_trade_signals(api_base_url, cache_duration):
    """Display trade signals page"""
    st.markdown("<h1>Trade Signals</h1>", unsafe_allow_html=True)
    
    # Fetch trade signals
    @st.cache_data(ttl=cache_duration)
    def fetch_signals():
        try:
            response = requests.get(f"{api_base_url}/trade_signals")
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Error fetching trade signals: {response.status_code}")
                return None
        except Exception as e:
            st.error(f"Failed to fetch trade signals: {str(e)}")
            return None
    
    signals = fetch_signals()
    
    if signals and 'signals' in signals:
        # Tabs for different signal types
        tabs = st.tabs(["All Signals", "Bullish", "Bearish", "Technical Patterns"])
        
        # Filter signals by type
        all_signals = signals['signals']
        bullish_signals = [s for s in all_signals if s['signal_type'] == 'bullish']
        bearish_signals = [s for s in all_signals if s['signal_type'] == 'bearish']
        pattern_signals = [s for s in all_signals if s['signal_type'] == 'pattern']
        
        # Display signals table
        def display_signals_table(signal_list):
            if signal_list:
                # Convert to DataFrame for better display
                df = pd.DataFrame(signal_list)
                
                # Format columns for display
                if 'timestamp' in df.columns:
                    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                
                if 'confidence' in df.columns:
                    df['confidence'] = df['confidence'].apply(lambda x: f"{x:.2f}%")
                
                # Apply color highlighting based on signal type
                def highlight_signals(row):
                    if row['signal_type'] == 'bullish':
                        return ['background-color: rgba(0, 255, 0, 0.2)'] * len(row)
                    elif row['signal_type'] == 'bearish':
                        return ['background-color: rgba(255, 0, 0, 0.2)'] * len(row)
                    else:
                        return ['background-color: rgba(255, 255, 0, 0.1)'] * len(row)
                
                # Display styled dataframe
                styled_df = df.style.apply(highlight_signals, axis=1)
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.info("No signals available in this category.")
        
        # All Signals tab
        with tabs[0]:
            st.markdown("<h3>All Trade Signals</h3>", unsafe_allow_html=True)
            display_signals_table(all_signals)
            
            # Signal distribution chart
            signal_counts = {
                'Bullish': len(bullish_signals),
                'Bearish': len(bearish_signals),
                'Patterns': len(pattern_signals)
            }
            
            fig = px.pie(
                values=list(signal_counts.values()),
                names=list(signal_counts.keys()),
                title="Signal Distribution",
                color=list(signal_counts.keys()),
                color_discrete_map={'Bullish': 'green', 'Bearish': 'red', 'Patterns': 'yellow'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Bullish Signals tab
        with tabs[1]:
            st.markdown("<h3>Bullish Signals</h3>", unsafe_allow_html=True)
            display_signals_table(bullish_signals)
            
            # Top bullish assets bar chart if data available
            if bullish_signals:
                top_bullish = pd.DataFrame(bullish_signals).sort_values('confidence', ascending=False).head(10)
                fig = px.bar(
                    top_bullish,
                    x='symbol',
                    y='confidence',
                    title="Top Bullish Signals by Confidence",
                    color='confidence',
                    color_continuous_scale=['lightgreen', 'darkgreen']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Bearish Signals tab
        with tabs[2]:
            st.markdown("<h3>Bearish Signals</h3>", unsafe_allow_html=True)
            display_signals_table(bearish_signals)
            
            # Top bearish assets bar chart if data available
            if bearish_signals:
                top_bearish = pd.DataFrame(bearish_signals).sort_values('confidence', ascending=False).head(10)
                fig = px.bar(
                    top_bearish,
                    x='symbol',
                    y='confidence',
                    title="Top Bearish Signals by Confidence",
                    color='confidence',
                    color_continuous_scale=['pink', 'darkred']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Technical Patterns tab
        with tabs[3]:
            st.markdown("<h3>Technical Patterns</h3>", unsafe_allow_html=True)
            display_signals_table(pattern_signals)
            
            # Pattern distribution if data available
            if pattern_signals:
                pattern_df = pd.DataFrame(pattern_signals)
                pattern_counts = pattern_df['pattern_name'].value_counts().reset_index()
                pattern_counts.columns = ['pattern', 'count']
                
                fig = px.bar(
                    pattern_counts,
                    x='pattern',
                    y='count',
                    title="Pattern Distribution",
                    color='count',
                    color_continuous_scale=['yellow', 'orange']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        # Signal timeline
        st.markdown("<h2>Signal Timeline</h2>", unsafe_allow_html=True)
        if 'signal_timeline' in signals:
            timeline_df = pd.DataFrame(signals['signal_timeline'])
            timeline_df['date'] = pd.to_datetime(timeline_df['date'])
            
            fig = px.line(
                timeline_df, 
                x='date', 
                y=['bullish_count', 'bearish_count', 'pattern_count'],
                title='Signal Count Over Time',
                labels={'value': 'Signal Count', 'variable': 'Signal Type'},
                color_discrete_map={
                    'bullish_count': 'green',
                    'bearish_count': 'red',
                    'pattern_count': 'yellow'
                }
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Watch list section
        st.markdown("<h2>Your Watch List</h2>", unsafe_allow_html=True)
        
        # Input for adding symbols to watch list
        watch_list = st.session_state.get('watch_list', [])
        
        col1, col2 = st.columns([3, 1])
        with col1:
            new_symbol = st.text_input("Add symbol to watch list", "")
        with col2:
            if st.button("Add Symbol"):
                if new_symbol and new_symbol not in watch_list:
                    watch_list.append(new_symbol.upper())
                    st.session_state.watch_list = watch_list
                    st.rerun()
        
        # Display watch list signals
        if watch_list:
            watch_signals = [s for s in all_signals if s['symbol'] in watch_list]
            st.write(f"Signals for your {len(watch_list)} watched symbols:")
            
            if watch_signals:
                display_signals_table(watch_signals)
            else:
                st.info("No signals for your watched symbols at this time.")
                
            # Show current watch list with delete buttons
            st.write("Your watch list:")
            cols = st.columns(4)
            for i, symbol in enumerate(watch_list):
                col_idx = i % 4
                with cols[col_idx]:
                    if st.button(f"❌ {symbol}", key=f"remove_{symbol}"):
                        watch_list.remove(symbol)
                        st.session_state.watch_list = watch_list
                        st.rerun()
        else:
            st.info("Your watch list is empty. Add symbols above to track specific assets.")
            
    else:
        st.error("Failed to fetch trade signals. Please try again later.")
        
        # Demo data option
        if st.button("Load Demo Data"):
            # Load demo data here
            st.warning("Demo data loaded. Note: This is sample data and not real-time signals.")
            # Implementation for demo data would go here