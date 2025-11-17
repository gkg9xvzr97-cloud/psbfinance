import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# --------- About Section ---------
st.sidebar.title("About This Finance App")
st.sidebar.markdown("""
**Finance Dashboard Project**

- Real-time stock data & interactive charts
- Compare asset performance (Stocks/Crypto/Forex)
- Analysis: Returns, Volatility, Trends
- Explanation of all sections
- Built with **Streamlit** and **Plotly**
""")

st.title("Finance Dashboard")
st.markdown("""
Welcome to your personalized Finance App!  
Fetch, compare, and visualize market data like **Yahoo Finance** or **Bloomberg**.  
_Explore stock/crypto performance, compare different symbols, and understand financial metrics visually._
""")

# --------- Symbol Selection ---------
st.header("Select Assets to Analyze")

symbols = st.text_input("Enter stock tickers separated by comma (e.g., AAPL, TSLA, MSFT):", "AAPL,TSLA,MSFT")
symbols = [s.strip().upper() for s in symbols.split(",") if s.strip()]

start_date = st.date_input("Start Date:", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date:", pd.to_datetime("today"))

if not symbols:
    st.warning("Please enter at least one asset symbol.")
    st.stop()

# --------- Data Download ---------
@st.cache_data
def fetch_data(symbols, start, end):
    raw_data = yf.download(symbols, start=start, end=end, group_by="ticker", threads=True)
    return raw_data

data = fetch_data(symbols, start_date, end_date)

# --------- Plots and Comparisons ---------
st.header("Plots & Comparisons")

for symbol in symbols:
    st.subheader(f"{symbol} — Price Chart")
    price_data = data['Close'][symbol] if len(symbols) > 1 else data['Close']
    fig = px.line(price_data, title=f"{symbol} Closing Price")
    st.plotly_chart(fig)

# Comparison Plot
st.subheader("Compare Price Trends")
comp_df = data['Close'] if len(symbols) > 1 else pd.DataFrame(data['Close'])
fig2 = px.line(comp_df, title="Price Comparison")
st.plotly_chart(fig2)

# --------- Financial Metrics ---------
st.header("Financial Metrics and Stats")

metrics_df = pd.DataFrame()
for symbol in symbols:
    prices = data['Close'][symbol] if len(symbols) > 1 else data['Close']
    returns = prices.pct_change().dropna()
    metrics_df[symbol] = [
        prices.mean(),              # Average Price
        returns.mean() * 252,       # Annualized Return
        returns.std() * (252**0.5), # Annualized Volatility
        prices.max(),               # Highest Price
        prices.min()                # Lowest Price
    ]
metrics_df.index = ["Avg Price", "Ann. Return", "Ann. Volatility", "Max Price", "Min Price"]
st.dataframe(metrics_df)

# --------- How It Works ---------
st.header("How It Works")
st.markdown("""
- **Select assets:** Type tickers in the box (e.g., AAPL, TSLA)
- **Choose period:** Use date selectors for analysis range
- **Visualizations:** View price trends and comparison for selected assets
- **Stats Table:** Quick look at average, returns, volatility, max/min prices
- **About Section:** Info on use, tech, and structure
""")

st.info("""
**Expand Further:**  
You can add more asset types (crypto, forex) using different APIs, and more advanced analytics (correlation, risk metrics, moving averages, etc).
""")

