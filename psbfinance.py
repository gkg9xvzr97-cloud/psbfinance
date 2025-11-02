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

# ✅ Ticker input
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):").upper()

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
