import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# --------- CONFIG ---------
st.set_page_config(page_title="PSP Finance", layout="wide")

# --------- SIDEBAR NAVIGATION ---------
st.sidebar.title("PSP Finance")
st.sidebar.caption("Explore professional tools for finance students and analysts.")
st.sidebar.markdown("---")

tabs = st.sidebar.radio("📁 Navigate", [
    "Home",  # << This MUST match the condition you check later
    "Ticker Research",
    "Compare Companies"
])
# --------- HOME TAB ---------
if tabs == "Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("Welcome to PSP Finance")
        st.markdown("""
        PSP Finance is a research-grade financial analytics platform built for finance students, researchers, and analysts.

        **Capabilities:**
        - Research public and private companies with explainable financials  
        - Visualize income, balance sheet, and cash flow with decomposition plots  
        - Compare company fundamentals side-by-side with scoring  
        - Read real-time financial news from professional RSS feeds  
        - Track FX rates, commodity exposure, and derivative risks  
        - Upload and manage multiple student or investor portfolios  
        - Learn from historical financial crises, regulations, and Basel reforms  

        > Designed to bridge classroom theory with real-world financial analysis.
        """)
    with col2:
        st.image("capilotimage.png", caption="Explore charts, fundamentals, and markets", width=280)
# --------- COMPARE TAB ---------
elif tabs == "Compare Companies":
    st.header("Compare Company Fundamentals & Price Performance")

    raw = st.text_input("Enter tickers (comma-separated)", value="AAPL, MSFT, TSLA")
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]

    if tickers:
        st.markdown("### 📈 Normalized 5-Year Price Chart")
        hist = yf.download(tickers, period="5y", auto_adjust=True)["Close"]
        norm = hist / hist.iloc[0] * 100
        st.line_chart(norm)

        st.markdown("### 🧮 Fundamental Comparisons")
        data = []
        for t in tickers:
            try:
                info = yf.Ticker(t).info
                data.append({
                    "Ticker": t,
                    "Name": info.get("shortName", t),
                    "Market Cap (B)": round(info.get("marketCap", 0)/1e9, 2),
                    "P/E Ratio": info.get("trailingPE", None),
                    "ROE (%)": round(info.get("returnOnEquity", 0)*100, 2),
                    "Revenue Growth (%)": round(info.get("revenueGrowth", 0)*100, 2)
                })
            except:
                continue

        df = pd.DataFrame(data)
        st.dataframe(df)

        if not df.empty:
            st.markdown("#### ✅ Best Performer (Price Return)")
            last = norm.iloc[-1]
            best = last.idxmax()
            st.success(f"Top price return: **{best}** with a {last[best]-100:.2f}% gain over 5 years.")

