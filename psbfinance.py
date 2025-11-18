import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

# =======================================================
# PAGE CONFIG
# =======================================================
st.set_page_config(
    page_title="FinSight Terminal",
    page_icon="💹",
    layout="wide",
)

# =======================================================
# STYLE (Bloomberg-like)
# =======================================================
st.markdown("""
<style>
body, .stApp {
    background-color: #111217;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #050608;
}
.metric-card {
    background: #191b22;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #333;
}
.accent { color: #F3BA2F; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =======================================================
# SAFE HELPERS
# =======================================================
def safe_float(value):
    try: return float(value)
    except: return None

def safe_percent(x):
    if x is None: return "–"
    try: return f"{x * 100:.2f}%"
    except: return "–"

def fmt_big(x):
    if x is None: return "–"
    try: x = float(x)
    except: return "–"
    if abs(x) >= 1e12: return f"{x/1e12:.2f}T"
    if abs(x) >= 1e9:  return f"{x/1e9:.2f}B"
    if abs(x) >= 1e6:  return f"{x/1e6:.2f}M"
    if abs(x) >= 1e3:  return f"{x/1e3:.2f}K"
    return f"{x:.2f}"

# =======================================================
# SIDEBAR
# =======================================================
with st.sidebar:
    st.title("💹 FinSight Terminal")

    ticker = st.text_input("Main Ticker", "AAPL").upper()

    default_end = date.today()
    default_start = default_end - timedelta(days=365)
    start_date, end_date = st.date_input("Date Range", [default_start, default_end])

    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])

# =======================================================
# LOAD TICKER (NO CACHING)
# =======================================================
try:
    stock = yf.Ticker(ticker)
    info = stock.info
except Exception:
    st.error("Invalid ticker symbol or data unavailable.")
    st.stop()

# =======================================================
# LOAD PRICE DATA SAFELY
# ===============
