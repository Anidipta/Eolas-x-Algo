import os
import streamlit as st
from streamlit_option_menu import option_menu
import threading
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import time
from pages import home, login, dashboard, grid_strategy, ai_tokens, social_sentiment, trading_bot, settings

# Load environment variables
load_dotenv()

# Initialize Firebase (if not already initialized)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS"))
        firebase_admin.initialize_app(cred)
        db = firestore.client()
    except Exception as e:
        st.error(f"Firebase initialization error: {e}")
        db = None
else:
    db = firestore.client()

# App configuration
st.set_page_config(
    page_title="CryptoGridPro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "wallet_connected" not in st.session_state:
    st.session_state.wallet_connected = False
if "wallet_address" not in st.session_state:
    st.session_state.wallet_address = None
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Apply custom styling
def apply_custom_styling():
    # Main gradient background
    st.markdown("""
    <style>
        .main {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            color: white;
        }
        .stApp {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        }
        .css-1d391kg, .css-1wrcr25 {
            background-color: rgba(14, 17, 23, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .stButton>button {
            background: linear-gradient(45deg, #6a11cb, #2575fc);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 24px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background: linear-gradient(45deg, #2575fc, #6a11cb);
            box-shadow: 0 0 15px rgba(106, 17, 203, 0.5);
            transform: translateY(-2px);
        }
        .css-1hverof {
            background-color: rgba(255, 255, 255, 0.1);
        }
        /* Custom success message */
        .success-message {
            background-color: rgba(25, 135, 84, 0.2);
            color: #d1fae5;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #16a34a;
        }
        /* Custom error message */
        .error-message {
            background-color: rgba(220, 53, 69, 0.2);
            color: #fee2e2;
            padding: 10px;
            border-radius: 5px;
            border-left: 5px solid #dc3545;
        }
    </style>
    """, unsafe_allow_html=True)

# Apply styling
apply_custom_styling()

# Data fetching thread
def background_data_fetcher():
    while True:
        if st.session_state.authenticated:
            try:
                # Update market data in session state
                from api.binance_api import fetch_top_pairs
                from api.coingecko_api import fetch_ai_tokens
                
                if 'market_data' not in st.session_state:
                    st.session_state.market_data = {}
                
                st.session_state.market_data['top_pairs'] = fetch_top_pairs(limit=20)
                st.session_state.market_data['ai_tokens'] = fetch_ai_tokens()
                
                # Sleep for 60 seconds
                time.sleep(60)
            except Exception as e:
                print(f"Error in background data fetcher: {e}")
                time.sleep(30)
        else:
            time.sleep(5)

# Start background thread if not already running
if 'data_thread_started' not in st.session_state:
    data_thread = threading.Thread(target=background_data_fetcher, daemon=True)
    data_thread.start()
    st.session_state.data_thread_started = True

# Main navigation logic
def main():
    with st.sidebar:
        st.image("assets/logo.png", width=200)
        
        if not st.session_state.authenticated:
            selected = option_menu(
                menu_title="Navigation",
                options=["Home", "Login", "Sign Up"],
                icons=["house", "person", "person-plus"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "rgba(0,0,0,0.2)"},
                    "icon": {"color": "orange", "font-size": "25px"},
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
                    "nav-link-selected": {"background-color": "rgba(106, 17, 203, 0.3)"},
                }
            )
        else:
            # User info section
            st.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin-bottom: 20px">
                <h3 style="margin:0;">Welcome!</h3>
                <p style="margin:0;">ID: {st.session_state.user_id[:8]}...</p>
                <p style="margin:0;">Status: {'🟢 Active' if st.session_state.authenticated else '🔴 Not logged in'}</p>
                <p style="margin:0;">Wallet: {'🔗 Connected' if st.session_state.wallet_connected else '❌ Not connected'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Main navigation for authenticated users
            selected = option_menu(
                menu_title="Navigation",
                options=["Dashboard", "Grid Strategy", "AI Tokens", "Social Sentiment", "Trading Bot", "Settings"],
                icons=["speedometer2", "grid", "robot", "people", "cpu", "gear"],
                menu_icon="cast",
                default_index=0,
                styles={
                    "container": {"padding": "5px", "background-color": "rgba(0,0,0,0.2)"},
                    "icon": {"color": "orange", "font-size": "25px"},
                    "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
                    "nav-link-selected": {"background-color": "rgba(106, 17, 203, 0.3)"},
                }
            )
            
            # Logout button at the bottom of sidebar
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_id = None
                st.session_state.wallet_connected = False
                st.session_state.wallet_address = None
                st.rerun()
    
    # Render selected page
    if not st.session_state.authenticated:
        if selected == "Home":
            home.show()
        elif selected == "Login":
            login.show_login()
        elif selected == "Sign Up":
            login.show_signup()
    else:
        if selected == "Dashboard":
            dashboard.show()
        elif selected == "Grid Strategy":
            grid_strategy.show()
        elif selected == "AI Tokens":
            ai_tokens.show()
        elif selected == "Social Sentiment":
            social_sentiment.show()
        elif selected == "Trading Bot":
            trading_bot.show()
        elif selected == "Settings":
            settings.show()

if __name__ == "__main__":
    main()