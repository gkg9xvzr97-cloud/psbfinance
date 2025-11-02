import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="PSBFinance", layout="wide")
st.title("📊 PSBFinance — Your Personal Stock Browser")
st.markdown("**Created by Ira-DIVINE, Emelia-Nour, Vinay Rao Gajura**")

# ✅ Ticker input
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):", key="main_ticker").upper()

# ✅ Stock analysis block
if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info

    # Company Info
    st.subheader(f"{info.get('longName', 'Unknown')} ({ticker})")
    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
    st.write(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
    st.write(info.get('longBusinessSummary', 'No summary available.'))

    # Stock Chart
    df = stock.history(period='6mo')
    st.subheader("📈 Stock Price Chart")
    st.line_chart(df['Close'])

    # Download Buttons
    st.subheader("📥 Download Financial Statements")
    st.download_button("Download Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
    st.download_button("Download Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
    st.download_button("Download Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")

    # CAPM Calculator
    st.subheader("📊 CAPM Calculator")
    rf = st.number_input("Risk-Free Rate (%)", value=2.0)
    beta = st.number_input("Beta", value=1.0)
    rm = st.number_input("Market Return (%)", value=8.0)
    capm_return = rf + beta * (rm - rf)
    st.write(f"**Expected Return (CAPM):** {capm_return:.2f}%")

    # Key Ratios
    st.subheader("📊 Key Financial Ratios")
    try:
        pe_ratio = info['forwardPE']
        roe = info['returnOnEquity']
        current_ratio = info['currentRatio']
        debt_equity = info['debtToEquity']
        st.write(f"**PE Ratio:** {pe_ratio:.2f}")
        st.write(f"**ROE:** {roe:.2%}")
        st.write(f"**Current Ratio:** {current_ratio:.2f}")
        st.write(f"**Debt-to-Equity:** {debt_equity:.2f}")
    except KeyError:
        st.warning("Some financial ratios are not available.")

    # Full Financial Metrics
    st.subheader("📊 Full Financial Metrics")
    try:
        metrics = {
            "Market Cap": info.get("marketCap"),
            "Enterprise Value": info.get("enterpriseValue"),
            "EBITDA": info.get("ebitda"),
            "EPS (TTM)": info.get("trailingEps"),
            "EPS (Forward)": info.get("forwardEps"),
            "PE Ratio (TTM)": info.get("trailingPE"),
            "PE Ratio (Forward)": info.get("forwardPE"),
            "PEG Ratio": info.get("pegRatio"),
            "Dividend Yield": info.get("dividendYield"),
            "Beta": info.get("beta"),
            "Revenue Growth": info.get("revenueGrowth"),
            "Profit Margins": info.get("profitMargins"),
            "ROE": info.get("returnOnEquity"),
            "ROA": info.get("returnOnAssets"),
            "Debt-to-Equity": info.get("debtToEquity"),
            "Current Ratio": info.get("currentRatio"),
            "Quick Ratio": info.get("quickRatio"),
            "Free Cash Flow": info.get("freeCashflow"),
            "Operating Cash Flow": info.get("operatingCashflow"),
            "Book Value per Share": info.get("bookValue"),
            "Price-to-Book": info.get("priceToBook"),
            "Price-to-Sales": info.get("priceToSalesTrailing12Months")
        }

        for label, value in metrics.items():
            st.write(f"**{label}:** {value:,}" if value else f"**{label}:** Data not available")
    except Exception:
        st.error("Unable to load full financial metrics.")

    # AMA ETF block
    if ticker == "AMA":
        st.subheader("📊 AMA ETF Key Stats")
        st.write("**Expense Ratio:** 1.29%")
        st.write("**Strategy:** 2x daily leveraged long exposure to AMAT")
        st.write("**Issuer:** Defiance ETFs")
        st.write("**Last NAV:** $20.00 (Sep 2025)")

    # Statement Type & Year
    statement_type = st.selectbox("Choose statement type", ["Balance Sheet", "Income Statement", "Cash Flow"], key="statement_type")
    year = st.selectbox("Choose year", ["2023", "2022", "2021"], key="statement_year")
    st.write(f"Showing {statement_type} for {ticker} in {year}")

    if not info.get("marketCap"):
        st.warning("This ETF may not publish full financial statements like traditional companies.")

# ✅ Fintech Explorer (outside ticker block)
st.subheader("🚀 Fintech Explorer")
company = st.selectbox("Choose a fintech", ["Qonto", "Lydia", "Swile", "Alan", "Ledger", "Revolut"], key="fintech_select")

if company == "Qonto":
    st.markdown("""
    **Qonto** is a French neobank founded in 2017 by Steve Anavi & Alexandre Prot.
    - 💰 **Funding:** $717M raised (Tiger Global, Valar Ventures)
    - 📈 **Valuation:** $5B (2025)
    - 🧾 **Revenue:** €448.7M in 2024 (+44% YoY)
    - 🏦 **Profit:** €144M net profit in 2024
    - 👥 **Customers:** 600,000+ across Europe
    - 🛠️ **Services:** Business accounts, invoicing, expense tracking
    - 📍 **HQ:** Paris, France
    - 📰 **News:** Filed for banking license, launched 4% interest account
    """)

elif company == "Lydia":
    st.markdown("""
    **Lydia** is a mobile payment app launched in 2013 by Cyril Chiche & Antoine Porte.
    - 💰 **Funding:** $260M (Tencent, Accel)
    - 🦄 **Valuation:** $1B (2021)
    - 👥 **Users:** 5.5M+ in France
    - 💵 **Revenue:** $100M+ (2023 est.)
    - 🛠️ **Services:** QR payments, shared accounts, crypto trading
    - 📍 **HQ:** Paris, France
    - 📰 **News:** Pivoted into a financial superapp
    """)

elif company == "Swile":
    st.markdown("""
    **Swile** offers employee benefits and smart cards, founded in 2016 by Loïc Soubeyrand.
    - 💰 **Funding:** $328M (Index Ventures, Idinvest)
    - 🦄 **Valuation:** $1B (2025)
    - 💵 **Revenue:** $190.1M (2024)
    - 👥 **Employees:** ~637
    - 🛠️ **Services:** Swile Card, HR integrations, gamified surveys
    - 📍 **HQ:** Montpellier, France
    - 📰 **News:** Integrated Bimpli, expanded benefits platform
    """)

elif company == "Alan":
    st.markdown("""
    **Alan** is a digital health insurance startup founded in 2016 by Jean-Charles Samuelian & Charles Gorintin.
    - 💰 **Funding:** $747M (Temasek, OTPP)
    - 🦄 **Valuation:** $4.5B (2024)
    - 👥 **Employees:** ~600
    - 🛠️ **Services:** Insurance, telehealth, reimbursements
    - 📍 **HQ:** Paris, France
    - 📰 **News:** Raised €173M Series F, partnered with Belfius Bank
    """)

elif company == "Ledger":
    st.markdown("""
    **Ledger** is a crypto hardware wallet company founded in 2014 by Thomas France & Nicolas Bacca.
    - 💰 **Funding:** $575M (Samsung, Morgan Creek)
    - 🦄 **Valuation:** $1.3B (2025)
    - 💵 **Revenue:** $133.2M (2024)
    - 🛠️ **Products:** Ledger Nano X, Ledger Live, Ledger Enterprise
    - 📍 **HQ:** Paris & Vierzon, France
    - 📰 **News:** Expanded enterprise offerings, launched new wallet models
    """
    # Stock Chart
    df = stock.history(period='6mo')
    st.subheader("📈 Stock Price Chart")
    st.line_chart(df['Close'])

    # Download Buttons
    st.subheader("📥 Download Financial Statements")
    st.download_button("Download Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
    st.download_button("Download Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
    st.download_button("Download Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")

    # CAPM Calculator
    st.subheader("📊 CAPM Calculator")
    rf = st.number_input("Risk-Free Rate (%)", value=2.0)
    beta = st.number_input("Beta", value=1.0)
    rm = st.number_input("Market Return (%)", value=8.0)
    capm_return = rf + beta * (rm - rf)
    st.write(f"**Expected Return (CAPM):** {capm_return:.2f}%")

    # Key Ratios
    st.subheader("📊 Key Financial Ratios")
    try:
        pe_ratio = info['forwardPE']
        roe = info['returnOnEquity']
        current_ratio = info['currentRatio']
        debt_equity = info['debtToEquity']
        st.write(f"**PE Ratio:** {pe_ratio:.2f}")
        st.write(f"**ROE:** {roe:.2%}")
        st.write(f"**Current Ratio:** {current_ratio:.2f}")
        st.write(f"**Debt-to-Equity:** {debt_equity:.2f}")
    except KeyError:
        st.warning("Some financial ratios are not available.")

    # Full Financial Metrics
    st.subheader("📊 Full Financial Metrics")
    try:
        metrics = {...}  # your full metrics dictionary
        for label, value in metrics.items():
            st.write(f"**{label}:** {value:,}" if value else f"**{label}:** Data not available")
    except Exception:
        st.error("Unable to load full financial metrics.")

    # AMA ETF block
    if ticker == "AMA":
        st.subheader("📊 AMA ETF Key Stats")
        st.write("**Expense Ratio:** 1.29%")
        st.write("**Strategy:** 2x daily leveraged long exposure to AMAT")
        st.write("**Issuer:** Defiance ETFs")
        st.write("**Last NAV:** $20.00 (Sep 2025)")

    # Statement Type & Year
    statement_type = st.selectbox("Choose statement type", ["Balance Sheet", "Income Statement", "Cash Flow"])
    year = st.selectbox("Choose year", ["2023", "2022", "2021"])
    st.write(f"Showing {statement_type} for {ticker} in {year}")

    if not info.get("marketCap"):
        st.warning("This ETF may not publish full financial statements like traditional companies.")

# ✅ Fintech Explorer (outside ticker block)
st.subheader("🚀 Fintech Explorer")
company = st.selectbox("Choose a fintech", ["Qonto", "Lydia", "Swile", "Alan", "Ledger", "Revolut"])

# ✅ Detailed markdown profiles (keep only this version)
if company == "Qonto":
    st.markdown("""...""")
elif company == "Lydia":
    st.markdown("""...""")
# etc.
