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
st.subheader("📦 Portfolio Tracker")

portfolio_tickers = st.text_input("Enter multiple tickers separated by commas (e.g., AAPL, TSLA, MSFT)").upper()

if portfolio_tickers:
    tickers = [t.strip() for t in portfolio_tickers.split(",")]
    portfolio_data = yf.download(tickers, start=start_date, end=end_date)['Adj Close']

    if not portfolio_data.empty:
        st.line_chart(portfolio_data)
        st.write("📊 Portfolio Daily Returns")
        daily_returns = portfolio_data.pct_change().dropna()
        st.dataframe(daily_returns.tail())
import numpy as np
import matplotlib.pyplot as plt

st.subheader("🧮 Monte Carlo Simulation")

num_simulations = st.slider("Number of Simulations", min_value=100, max_value=1000, value=500)
num_days = st.slider("Number of Days to Simulate", min_value=30, max_value=365, value=252)

if ticker:
    df = fetch_data(ticker, start_date, end_date)

    if df is not None and not df.empty:
        # All your analysis and charts go here
        st.subheader(f"📈 {ticker} Stock Price")
        st.line_chart(df['Adj Close'])

        # Sharpe Ratio, Volatility, etc.
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
    else:
        st.warning("No data found for this ticker.")

st.subheader("🏢 Global Firms & FinTech Reports")

reports = {
    "KPMG UK Financials 2024": "https://assets.kpmg.com/content/dam/kpmgsites/uk/pdf/2025/06/uk-members-report-and-financial-statements-2024.pdf",
    "KPMG Integrated Report": "https://corporatereporting.kpmg.nl/downloads",
    "EY SEC Annual Reports 2024": "https://www.ey.com/en_us/technical/accountinglink/2024-sec-annual-reports-form-10-k",
    "EY Global Revenue Report": "https://www.ey.com/en_gl/newsroom/2024/10/ey-reports-global-revenue-of-51-point-2-billion-us-dollars-for-fiscal-year-2024",
    "PwC Transparency Report 2024": "https://www.pwc.com/gx/en/about/transparency-report/2024/financials.html",
    "PwC UK Financial Statements": "https://www.pwc.co.uk/annualreport/assets/2024/pwc-uk-financial-statements-2024.pdf",
    "Global FinTech Report (GFTN)": "https://gftn.co/hubfs/Global%20State%20of%20Fintech%202024/Global%20State%20of%20FinTech%20Report%202024%20Full%20-%20Publish.pdf",
    "F-Prime FinTech Index": "https://fintechindex.fprimecapital.com/wp-content/uploads/2024/02/F-Prime-Capital-2024-State-of-Fintech-Report.pdf",
    "BCG FinTech Growth Report": "https://www.bcg.com/publications/2024/global-fintech-prudence-profits-and-growth"
}

for title, url in reports.items():
    st.markdown(f"- [{title}]({url})")
st.subheader("🌍 Global Firms & FinTech Reports")

reports = {
    "KPMG IFRS Guide 2024": "https://assets.kpmg.com/content/dam/kpmgsites/xx/pdf/ifrg/2024/isg-2024-ifs.pdf",
    "KPMG Disclosures Brochure": "https://assets.kpmg.com/content/dam/kpmg/be/pdf/IFRS-Illustrative-disclosures-2024-EN-Brochure-LR.pdf",
    "EY Global Revenue Report 2024": "https://www.ey.com/en_gl/newsroom/2024/10/ey-reports-global-revenue-of-51-point-2-billion-us-dollars-for-fiscal-year-2024",
    "EY IFRS Disclosure Checklist": "https://www.ey.com/en_gl/technical/ifrs-technical-resources/international-gaap-disclosure-checklist-for-annual-financial-statements-september-2024",
    "PwC Transparency Report": "https://www.pwc.com/gx/en/about/transparency-report/2024/financials.html",
    "Stripe Annual Letter 2024": "https://stripe.com/annual-updates/2024",
    "Stripe Payment Volume Report": "https://stripe.com/newsroom/news/stripe-2024-update",
    "Revolut Financial Statements": "https://www.revolut.com/reports-and-results/",
    "PayPal FinTech Trends 2024": "https://www.paypal.com/us/brc/article/8-payment-technology-trends-2024"
}

for title, url in reports.items():
    st.markdown(f"### 📄 {title}")
    st.markdown(f"[🔗 View Full Report]({url})")
    st.markdown(f'<iframe src="{url}" width="100%" height="600px"></iframe>', unsafe_allow_html=True)
