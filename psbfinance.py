import streamlit as st
from datetime import datetime
import pandas as pd
import yfinance as yf

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
def fetch_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    if df.empty:
        st.error("No data found. Please check the ticker or date range.")
    return df

if ticker:
    df = fetch_data(ticker, start_date, end_date)
    if not df.empty:
        st.subheader(f"📈 {ticker} Stock Price")
        st.line_chart(df['Adj Close'])
rf = st.number_input("Risk-Free Rate (%)", value=2.0)

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
st.markdown("""
### 📚 What Is the Fama-French 3-Factor Model?

The Fama-French model expands on the traditional CAPM by adding two extra dimensions:
- **Market Risk Premium**: The return of the market minus the risk-free rate.
- **Size Premium (SMB)**: Small minus big — captures the tendency for smaller companies to outperform.
- **Value Premium (HML)**: High minus low — captures the tendency for value stocks to outperform growth stocks.

This model helps explain stock returns more accurately by accounting for company size and value characteristics.
""")
import feedparser

st.subheader("📰 Latest Financial News (France 24)")
feed = feedparser.parse("https://www.france24.com/en/rss")
for entry in feed.entries[:5]:
    st.markdown(f"**{entry.title}** — {entry.published}")
    st.write(entry.link)

if ticker:
    stock = yf.Ticker(ticker)
    news_items = stock.news
    st.subheader(f"🗞️ News for {ticker}")
    for item in news_items[:5]:
        st.markdown(f"**{item['title']}** — {item['publisher']}")
        st.write(item['link'])
st.subheader("📥 Download Financial Statements")

if ticker:
    stock = yf.Ticker(ticker)
    st.download_button("Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
    st.download_button("Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
    st.download_button("Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")
