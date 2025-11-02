import streamlit as st
import yfinance as yf
import pandas as pd

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Title and credits
st.title("📊 PSBFinance — Your Personal Stock Browser")
st.markdown("**Created by Ira-DIVINE, Emelia-Nour, Vinay Rao Gajura**")

# Ticker input
ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):", key="ticker_input").upper()

# Stock block
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
# 📥 Download Financial Statements
st.subheader("📥 Download Financial Statements")

try:
    st.download_button(
        label="Download Balance Sheet",
        data=stock.balance_sheet.to_csv().encode(),
        file_name=f"{ticker}_balance_sheet.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Download Income Statement",
        data=stock.income_stmt.to_csv().encode(),
        file_name=f"{ticker}_income_statement.csv",
        mime="text/csv"
    )
    st.download_button(
        label="Download Cash Flow",
        data=stock.cashflow.to_csv().encode(),
        file_name=f"{ticker}_cash_flow.csv",
        mime="text/csv"
    )
except Exception:
    st.warning("Financial statements are not available for this ticker.")
# 📊 CAPM Calculator
st.subheader("📊 CAPM Calculator")

rf = st.number_input("Risk-Free Rate (%)", value=2.0)
beta = st.number_input("Beta", value=info.get("beta", 1.0))
rm = st.number_input("Market Return (%)", value=8.0)

capm_return = rf + beta * (rm - rf)
st.write(f"**Expected Return (CAPM):** {capm_return:.2f}%")
# 📊 Key Financial Ratios
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
# 📊 Full Financial Metrics
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
        st.write(f"**{label}:** {value:,}" if value is not None else f"**{label}:** Data not available")
except Exception:
    st.error("Unable to load full financial metrics.")
# 🚀 Fintech Explorer
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
    - 📰 **News:** Secured UK banking license, expanded product suite
    """)
    # 📁 Statement Type & Year Selector
st.subheader("📁 View Financial Statement by Year")

statement_type = st.selectbox("Choose statement type", ["Balance Sheet", "Income Statement", "Cash Flow"], key="statement_type")
year = st.selectbox("Choose year", ["2023", "2022", "2021"], key="statement_year")

st.write(f"Showing **{statement_type}** for **{ticker}** in **{year}**")

# Placeholder for future logic (e.g., loading from CSV or API)
st.info("This feature is under development. In the future, you'll be able to view historical statements by year.")
# 🛡️ AMA ETF Fallback Block
if ticker == "AMA":
    st.subheader("📊 AMA ETF Key Stats")
    st.write("**Expense Ratio:** 1.29%")
    st.write("**Strategy:** 2x daily leveraged long exposure to AMAT")
    st.write("**Asset Class:** Equity")
    st.write("**Issuer:** Defiance ETFs")
    st.write("**Last NAV:** $20.00 (as of Sep 2025)")
    st.warning("This ETF may not publish full financial statements like traditional companies. For key stats, check issuer websites or SEC filings.")
import io

buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Financials')
    writer.save()

st.download_button(
    label="Export to Excel",
    data=buffer.getvalue(),
    file_name=f"{ticker}_financials.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
tickers = st.text_input("Enter multiple tickers separated by commas (e.g., AAPL, MSFT, TSLA):", key="multi_tickers")
if tickers:
    symbols = [t.strip().upper() for t in tickers.split(",")]
    for symbol in symbols:
        stock = yf.Ticker(symbol)
        info = stock.info
        st.subheader(f"{info.get('longName', 'Unknown')} ({symbol})")
        st.write(f"**Market Cap:** {info.get('marketCap', 'N/A')}")
        st.write(f"**PE Ratio:** {info.get('forwardPE', 'N/A')}")
import matplotlib.pyplot as plt

ratios = {
    "PE Ratio": info.get("forwardPE"),
    "ROE": info.get("returnOnEquity"),
    "Current Ratio": info.get("currentRatio"),
    "Debt-to-Equity": info.get("debtToEquity")
}
df_ratios = pd.DataFrame.from_dict(ratios, orient='index', columns=['Value'])

st.subheader("📊 Financial Ratios Chart")
st.bar_chart(df_ratios)
import statsmodels.api as sm
import pandas_datareader.data as web
from datetime import datetime

start = st.date_input("Start Date", datetime(2015, 1, 1))
end = st.date_input("End Date", datetime(2023, 12, 31))

ff_factors = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start, end)[0]
stock_returns = yf.download(ticker, start=start, end=end)['Adj Close'].pct_change().dropna()
excess_returns = stock_returns - ff_factors['RF']

X = ff_factors[['Mkt-RF', 'SMB', 'HML']]
X = sm.add_constant(X)
model = sm.OLS(excess_returns, X).fit()

st.subheader("📈 Fama-French Model Results")
st.write(model.summary())





