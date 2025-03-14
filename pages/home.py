# pages/home.py
import streamlit as st
from streamlit_lottie import st_lottie
import json
import requests

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def show():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("# CryptoGridPro")
        st.markdown("## Intelligent Crypto Grid Trading")
        
        st.markdown("""
        Welcome to CryptoGridPro, your complete solution for intelligent cryptocurrency grid trading. 
        Our platform combines advanced technical analysis with AI-driven insights to help you 
        make better trading decisions.
        
        ### Key Features:
        - **Grid Trading Made Easy**: Automated grid strategy creation and backtesting
        - **AI Token Tracker**: Monitor performance of AI-related tokens
        - **Social Sentiment Analysis**: Track market sentiment from social media
        - **Real-time Signals**: Get actionable insights for your trades
        """)
        
        st.markdown("### Get Started Now")
        col1a, col1b = st.columns(2)
        with col1a:
            st.button("Sign Up", key="home_signup", help="Create your account")
        with col1b:
            st.button("Login", key="home_login", help="Access your account")
    
    with col2:
        # Load Lottie animation
        lottie_crypto = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_iivslayz.json")
        st_lottie(lottie_crypto, height=400, key="crypto_animation")
        
        st.markdown("""
        ### Why CryptoGridPro?
        - **Backtested Strategies**: Create and test grid strategies before investing
        - **AI-Powered Analysis**: Get insights from AI token movements
        - **Real-time Data**: Stay updated with live market data
        - **Secure Platform**: Your data and funds stay secure
        """)
    
    # Features section
    st.markdown("---")
    st.markdown("## Platform Features")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Grid Trading")
        st.markdown("""
        Optimize your crypto trading with our grid trading strategy builder. 
        Define your investment amount, set your risk tolerance, and let our 
        system create the perfect grid strategy for your needs.
        """)
    
    with col2:
        st.markdown("### AI Token Tracker")
        st.markdown("""
        Stay updated on the performance of AI-related tokens. Our specialized 
        tracker monitors the latest trends and movements in AI tokens, helping 
        you identify potential opportunities.
        """)
    
    with col3:
        st.markdown("### Social Sentiment")
        st.markdown("""
        Make informed decisions based on social media sentiment. Our platform 
        analyzes online discussions about cryptocurrencies to provide insights 
        into market sentiment and potential price movements.
        """)
    
    # Testimonials (simulated)
    st.markdown("---")
    st.markdown("## What Users Say")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        > "CryptoGridPro has completely transformed my trading experience. 
        > The grid strategies are easy to set up and have consistently 
        > delivered results." - **Alex K.**
        """)
    
    with col2:
        st.markdown("""
        > "The AI token tracker has helped me discover opportunities I would have 
        > otherwise missed. This platform offers great value for both beginners and 
        > experienced traders." - **Sarah M.**
        """)
    
    # Call to action
    st.markdown("---")
    st.markdown("## Ready to start your grid trading journey?")
    st.markdown("Sign up now and get access to all features!")
    
    col1, _, col2 = st.columns([1, 2, 1])
    with col1:
        if st.button("Create Account", use_container_width=True):
            st.session_state.show_page = "signup"
            st.rerun()
    with col2:
        if st.button("Learn More", use_container_width=True):
            st.session_state.show_page = "about"
            st.rerun()
