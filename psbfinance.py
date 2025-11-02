import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="PSBFinance", layout="wide")
st.title("📊 PSBFinance — Your Personal Stock Browser")
st.markdown("**Created by Ira-DIVINE, Emelia-Nour, Vinay Rao Gajura**")

ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):").upper()

if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info

    st.subheader(f"{info.get('longName', 'Unknown')} ({ticker})")
    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
    st.write(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
    st.write(info.get('longBusinessSummary', 'No summary available.'))

    st.subheader("📈 Stock Price Chart")
    df = stock.history(period='6mo')
    st.line_chart(df['Close'])

    st.subheader("📥 Download Financial Statements")
    st.download_button("Download Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
    st.download_button("Download Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
    st.download_button("Download Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")

    st.subheader("📊 CAPM Calculator")
    rf = st.number_input("Risk-Free Rate (%)", value=2.0)
    beta = st.number_input("Beta", value=1.0)
    rm = st.number_input("Market Return (%)", value=8.0)
    capm_return = rf + beta * (rm - rf)
    st.write(f"**Expected Return (CAPM):** {capm_return:.2f}%")

    st.subheader("📊 Key Financial Ratios")
    try:
        pe_ratio = info['forwardPE']
        roe = info['returnOnEquity']
        current_ratio = info['currentRatio']
        debt_equity = info['debtToEquity']

        st.write(f"**PE Ratio:** {pe_ratio:.2f} — {'High' if pe_ratio > 25 else 'Low' if pe_ratio < 10 else 'Moderate'}")
        st.write(f"**Return on Equity (ROE):** {roe:.2%} — {'Strong' if roe > 0.15 else 'Weak'}")
        st.write(f"**Current Ratio:** {current_ratio:.2f} — {'Healthy' if current_ratio > 1.5 else 'Risky'}")
        st.write(f"**Debt-to-Equity:** {debt_equity:.2f} — {'High leverage' if debt_equity > 2 else 'Low leverage'}")
    except KeyError:
        st.warning("Some financial ratios are not available for this company.")

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
            if value is not None:
                st.write(f"**{label}:** {value:,}")
            else:
                st.write(f"**{label}:** Data not available")
    except Exception as e:
        st.error("Unable to load full financial metrics.")

# 🔹 Fintech Explorer (outside ticker block)
st.subheader("🚀 Fintech Explorer")
company = st.selectbox("Choose a fintech", ["Qonto", "Lydia", "Swile", "Alan", "Ledger", "Revolut"])

if company == "Qonto":
    st.write("Qonto is a French neobank founded in 2016. It raised over €486M and serves SMEs and freelancers across Europe. Last updated: 2024.")
elif company == "Lydia":
    st.write("Lydia is a mobile payment app launched in France in 2013. It has over 5 million users and raised €235M. Last updated: 2024.")
elif company == "Swile":
    st.write("Swile offers employee benefits and smart cards. Founded in 2018, it raised €200M and serves companies across France. Last updated: 2024.")
elif company == "Alan":
    st.write("Alan is a digital health insurance startup founded in 2016. It raised €390M and covers over 500,000 members. Last updated: 2024.")
elif company == "Ledger":
    st.write("Ledger is a crypto hardware wallet company founded in 2014. It raised over €450M and serves millions of users globally. Last updated: 2024.")
elif company == "Revolut":
    st.write("Revolut is a UK-based fintech with strong presence in France. It has over 30M users globally and offers banking, crypto, and investment services. Last updated: 2024.")
if ticker == "AMA":
    st.subheader("📊 AMA ETF Key Stats")
    st.write("**Expense Ratio:** 1.29%")
    st.write("**Strategy:** 2x daily leveraged long exposure to AMAT")
    st.write("**Asset Class:** Equity")
    st.write("**Issuer:** Defiance ETFs")
    st.write("**Last NAV:** $20.00 (as of Sep 2025)")
statement_type = st.selectbox("Choose statement type", ["Balance Sheet", "Income Statement", "Cash Flow"])
year = st.selectbox("Choose year", ["2023", "2022", "2021"])

# Then load from a local CSV or external source
st.write(f"Showing {statement_type} for {ticker} in {year}")
if not info.get("marketCap"):
    st.warning("This ETF may not publish full financial statements like traditional companies. For key stats, check issuer websites or SEC filings.")
st.subheader("🚀 Fintech Explorer")

company = st.selectbox("Choose a fintech", ["Qonto", "Lydia", "Swile", "Alan", "Ledger", "Revolut"])

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
    """)

elif company == "Revolut":
    st.markdown("""
    **Revolut** is a UK-based fintech with strong presence in France, founded in 2015 by Nikolay Storonsky & Vlad Yatsenko.
    - 💰 **Funding:** $1.99B (Visa, Index Ventures)
    - 🦄 **Valuation:** $75B (2025)
    - 💵 **Revenue:** $4.1B (2024)
    - 🏦 **Profit:** $1.1B net profit (2024)
    - 👥 **Users:** 52.5M globally
    - 📍 **HQ:** London & Paris
    - 📰 **News:** Secured UK banking license, expanded product suite""")
    # ✅ Everything inside this block runs only when a ticker is entered
if ticker:
    stock = yf.Ticker(ticker)
    info = stock.info

    # Company Info
    ...

    # Stock Chart
    ...

    # Download Buttons
    ...

    # CAPM Calculator
    ...

    # Key Ratios
    ...

    # Full Financial Metrics
    ...

    # ✅ AMA ETF block (inside ticker block)
    if ticker == "AMA":
        st.subheader("📊 AMA ETF Key Stats")
        st.write("**Expense Ratio:** 1.29%")
        st.write("**Strategy:** 2x daily leveraged long exposure to AMAT")
        st.write("**Asset Class:** Equity")
        st.write("**Issuer:** Defiance ETFs")
        st.write("**Last NAV:** $20.00 (as of Sep 2025)")

    # ✅ Statement Type & Year dropdowns
    statement_type = st.selectbox("Choose statement type", ["Balance Sheet", "Income Statement", "Cash Flow"])
    year = st.selectbox("Choose year", ["2023", "2022", "2021"])
    st.write(f"Showing {statement_type} for {ticker} in {year}")

    if not info.get("marketCap"):
        st.warning("This ETF may not publish full financial statements like traditional companies. For key stats, check issuer websites or SEC filings.")

# ✅ Fintech Explorer (outside ticker block — keep only this version)
st.subheader("🚀 Fintech Explorer")
company = st.selectbox("Choose a fintech", ["Qonto", "Lydia", "Swile", "Alan", "Ledger", "Revolut"])

# Full markdown profiles (keep this version only)
if company == "Qonto":
    st.markdown("""...""")
elif company == "Lydia":
    st.markdown("""...""")
# etc.


