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
