import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="PSBFinance", layout="wide")

st.title("📊 PSBFinance — Your Personal Stock Browser")
st.markdown("**Created by Ira-DIVINE, Emelia-Nour, Vinay Rao Gajura**")

ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):").upper()

if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info

    st.subheader(f"{info.get('longName', 'Unknown')} ({ticker})")
    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
    st.write(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
    st.write(info.get('longBusinessSummary', 'No summary available.'))

    st.subheader("📈 Stock Price Chart")
    df = stock.history(period='6mo')
    st.line_chart(df['Close'])

    st.subheader("📥 Download Financial Statements")
    st.download_button("Download Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
    st.download_button("Download Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
    st.download_button("Download Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")
