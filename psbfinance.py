import streamlit as st
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Branding image
st.image("psbfinance image.png", use_column_width=True)  # Make sure this file is in the same folder

# Intro text
st.markdown("""
# 💼 PSBFinance — Your Personal Finance Browser  
### Created by IRA.Divine  
A student-led project designed to make financial data accessible, visual, and downloadable for everyone.  
Built with Python, Streamlit, and real-time market data.

**Mission:** Empower users to explore stocks, analyze performance, and download insights — all in one place.
""")
start_date = st.date_input("Start Date", value=pd.to_datetime("2000-01-01"))
end_date = st.date_input("End Date", value=datetime.today())
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT)").upper()
import yfinance as yf
from pandas_datareader import data as web

def fetch_data(ticker, start, end):
    try:
        df = yf.download(ticker, start=start, end=end)
        if df.empty:
            raise ValueError("Empty from Yahoo")
        return df
    except:
        try:
            df = web.DataReader(ticker, 'av-alpha-vantage', start, end, api_key='YOUR_API_KEY')
            return df
        except:
            st.error("Failed to fetch data from both Yahoo Finance and Alpha Vantage.")
            return pd.DataFrame()

if ticker:
    df = fetch_data(ticker, start_date, end_date)
    if not df.empty:
        st.subheader(f"📈 {ticker} Stock Price")
        st.line_chart(df['Adj Close'])
