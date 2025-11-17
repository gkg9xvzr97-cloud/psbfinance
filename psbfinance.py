# app.py

import streamlit as st

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="PSP Finance", layout="wide")

# ---------------------- Custom Styling ----------------------
st.markdown("""
<style>
:root{
  --ink:#0e1a2b; --muted:#6b7b91; --card:#f6f8fb; --accent:#0d6efd;
}
html, body, .block-container { color: var(--ink); }
.stButton>button {
  background: var(--accent); color: #fff; border: 0; border-radius: 10px;
  padding: 10px 18px; font-weight: 600;
}
.card {
  background: var(--card); border: 1px solid #e6ebf2; border-radius: 14px; padding: 16px 18px;
}
.smallnote { color: var(--muted); font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Navigation ----------------------
PAGES = [
    "Home",
    "Dashboard",
    "Portfolio Optimizer",
    "Failed Companies",
    "Unpopular Investments",
    "Why Financial Models Fail",
    "Charts & Data",
    "Lessons for the Future",
    "News Feed",
    "Public Company Financials Lookup",
    "About"
]

st.sidebar.title("PSP Finance")
page = st.sidebar.radio("Navigate", PAGES)

# ---------------------- Page Functions ----------------------
def home():
    st.title("Welcome to PSP Finance")
    st.write("This is the starting point. We’ll add features step by step.")

def dashboard():
    st.title("Dashboard")
    st.info("Placeholder: will show live market charts and risk metrics.")

def optimizer():
    st.title("Portfolio Optimizer")
    st.info("Placeholder: will implement Modern Portfolio Theory.")

def failed_companies():
    st.title("Failed Companies")
    st.info("Placeholder: case studies like Enron, Lehman Brothers, Wirecard.")

def unpopular_investments():
    st.title("Unpopular Investments")
    st.info("Placeholder: assets that underperformed or lost investor confidence.")

def models_fail():
    st.title("Why Financial Models Fail")
    st.info("Placeholder: explanations of model limitations.")

def charts_data():
    st.title("Charts & Data")
    st.info("Placeholder: company comparisons, index performance, risk/return scatter.")

def lessons_future():
    st.title("Lessons for the Future")
    st.info("Placeholder: diversification, risk management, realistic assumptions.")

def news_feed():
    st.title("News Feed")
    st.info("Placeholder: finance RSS feeds and keyword filters.")

def financials_lookup():
    st.title("Public Company Financials Lookup")
    st.info("Placeholder: income statement, balance sheet, cash flow.")

def about():
    st.title("About PSP Finance")
    st.markdown("""
    ### What is PSP Finance?
    PSP Finance is a research and learning platform that combines **live market data**,  
    **portfolio optimization models**, and **educational case studies**.

    ### Features
    - **Dashboard:** Multi-ticker charts, rolling risk, sector snapshots.
    - **Portfolio Optimizer:** Mean-variance analytics, efficient frontier, Sharpe ratio.
    - **Failed Companies:** Case studies of collapsed firms.
    - **Unpopular Investments:** Lessons from risky bets.
    - **Why Models Fail:** Educational breakdown of assumptions and pitfalls.
    - **Charts & Data:** Company comparisons, index performance, risk/return scatter.
    - **Lessons for the Future:** Practical takeaways for investors.
    - **News Feed:** Live updates from financial sources.
    - **Financials Lookup:** Company fundamentals (Income, Balance Sheet, Cash Flow).
    """)

# ---------------------- Router ----------------------
ROUTES = {
    "Home": home,
    "Dashboard": dashboard,
    "Portfolio Optimizer": optimizer,
    "Failed Companies": failed_companies,
    "Unpopular Investments": unpopular_investments,
    "Why Financial Models Fail": models_fail,
    "Charts & Data": charts_data,
    "Lessons for the Future": lessons_future,
    "News Feed": news_feed,
    "Public Company Financials Lookup": financials_lookup,
    "About": about,
}

ROUTES[page]()
import yfinance as yf
import pandas as pd
import numpy as np

# Utility: load prices
@st.cache_data(ttl=300)
def load_prices(tickers, period="1y", interval="1d"):
    if isinstance(tickers, str):
        tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not tickers:
        return pd.DataFrame()
    df = yf.download(tickers, period=period, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    return df.dropna(how="all")

# Risk metrics
def rolling_vol(series, window=60):
    rets = series.pct_change().dropna()
    return (rets.rolling(window).std() * np.sqrt(252)).dropna()

def rolling_beta(asset, benchmark, window=60):
    ar = asset.pct_change().dropna()
    br = benchmark.pct_change().dropna()
    idx = ar.index.intersection(br.index)
    ar, br = ar.loc[idx], br.loc[idx]
    cov = ar.rolling(window).cov(br)
    var = br.rolling(window).var()
    return (cov / var).dropna()

def max_drawdown(series):
    cummax = series.cummax()
    dd = (series / cummax) - 1.0
    return float(dd.min())

# Dashboard page
def dashboard():
    st.title("Global Market Dashboard")

    # Presets
    presets = {
        "US Tech": "AAPL, MSFT, NVDA, AMZN, GOOGL",
        "US Banks": "JPM, BAC, WFC, C",
        "Energy": "XOM, CVX, SLB, BP",
        "Europe": "NESN.SW, ASML.AS, SAP.DE, SIE.DE",
        "Crypto": "BTC-USD, ETH-USD"
    }

    st.caption("💡 Try presets or enter your own tickers.")
    cols = st.columns(len(presets))
    for i, (label, tick) in enumerate(presets.items()):
        if cols[i].button(label):
            st.session_state["dash_tickers"] = tick

    raw = st.text_input("Tickers (comma-separated)", value=st.session_state.get("dash_tickers", "AAPL, MSFT, NVDA"))
    period = st.selectbox("Period", ["6mo", "1y", "2y", "3y", "5y"], index=1)

    pxs = load_prices(raw, period=period)
    if not pxs.empty:
        norm = pxs / pxs.iloc[0] * 100
        st.line_chart(norm)
        st.download_button("Download Data", data=pxs.to_csv().encode("utf-8"), file_name="prices.csv")

        # Rolling risk metrics
        st.markdown("### Rolling Risk Analysis")
        try:
            t_sel = [t.strip() for t in raw.split(",") if t.strip()][0]
            bench = "SPY"
            prices_risk = load_prices([t_sel, bench], period=period)
            a, b = prices_risk.iloc[:, 0], prices_risk.iloc[:, 1]
            vol60 = rolling_vol(a)
            beta60 = rolling_beta(a, b)
            dd = max_drawdown(a)

            c1, c2, c3 = st.columns(3)
            c1.metric("Max Drawdown", f"{dd:.2%}")
            c2.metric("Current 60d Vol", f"{vol60.iloc[-1]:.2%}")
            c3.metric("Current 60d Beta vs SPY", f"{beta60.iloc[-1]:.2f}")

            st.line_chart(pd.DataFrame({"60d Vol": vol60, "60d Beta": beta60}))
        except Exception:
            st.info("Select at least one ticker for risk metrics.")

        # Sector snapshot
        st.markdown("### Sector Snapshot (SPDR ETFs)")
        sector_map = {"SPY":"S&P 500","XLK":"Tech","XLF":"Financials","XLE":"Energy","XLY":"Consumer Disc","XLV":"Health","XLP":"Staples"}
        sec_df = load_prices(list(sector_map.keys()), period="6mo")
        if not sec_df.empty:
            perf = (sec_df.iloc[-1] / sec_df.iloc[0] - 1).sort_values(ascending=False)
            perf.index = [sector_map.get(k, k) for k in perf.index]
            st.bar_chart(perf * 100)
