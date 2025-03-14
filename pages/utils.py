import numpy as np
import streamlit as st

def format_large_number(num):
    """Format large numbers for display"""
    if num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    elif num >= 1_000:
        return f"${num / 1_000:.2f}K"
    else:
        return f"${num:.2f}"

def get_signal_color(signal):
    """Get color based on trading signal"""
    if signal == "buy":
        return "green"
    elif signal == "sell":
        return "red"
    else:
        return "gray"

def get_trend_arrow(value):
    """Return trend arrow based on value"""
    if value > 0:
        return "↑"
    elif value < 0:
        return "↓"
    else:
        return "→"