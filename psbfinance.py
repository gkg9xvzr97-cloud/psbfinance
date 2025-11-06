import streamlit as st

# --------- PAGE CONFIG ---------
st.set_page_config(page_title="PSP Finance", layout="wide")

# --------- SIDEBAR NAV ---------
st.sidebar.title("PSP Finance")
st.sidebar.caption("Explore professional tools for finance students and analysts.")
st.sidebar.markdown("---")

tabs = st.sidebar.radio(" Navigate", [
    " Home",
    " Ticker Research",
    " Compare Companies",
    " Portfolios",
    " Finance News",
    " FX & Derivatives",
    " Screener",
    " Events Calendar",
    " Knowledge Base",
    " About"
])

# --------- HOME PAGE ---------
if tabs == " Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("Welcome to PSP Finance")
        st.markdown("""
        PSP Finance is a research-grade financial analytics platform created by students, for students and analysts.

        **What You Can Do:**
        -  Research public and private companies
        -  Visualize income, balance, and cash flow with explainable ratios
        -  Upload and monitor multiple portfolios
        -  Read real-time financial news via RSS feeds
        -  Compare companies side-by-side with scoring
        -  Track FX & Derivative exposures
        -  Learn from history: crises, Basel rules, and financial theory

        > PSP Finance helps you **analyze professionally, learn deeply, and report clearly**.
        """)
    with col2:
        st.image("https://images.unsplash.com/photo-1553729784-e91953dec042?q=80&w=500&auto=format&fit=crop", width=280)
import yfinance as yf
import pandas as pd
import plotly.express as px

elif tabs == "🔍 Ticker Research":
    st.header("Ticker Research — Company Dashboard")

    ticker = st.text_input("Enter a company ticker (e.g., AAPL, TSLA, NVDA)", "AAPL").upper()
    if ticker:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            st.subheader(f"{info.get('shortName', ticker)} ({ticker})")
            st.caption(info.get("longBusinessSummary", "No description available."))

            col1, col2 = st.columns(2)
            col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}", delta=f"{info.get('regularMarketChangePercent', 0):.2f}%")
            col2.metric("Market Cap", f"${info.get('marketCap', 0) / 1e9:.2f}B")

            # Revenue vs Net Income Chart
            st.markdown("### Revenue vs Net Income")
            fin = stock.financials.T
            if 'Total Revenue' in fin.columns and 'Net Income' in fin.columns:
                df = pd.DataFrame({
                    "Revenue": fin['Total Revenue'],
                    "Net Income": fin['Net Income']
                })
                df.index.name = "Year"
                fig = px.bar(df, barmode="group", title=f"{ticker} — Revenue vs Net Income")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Financial data incomplete on Yahoo Finance.")

            # Expandable Explainable Ratios
            st.markdown("### 🔍 Explainable Financial Ratios")
            with st.expander("Profitability"):
                st.write(f"**ROE:** {info.get('returnOnEquity', 0)*100:.2f}% — Return on shareholders' equity")
                st.write(f"**Net Margin:** {info.get('netMargins', 0)*100:.2f}% — Net income as a % of revenue")
            with st.expander("Valuation"):
                st.write(f"**P/E Ratio (TTM):** {info.get('trailingPE', 'N/A')} — Price / Earnings")
                st.write(f"**P/B Ratio:** {info.get('priceToBook', 'N/A')} — Price / Book value")
            with st.expander("Growth"):
                st.write(f"**Revenue Growth YoY:** {info.get('revenueGrowth', 0)*100:.2f}%")
                st.write(f"**EPS Growth YoY:** {info.get('earningsQuarterlyGrowth', 0)*100:.2f}%")
        except Exception as e:
            st.error(f"Failed to load dat
