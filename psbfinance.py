import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(page_title="Finance Failures Analytics", layout="wide")

st.title("📉 Finance Failures Analytics")
st.write("Analyze failed companies, unpopular investments, and financial model breakdowns.")

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Navigate",
    [
        "Home",
        "Failed Companies",
        "Unpopular Investments",
        "Financial Model Failures",
        "Charts & Data",
        "News",
        "Public Company Financials",
    ]
)

# Home Page
if page == "Home":
    st.header("🏠 Home")
    st.write("Welcome to the Finance Failures Analytics dashboard.")

# Failed Companies Page
elif page == "Failed Companies":
    st.header("💀 Failed Companies")

    failed_list = {
        "Lehman Brothers": "Bankruptcy due to subprime crisis (2008)",
        "Enron": "Fraud & accounting scandal (2001)",
        "FTX": "Crypto fraud collapse (2022)",
        "Kodak": "Failure to innovate (2012)",
    }

    st.write(pd.DataFrame.from_dict(failed_list, orient="index", columns=["Reason for Failure"]))

# Unpopular Investments
elif page == "Unpopular Investments":
    st.header("📉 Unpopular Investments")

    unpopular = {
        "Penny Stocks": "Highly speculative & risky",
        "Annuities": "Low returns & long lock-in periods",
        "Municipal Bonds": "Low interest, low risk",
        "Long-term Bonds": "Highly sensitive to inflation",
    }

    st.write(pd.DataFrame.from_dict(unpopular, orient="index", columns=["Why Unpopular"]))

# Financial Model Failures
elif page == "Financial Model Failures":
    st.header("📊 Why Financial Models Fail")
    st.write(
        """
        Common reasons:
        - Wrong assumptions
        - Overfitting
        - Ignoring market shocks
        - Human behavioral biases
        - Poor data quality
        """
    )

# Charts & Data
elif page == "Charts & Data":
    st.header("📈 Index Comparison Chart")

    tickers = ["^GSPC", "^IXIC", "^DJI"]
    names = {"^GSPC": "S&P 500", "^IXIC": "NASDAQ", "^DJI": "Dow Jones"}

    data = {}
    for t in tickers:
        df = yf.download(t, period="1y")
        data[names[t]] = df["Close"]

    combined = pd.DataFrame(data)
    fig = px.line(combined, title="Market Index Comparison")
    st.plotly_chart(fig, use_container_width=True)

# News Page
elif page == "News":
    st.header("📰 Finance News (Static Placeholder)")
    st.write("Live news API can be added.")

# Public Company Financials
elif page == "Public Company Financials":
    st.header("🏢 Public Company Financial Lookup")

    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL, TSLA, AMZN)")

    if symbol:
        stock = yf.Ticker(symbol)

        st.subheader("📄 Income Statement")
        st.write(stock.financials)

        st.subheader("📂 Balance Sheet")
        st.write(stock.balance_sheet)

        st.subheader("💵 Cash Flow")
        st.write(stock.cashflow)

        hist = stock.history(period="1y")
        fig = px.line(hist, y="Close", title=f"{symbol} Price History (1 year)")
        st.plotly_chart(fig, use_container_width=True)

st.write("
---
&copy; 2025 Finance Failures Analytics | Built for Tech for Business")
