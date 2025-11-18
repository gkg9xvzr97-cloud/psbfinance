import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="FinSight Terminal",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# CUSTOM STYLING (Bloomberg / Yahoo Finance inspired)
# ---------------------------------------------------------
custom_css = """
<style>
body, .stApp {
    background-color: #111217;
    color: #f5f5f5;
}
section[data-testid="stSidebar"] {
    background-color: #050608;
    border-right: 1px solid #333;
}
.metric-card {
    background: #191b22;
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    border: 1px solid #333;
}
h1, h2, h3, h4 {
    color: #f5f5f5;
}
.accent {
    color: #f3ba2f;
    font-weight: 700;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_ticker_object(ticker: str):
    """Load yfinance Ticker WITHOUT caching errors."""
    try:
        t = yf.Ticker(ticker)
        _ = t.info  # force metadata load
        return t
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_price_history(ticker: str, start: date, end: date, interval="1d"):
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
        if data is None or data.empty:
            return None
        data.dropna(inplace=True)
        return data
    except Exception:
        return None


def safe_get(dct, key, default=None):
    """Safe dictionary getter."""
    val = dct.get(key, default)
    return val if val not in (None, "nan", "None") else default


def format_large_number(x):
    """Format numbers like 1.3M, 5.2B, etc."""
    if x is None:
        return "–"
    try: x = float(x)
    except: return "–"
    if abs(x) >= 1e12: return f"{x/1e12:.2f}T"
    if abs(x) >= 1e9:  return f"{x/1e9:.2f}B"
    if abs(x) >= 1e6:  return f"{x/1e6:.2f}M"
    if abs(x) >= 1e3:  return f"{x/1e3:.2f}K"
    return f"{x:.2f}"


def format_percent(x):
    if x is None:
        return "–"
    try:
        return f"{x * 100:.2f}%"
    except:
        return "–"


def compute_ratios(info, balance_sheet):
    """Calculate basic financial ratios safely."""
    ratios = {}

    ratios["Market Cap"]       = safe_get(info, "marketCap")
    ratios["Trailing P/E"]     = safe_get(info, "trailingPE")
    ratios["Forward P/E"]      = safe_get(info, "forwardPE")
    ratios["PEG"]              = safe_get(info, "pegRatio")
    ratios["P/B"]              = safe_get(info, "priceToBook")
    ratios["Dividend Yield"]   = safe_get(info, "dividendYield")
    ratios["ROA"]              = safe_get(info, "returnOnAssets")
    ratios["ROE"]              = safe_get(info, "returnOnEquity")
    ratios["Profit Margin"]    = safe_get(info, "profitMargins")
    ratios["Operating Margin"] = safe_get(info, "operatingMargins")

    # Balance sheet ratios
    try:
        latest_bs = balance_sheet.iloc[:, 0]

        ca  = latest_bs.get("Total Current Assets")
        cl  = latest_bs.get("Total Current Liabilities")
        li  = latest_bs.get("Total Liab")
        eq  = latest_bs.get("Total Stockholder Equity")

        if ca and cl:
            ratios["Current Ratio"] = ca / cl

        if li and eq:
            ratios["Debt to Equity"] = li / eq

    except Exception:
        pass

    return ratios


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("💹 FinSight Terminal")
    primary_ticker = st.text_input("Ticker", "AAPL").upper()

    default_end = date.today()
    default_start = default_end - timedelta(days=365)
    start_date, end_date = st.date_input("Date Range", [default_start, default_end])

    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])

    comparison_raw = st.text_input("Compare (comma separated)", "MSFT,GOOGL")
    comparison_list = [t.strip().upper() for t in comparison_raw.split(",") if t]

# ---------------------------------------------------------
# MAIN DATA LOAD
# ---------------------------------------------------------
ticker_obj = load_ticker_object(primary_ticker)
if ticker_obj is None:
    st.error("Invalid ticker symbol.")
    st.stop()

price_data = load_price_history(primary_ticker, start_date, end_date, interval)
if price_data is None:
    st.error("Could not load price data.")
    st.stop()

# SAFE financial data loading
info = ticker_obj.info

financials = ticker_obj.financials if isinstance(ticker_obj.financials, pd.DataFrame) else pd.DataFrame()
balance_sheet = ticker_obj.balance_sheet if isinstance(ticker_obj.balance_sheet, pd.DataFrame) else pd.DataFrame()
cashflow = ticker_obj.cashflow if isinstance(ticker_obj.cashflow, pd.DataFrame) else pd.DataFrame()
earnings = ticker_obj.earnings if isinstance(ticker_obj.earnings, pd.DataFrame) else pd.DataFrame()

ratios = compute_ratios(info, balance_sheet)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
company_name = safe_get(info, "longName", primary_ticker)

st.markdown(f"## <span class='accent'>{company_name}</span> ({primary_ticker})", unsafe_allow_html=True)
st.caption(f"{safe_get(info, 'sector', '–')} — {safe_get(info, 'industry', '–')}")

last_close = price_data["Close"].iloc[-1]
prev_close = price_data["Close"].iloc[-2]
change = last_close - prev_close
change_pct = change / prev_close * 100

st.write(f"**{last_close:.2f} USD** ({'🟢' if change >= 0 else '🔻'} {change:.2f}, {change_pct:.2f}%)")
st.divider()

# ---------------------------------------------------------
# TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📈 Overview", "📊 Financials", "📐 Ratios", "📊 Comparisons", "📰 News"]
)

# ----------------------------------
