import streamlit as st
from datetime import datetime
import pandas as pd

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Branding image (make sure this file is in the same folder)
st.image("psbfinance image.png", use_column_width=True)

# Intro text
st.markdown("""
# 💼 PSBFinance — Your Personal Finance Browser  
### Created by IRA.Divine  
A student-led project designed to make financial data accessible, visual, and downloadable for everyone.  
Built with Python, Streamlit, and real-time market data.
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
rf = st.number_input("Risk-Free Rate (%)", value=2.0)

if not df.empty:
    returns = df['Adj Close'].pct_change().dropna()
    risk_free_rate = rf / 100 / 252
    excess_returns = returns - risk_free_rate

    sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * (252 ** 0.5)
    volatility = returns.std() * (252 ** 0.5)

    st.metric("📊 Sharpe Ratio", f"{sharpe_ratio:.2f}")
    st.metric("📉 Annualized Volatility", f"{volatility:.2%}")

    df['MA20'] = df['Adj Close'].rolling(window=20).mean()
    df['MA50'] = df['Adj Close'].rolling(window=50).mean()

    st.subheader("📈 Price with Moving Averages")
    st.line_chart(df[['Adj Close', 'MA20', 'MA50']])
