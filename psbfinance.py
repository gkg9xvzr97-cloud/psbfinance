import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.graph_objs as go

# --- Sidebar About ---
st.sidebar.title("About This App")
st.sidebar.info("""
A Yahoo Finance-like dashboard.  
- Live stock quotes and charts  
- Latest financial news  
- Company info & comparisons  
- Made with Streamlit, yfinance, newsapi
""")

st.title("Yahoo Finance Style Dashboard")

st.write("""
**Track stocks, read the latest news, and visualize financial metrics — all in one place.**
""")

# --- Select Company Symbol ---
st.header("Search Stock Symbol")
symbol = st.text_input("Enter Symbol", "AAPL").upper()
start_date = st.date_input("Start Date", pd.to_datetime("2023-01-01"))
end_date = st.date_input("End Date", pd.to_datetime("today"))

# --- Fetch Data ---
@st.cache_data
def get_data(symbol, start, end):
    return yf.download(symbol, start=start, end=end)

try:
    df = get_data(symbol, start_date, end_date)
except Exception as e:
    st.error("Couldn't fetch data")

# --- Overview & Company Info ---
st.header("Company Information")
company = yf.Ticker(symbol)
info = company.info
st.subheader(f"{info.get('longName', symbol)}")
st.write(info.get('longBusinessSummary', 'No business summary available.'))

# --- Price Plot ---
st.header("Stock Price")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Close'))
fig.update_layout(title=f"{symbol} Stock Price", xaxis_title="Date", yaxis_title="Price ($)")
st.plotly_chart(fig)

# --- Volume Plot ---
st.header("Volume")
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume'))
fig2.update_layout(title=f"{symbol} Volume", xaxis_title="Date", yaxis_title="Volume")
st.plotly_chart(fig2)

# --- Comparison Plot ---
st.header("Compare With Another Symbol")
compare_symbol = st.text_input("Compare With (Symbol)", "MSFT").upper()
df_compare = get_data(compare_symbol, start_date, end_date)
comp_df = pd.DataFrame({symbol: df['Close'], compare_symbol: df_compare['Close']}).dropna()
fig3 = go.Figure()
for s in comp_df.columns:
    fig3.add_trace(go.Scatter(x=comp_df.index, y=comp_df[s], mode='lines', name=s))
fig3.update_layout(title=f"{symbol} vs {compare_symbol}", xaxis_title="Date", yaxis_title="Price ($)")
st.plotly_chart(fig3)

# --- Financial News Section ---
st.header("Latest News")
def get_news(symbol):
    # Replace YOUR_NEWSAPI_KEY with your actual key
    url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey=YOUR_NEWSAPI_KEY&pageSize=5"
    r = requests.get(url)
    articles = r.json().get("articles", [])
    return articles

news = get_news(symbol)
for n in news:
    st.subheader(n.get('title', 'No title'))
    st.write(n.get('description', ''))
    st.markdown(f"[Read more]({n.get('url', '#')})")

# --- How It Works Section ---
st.sidebar.header("How To Use")
st.sidebar.markdown("""
- Type in a stock ticker & time period  
- Get company info, price, volume  
- Compare with another symbol  
- Read up-to-date financial news  
""")
