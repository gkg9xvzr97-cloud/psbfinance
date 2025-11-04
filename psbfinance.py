import streamlit as st

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
ssection = st.sidebar.radio("📂 Navigate", [
    "About Us", "General Knowledge", "Finance News", "Global Financials",
    "Finance Quiz", "Topic Explorer", "Document Analyzer", "Company Search", "SEC Filings"
])

])

st.markdown("---")


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
st.markdown("---")

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
    st.markdown("---")

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

    if ticker:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            price = data["Close"].iloc[-1]
            st.success(f"📈 Current price of {ticker.upper()}: ${price:.2f}")
        except Exception as e:
            st.error("⚠️ Could not retrieve stock data. Please check the ticker symbol.")
st.markdown("### 💱 Currency Exchange Rates")

base_currency = st.selectbox("Base currency", ["USD", "EUR", "GBP", "JPY", "AUD"])
target_currency = st.selectbox("Target currency", ["USD", "EUR", "GBP", "JPY", "AUD"])

if base_currency and target_currency and base_currency != target_currency:
    try:
        pair = f"{base_currency}{target_currency}=X"
        fx = yf.Ticker(pair)
        fx_data = fx.history(period="1d")
        fx_rate = fx_data["Close"].iloc[-1]
        st.success(f"💱 1 {base_currency} = {fx_rate:.4f} {target_currency}")
    except Exception as e:
        st.error("⚠️ Could not retrieve exchange rate. Please try again.")
st.markdown("### 📊 Stock Price Chart")

chart_ticker = st.text_input("Enter a ticker for chart (e.g., AAPL, TSLA, MSFT):")

if chart_ticker:
    try:
        chart_data = yf.Ticker(chart_ticker).history(period="6mo")
        st.line_chart(chart_data["Close"])
        st.caption(f"Showing closing prices for {chart_ticker.upper()} over the past 6 months.")
    except Exception as e:
        st.error("⚠️ Could not load chart. Please check the ticker.")
        st.markdown("---")

if section == "Finance Quiz":
    st.header("🎓 Finance Knowledge Quiz")


    st.markdown("Test your understanding of key finance concepts with this short quiz.")

    questions = [
        {
            "question": "What does a derivative derive its value from?",
            "options": ["Government policy", "Underlying asset", "Company revenue", "Market sentiment"],
            "answer": 1
        },
        {
            "question": "Which strategy protects a seller using futures?",
            "options": ["Long hedge", "Short hedge", "Put option", "Swap"],
            "answer": 1
        },
        {
            "question": "What does duration measure in bond pricing?",
            "options": ["Credit risk", "Liquidity", "Sensitivity to interest rates", "Inflation exposure"],
            "answer": 2
        },
        {
            "question": "Which model is used to price options?",
            "options": ["CAPM", "Black-Scholes", "Monte Carlo", "Binomial Tree"],
            "answer": 1
        },
        {
            "question": "What does VaR measure?",
            "options": ["Expected return", "Downside risk", "Volatility", "Liquidity"],
            "answer": 1
        }
    ]
st.markdown("---")

    for i, q in enumerate(questions):
        st.subheader(f"Q{i+1}: {q['question']}")
        selected = st.radio(f"Choose your answer:", q["options"], key=f"q{i}")
        if selected == q["options"][q["answer"]]:
            st.success("✅ Correct!")
        else:
            st.warning(f"❌ Incorrect. Correct answer: {q['options'][q['answer']]}")
