import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# Load your API key from the .env file
load_dotenv()
API_KEY = os.getenv('API_KEY')

def fetch_data(symbol):
    """Fetches daily close prices for the given stock symbol from Alpha Vantage."""
    url = (
        "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={symbol}&outputsize=compact&apikey={API_KEY}"
    )
    r = requests.get(url)
    data = r.json()
    # Error handling for API response
    if "Time Series (Daily)" not in data:
        return None
    df = pd.DataFrame(data["Time Series (Daily)"]).T
    df = df.rename(columns={"5. adjusted close": "Close"})
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df[["Close"]]

st.title("📈 Stock Comparison App")

st.subheader("Compare closing prices of two stocks")

symbol = st.text_input("Enter Main Ticker (e.g. AAPL)", "AAPL")
compare_symbol = st.text_input("Enter Compare Ticker (e.g. MSFT)", "MSFT")

if st.button("Compare"):
    if not API_KEY:
        st.error("API Key not found. Please set it in your .env file.")
    else:
        with st.spinner("Fetching data..."):
            df = fetch_data(symbol)
            df_compare = fetch_data(compare_symbol)

        # Error checks on returned data
        if (df is None or df.empty) or (df_compare is None or df_compare.empty):
            st.error("Failed to fetch stock data for one or both tickers. Check ticker spelling and API key/limits.")
        else:
            # Align and concatenate by date index
            comp_df = pd.concat([df["Close"], df_compare["Close"]], axis=1, join='inner')
            comp_df.columns = [symbol, compare_symbol]
            comp_df = comp_df.dropna()
            st.line_chart(comp_df)
            st.write("Recent data comparison:", comp_df.tail())
            st.success("Chart generated successfully!")

st.markdown("""
*Features included:*
- Secure API key handling (.env)
- Ticker error handling
- Financial-style chart and data table
""")
