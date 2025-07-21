# Crypto Trading Insights Dashboard

## Overview
This project is a **real-time crypto trading insights dashboard** built using **Streamlit** and **FastAPI**. It provides automated trading insights, including:
- **Grid Trading Pair Screener** (Identifies profitable grid trading opportunities)
- **AI Token Tracking** (Monitors AI-related crypto assets)
- **Early Market Trend Detection** (Analyzes market sentiment and price movements)
- **Live Trading Signals** (Buy/Sell indicators for top trading pairs)

## Features
✅ **Live Cryptocurrency Data** – Fetches real-time price, volume, and order book details from Binance API & CoinGecko API.  
✅ **Grid Trading Pair Screener** – Identifies low/high volatility pairs for grid trading strategies.  
✅ **AI Token Price Tracking** – Monitors AI-related tokens to support informed trading decisions.  
✅ **Early Market Trend Detection** – Uses social sentiment analysis and price movement data.  
✅ **FastAPI Backend** – Serves live trading insights and signals.  
✅ **Streamlit Frontend** – Displays charts, analytics, and alerts in a user-friendly UI.

---

## Tech Stack
- **Python** – Core programming language
- **FastAPI** – Backend API for serving trading signals
- **Streamlit** – Web dashboard for visualization
- **Binance API & CoinGecko API** – Real-time cryptocurrency data
- **TA-Lib & Pandas** – Technical analysis and data processing
- **Matplotlib & Plotly** – Data visualization
- **SQLite** – Database for trade logs (optional)

---

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/Anidipta/Eolas-x-Algo.git
cd Eolas-x-Algo
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Running the Application
### 1. Start the FastAPI Backend
```bash
python backend/main.py
```
- Access API Docs at: **`http://127.0.0.1:8000/docs`**

### 2. Start the Streamlit Frontend
```bash
streamlit run app.py
```
- Open in browser: **`http://localhost:8501`**

---

## API Endpoints (FastAPI)
| Method | Endpoint | Description |
|--------|----------------|--------------------------------|
| GET | `/trading-pairs` | Get recommended trading pairs |
| GET | `/ai-tokens` | Get AI token price movements |
| GET | `/market-trends` | Get early market trend insights |
| GET | `/trade-signals` | Get current buy/sell signals |

---

## Project Structure
```
Eolas x Algo/
│-- backend/
│   ├── data_fetcher.py  # Fetches crypto data from APIs
│   ├── main.py  # FastAPI backend
│   ├── trading_logic.py  # Implements trading strategies
│
│-- pages/
│   ├── ai_tokens.py  # AI token tracking
│   ├── api_functions.py  # API-related utilities
│   ├── dashboard_overview.py  # Overview of the trading dashboard
│   ├── market_trends.py  # Market trend analysis
│   ├── trade_signals.py  # Trading signal indicators
│   ├── trading_pairs.py  # Displays trading pairs
│   ├── utils.py  # Utility functions
│
│-- app.py  # Streamlit dashboard entry point
│-- requirements.txt  # Project dependencies
│-- README.md  # Project documentation
│-- .gitignore  # Git ignore file

```

---

## Future Enhancements
🚀 **Automated Trading Execution** – Integrate Binance trading APIs to execute trades automatically.  
🚀 **Sentiment Analysis from Twitter/Reddit** – Enhance trend detection.  
🚀 **User Authentication** – Allow users to save preferences.  