if section == "Topic Explorer":
    st.header("🧠 Explore Finance by Topic")

    topic = st.selectbox("Choose a topic", [
        "Options & Strategies",
        "Risk & Volatility",
        "Credit & Derivatives",
        "Commodities & Real Options",
        "Interest Rates & Pricing",
        "Swaps & Securitization"
    ])

    if topic == "Options & Strategies":
        st.markdown("""
        ### 📘 Options & Strategies
        - Options give rights to buy/sell assets at set prices.
        - Strategies include spreads, straddles, and protective puts.
        - Pricing uses binomial trees and Black-Scholes models.
        """)

    elif topic == "Risk & Volatility":
        st.markdown("""
        ### 📘 Risk & Volatility
        - Value at Risk and Expected Shortfall measure downside risk.
        - Volatility models include EWMA and GARCH.
        - Greeks (delta, gamma, theta, etc.) track option sensitivities.
        """)

    elif topic == "Credit & Derivatives":
        st.markdown("""
        ### 📘 Credit & Derivatives
        - Credit derivatives transfer default risk.
        - CDS, synthetic CDOs, and TRS are key instruments.
        - Risk management includes collateral, netting, and exposure modeling.
        """)

    elif topic == "Commodities & Real Options":
        st.markdown("""
        ### 📘 Commodities & Real Options
        - Commodity derivatives reflect storage costs and seasonal patterns.
        - Real options value strategic flexibility in business decisions.
        - Used in energy, agriculture, and infrastructure planning.
        """)

    elif topic == "Interest Rates & Pricing":
        st.markdown("""
        ### 📘 Interest Rates & Pricing
        - Spot rates discount future cashflows; yield curves show rates over time.
        - Duration and convexity measure bond sensitivity to interest rate changes.
        - Forward prices reflect cost of carry, income, and rate differentials.
        """)

    elif topic == "Swaps & Securitization":
        st.markdown("""
        ### 📘 Swaps & Securitization
        - Swaps exchange fixed and floating payments or currencies.
        - Securitization pools loans into tradable securities.
        - Valuation adjustments account for credit, funding, and margin risks.
        """)
        st.markdown("---")

if section == "Document Analyzer":
    st.header("📁 Finance Document Analyzer")

    uploaded_file = st.file_uploader("Upload a finance-related document (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file:
        st.success(f"✅ Uploaded: {uploaded_file.name}")

        file_text = uploaded_file.read().decode("utf-8", errors="ignore")

        st.markdown("### 📄 Document Preview")
        st.text_area("Content", file_text[:3000], height=300)

        st.markdown("### 🧠 Summary")
        st.write("This document discusses key financial concepts including derivatives, pricing models, risk management, and market structures. It may include formulas, examples, and strategic insights relevant to students and professionals.")
st.markdown("""
---
© 2025 PSBFinance — Built by students for students.
""")
import pandas as pd
import yfinance as yf

if section == "Company Search":
    st.header("🏢 Company Search & Financials")

    query = st.text_input("Enter a company name or ticker (e.g., AAPL, MSFT, TSLA):")

    if query:
        try:
            ticker = yf.Ticker(query)
            info = ticker.info

            st.subheader(f"📊 {info.get('longName', query)} ({query.upper()})")
            st.markdown(f"**Sector:** {info.get('sector', 'N/A')}  \n**Industry:** {info.get('industry', 'N/A')}  \n**Market Cap:** {info.get('marketCap', 'N/A'):,}")

            st.markdown("### 🧾 Financial Statements")

            # Income Statement
            st.markdown("#### 📈 Income Statement")
            income = ticker.financials.T
            st.dataframe(income)
            st.download_button("Download Income Statement", income.to_csv().encode(), file_name="income_statement.csv")

            # Balance Sheet
            st.markdown("#### 🧾 Balance Sheet")
            balance = ticker.balance_sheet.T
            st.dataframe(balance)
            st.download_button("Download Balance Sheet", balance.to_csv().encode(), file_name="balance_sheet.csv")

            # Cash Flow
            st.markdown("#### 💵 Cash Flow Statement")
            cashflow = ticker.cashflow.T
            st.dataframe(cashflow)
            st.download_button("Download Cash Flow", cashflow.to_csv().encode(), file_name="cash_flow.csv")

        except Exception as e:
            st.error("⚠️ Could not retrieve company data. Please check the ticker or try again later.")
import requests
from bs4 import BeautifulSoup

if section == "SEC Filings":
    st.header("🧾 SEC Filings Viewer")

    sec_ticker = st.text_input("Enter a company ticker (e.g., AAPL, MSFT, TSLA):")

    if sec_ticker:
        st.markdown("Showing latest 10-K, 10-Q, and 8-K filings from the SEC EDGAR database.")

        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={sec_ticker}&type=&owner=exclude&count=10&action=getcompany"

        try:
            response = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.find_all("tr")

            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    form_type = cols[0].text.strip()
                    filing_date = cols[3].text.strip()
                    link_tag = cols[1].find("a")
                    if link_tag:
                        filing_link = "https://www.sec.gov" + link_tag["href"]
                        if form_type in ["10-K", "10-Q", "8-K"]:
                            st.markdown(f"**{form_type}** filed on {filing_date} — [View Filing]({filing_link})")
        except Exception as e:
            st.error("⚠️ Could not retrieve SEC filings. Please check the ticker or try again later.")
