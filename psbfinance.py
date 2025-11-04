import streamlit as st

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge"])

# Section 1: About Us
if section == "About Us":
    st.title("🧠 Welcome to PSBFinance")
    st.image("https://raw.githubusercontent.com/gkyash97-st-cloud/psbfinance/main/capilotimage.png", use_column_width=True)
    st.markdown("""
    ### Built by students for students.

    PSBFinance is a learning dashboard designed to make finance accessible, visual, and practical.

    **Team Members:**  
    - Amelie-Nour  
    - Sai Vinay  
    - N. Pooja  
    - Ira.Divine (Founder & Architect — mentioned here only)
    """)

# Section 2: General Knowledge
if section == "General Knowledge":
    st.header("📚 General Finance Knowledge")

    st.markdown("""
    This section provides a practical overview of key financial concepts, contracts, strategies, and models — designed to help you understand how modern finance works.

    ### 🔹 Derivatives & Markets
    - Derivatives derive value from assets like stocks, bonds, currencies, or commodities.
    - Common types include forwards, futures, options, and swaps.
    - Markets are either exchange-traded (standardized) or over-the-counter (customized).

    ### 🔹 Hedging with Futures
    - Futures contracts help manage risk for buyers and sellers.
    - Hedging strategies use optimal ratios to reduce exposure to price changes.
    - Equity portfolios can be hedged using index futures.

    ### 🔹 Interest Rates & Pricing
    - Spot rates discount future cashflows; yield curves show rates over time.
    - Duration and convexity measure bond sensitivity to interest rate changes.
    - Forward prices reflect cost of carry, income, and rate differentials.

    ### 🔹 Swaps & Securitization
    - Swaps exchange fixed and floating payments or currencies.
    - Securitization pools loans into tradable securities.
    - Valuation adjustments account for credit, funding, and margin risks.

    ### 🔹 Options & Strategies
    - Options give rights to buy/sell assets at set prices.
    - Strategies include spreads, straddles, and protective puts.
    - Pricing uses binomial trees and Black-Scholes models.

    ### 🔹 Risk & Volatility
    - Value at Risk and Expected Shortfall measure downside risk.
    - Volatility models include EWMA and GARCH.
    - Greeks (delta, gamma, theta, etc.) track option sensitivities.

    ### 🔹 Credit & Exotic Derivatives
    - Credit derivatives transfer default risk.
    - Exotic options include barriers, lookbacks, and Asian options.
    - Interest rate derivatives include caps, floors, and swaptions.

    ### 🔹 Commodities & Real Options
    - Commodity derivatives reflect storage costs and seasonal patterns.
    - Real options value strategic flexibility in business decisions.
    - Case studies highlight lessons from financial mishaps.

    ---
    This summary is designed to help you grasp the core mechanics of modern financial instruments and risk management — fast, clean, and practical.
    """)
    if section == "Finance News":
    st.header("📰 Latest Finance News")

    st.markdown("""
    Stay updated with the latest headlines from the world of finance, markets, and economics.

    This section will soon include live news feeds, curated summaries, and trending topics.
    """)

import yfinance as yf  # Make sure this is at the top of your file

if section == "Global Financials":
    st.header("🌍 Global Financial Dashboard")

    st.markdown("Explore global financial data including stock prices, currency exchange rates, and economic indicators.")

    ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):")
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News"])

    if ticker:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            price = data["Close"].iloc[-1]
            st.success(f"📈 Current price of {ticker.upper()}: ${price:.2f}")
        except Exception as e:
            st.error("⚠️ Could not retrieve stock data. Please check the ticker symbol.")
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

