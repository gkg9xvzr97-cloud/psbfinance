import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="PSBFinance", layout="wide")
st.title("📊 PSBFinance — Your Personal Stock Browser")
st.markdown("**Created by Ira-DIVINE, Emelia-Nour, Vinay Rao Gajura**")

# 🔹 Ticker input
tickers = st.text_input("Enter one or more stock tickers (e.g., AAPL, TSLA, MSFT):", key="ticker_input").upper()
symbols = [t.strip() for t in tickers.split(",") if t.strip()]

# 🔍 Loop through each ticker
for ticker in symbols:
    stock = yf.Ticker(ticker)
    info = stock.info
    df = stock.history(period='6mo')

    st.header(f"📈 {info.get('longName', 'Unknown')} ({ticker})")
    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
    st.write(f"**Website:** [{info.get('website', 'N/A')}]({info.get('website', '#')})")
    st.write(info.get('longBusinessSummary', 'No summary available.'))

    # 🔹 Price chart
    st.subheader("📉 Stock Price (6 months)")
    st.line_chart(df['Close'])

    # 🔹 Download statements
    st.subheader("📥 Download Financial Statements")
    st.download_button("Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
    st.download_button("Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
    st.download_button("Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")

    # 🔹 Export to Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        stock.balance_sheet.to_excel(writer, sheet_name='Balance Sheet')
        stock.income_stmt.to_excel(writer, sheet_name='Income Statement')
        stock.cashflow.to_excel(writer, sheet_name='Cash Flow')
    st.download_button("📤 Export All to Excel", buffer.getvalue(), f"{ticker}_financials.xlsx")

    # 🔹 CAPM Calculator
    st.subheader("📊 CAPM Calculator")
    rf = st.number_input("Risk-Free Rate (%)", value=2.0)
    beta = st.number_input("Beta", value=info.get("beta", 1.0))
    rm = st.number_input("Market Return (%)", value=8.0)
    capm_return = rf + beta * (rm - rf)
    st.write(f"**Expected Return (CAPM):** {capm_return:.2f}%")

    # 🔹 Key Ratios
    st.subheader("📊 Key Financial Ratios")
    ratios = {
        "PE Ratio": info.get("forwardPE"),
        "ROE": info.get("returnOnEquity"),
        "Current Ratio": info.get("currentRatio"),
        "Debt-to-Equity": info.get("debtToEquity")
    }
    for label, value in ratios.items():
        st.write(f"**{label}:** {value:.2f}" if value else f"**{label}:** N/A")

    # 🔹 Ratio Chart
    st.subheader("📊 Ratio Chart")
    df_ratios = pd.DataFrame.from_dict(ratios, orient='index', columns=['Value']).dropna()
    st.bar_chart(df_ratios)

    # 🔹 Full Metrics
    st.subheader("📊 Full Financial Metrics")
    metrics = {
        "Market Cap": info.get("marketCap"),
        "Enterprise Value": info.get("enterpriseValue"),
        "EBITDA": info.get("ebitda"),
        "EPS (TTM)": info.get("trailingEps"),
        "EPS (Forward)": info.get("forwardEps"),
        "PEG Ratio": info.get("pegRatio"),
        "Dividend Yield": info.get("dividendYield"),
        "Revenue Growth": info.get("revenueGrowth"),
        "Profit Margins": info.get("profitMargins"),
        "ROA": info.get("returnOnAssets"),
        "Quick Ratio": info.get("quickRatio"),
        "Free Cash Flow": info.get("freeCashflow"),
        "Operating Cash Flow": info.get("operatingCashflow"),
        "Book Value per Share": info.get("bookValue"),
        "Price-to-Book": info.get("priceToBook"),
        "Price-to-Sales": info.get("priceToSalesTrailing12Months")
    }
    for label, value in metrics.items():
        st.write(f"**{label}:** {value:,}" if value else f"**{label}:** N/A")

# 🚀 Fintech Explorer
st.subheader("🚀 Fintech Explorer")
company = st.selectbox("Choose a fintech", ["Qonto", "Lydia", "Swile", "Alan", "Ledger", "Revolut"], key="fintech_select")

if company == "Qonto":
    st.markdown("""
    **Qonto** — French neobank founded in 2017  
    - 💰 $717M raised  
    - 📈 $5B valuation  
    - 🧾 €448.7M revenue (2024)  
    - 🏦 €144M net profit  
    - 👥 600,000+ customers  
    - 🛠️ Business accounts, invoicing, expense tracking  
    - 📍 Paris, France  
    """)

elif company == "Lydia":
    st.markdown("""
    **Lydia** — Mobile payments app launched in 2013  
    - 💰 $260M raised  
    - 🦄 $1B valuation  
    - 👥 5.5M+ users  
    - 🛠️ QR payments, shared accounts, crypto  
    - 📍 Paris, France  
    """)

elif company == "Swile":
    st.markdown("""
    **Swile** — Employee benefits platform  
    - 💰 $328M raised  
    - 🦄 $1B valuation  
    - 💵 $190.1M revenue  
    - 👥 ~637 employees  
    - 🛠️ Swile Card, HR tools, gamified surveys  
    - 📍 Montpellier, France  
    """)

elif company == "Alan":
    st.markdown("""
    **Alan** — Digital health insurance  
    - 💰 $747M raised  
    - 🦄 $4.5B valuation  
    - 👥 ~600 employees  
    - 🛠️ Insurance, telehealth, reimbursements  
    - 📍 Paris, France  
    """)

elif company == "Ledger":
    st.markdown("""
    **Ledger** — Crypto hardware wallets  
    - 💰 $575M raised  
    - 🦄 $1.3B valuation  
    - 💵 $133.2M revenue  
    - 🛠️ Ledger Nano X, Ledger Live  
    - 📍 Paris & Vierzon  
    """)

elif company == "Revolut":
    st.markdown("""
    **Revolut** — UK fintech with strong French presence  
    - 💰 $1.99B raised  
    - 🦄 $75B valuation  
    - 💵 $4.1B revenue  
    - 🏦 $1.1B net profit  
    - 👥 52.5M users  
    - 📍 London & Paris  
    """)
    import statsmodels.api as sm
import pandas_datareader.data as web
from datetime import datetime

st.subheader("📈 Fama-French 3-Factor Model")

selected_ticker = st.text_input("Choose one ticker for Fama-French analysis:", key="ff_ticker").upper()
start_date = st.date_input("Start Date", datetime(2020, 1, 1))
end_date = st.date_input("End Date", datetime(2023, 12, 31))

if selected_ticker:
    ff_factors = web.DataReader('F-F_Research_Data_Factors', 'famafrench', start_date, end_date)[0]
    ff_factors = ff_factors / 100  # Convert percentages to decimals

    stock_data = yf.download(selected_ticker, start=start_date, end=end_date)['Adj Close']
    stock_returns = stock_data.pct_change().dropna()
    ff_factors = ff_factors.loc[stock_returns.index]

    excess_returns = stock_returns - ff_factors['RF']
    X = ff_factors[['Mkt-RF', 'SMB', 'HML']]
    X = sm.add_constant(X)

    model = sm.OLS(excess_returns, X).fit()
    st.write(model.summary())
    st.subheader("📊 Sharpe Ratio")

returns = df['Close'].pct_change().dropna()
risk_free_rate = rf / 100 / 252  # Daily risk-free rate
excess_returns = returns - risk_free_rate
sharpe_ratio = excess_returns.mean() / excess_returns.std()

st.write(f"**Sharpe Ratio:** {sharpe_ratio:.2f}")
st.subheader("📈 Alpha vs. Market")

market = yf.download("^GSPC", start=df.index[0], end=df.index[-1])['Adj Close'].pct_change().dropna()
stock = df['Close'].pct_change().dropna()
aligned = pd.concat([stock, market], axis=1).dropna()
aligned.columns = ['Stock', 'Market']

X = sm.add_constant(aligned['Market'])
model = sm.OLS(aligned['Stock'], X).fit()
alpha = model.params['const']

st.write(f"**Alpha:** {alpha:.4f}")
st.subheader("📉 Volatility")

volatility = returns.std() * (252 ** 0.5)  # Annualized
st.write(f"**Annualized Volatility:** {volatility:.2%}")
st.subheader("📊 Moving Averages")

df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()

st.line_chart(df[['Close', 'MA20', 'MA50']])
st.subheader("📊 Sharpe Ratio")

returns = df['Close'].pct_change().dropna()
risk_free_daily = rf / 100 / 252
excess_returns = returns - risk_free_daily
sharpe_ratio = excess_returns.mean() / excess_returns.std()

st.write(f"**Sharpe Ratio:** {sharpe_ratio:.2f}")
st.subheader("📈 Alpha vs. Market (S&P 500)")

market_data = yf.download("^GSPC", start=df.index[0], end=df.index[-1])['Adj Close'].pct_change().dropna()
stock_returns = df['Close'].pct_change().dropna()
aligned = pd.concat([stock_returns, market_data], axis=1).dropna()
aligned.columns = ['Stock', 'Market']

X = sm.add_constant(aligned['Market'])
model = sm.OLS(aligned['Stock'], X).fit()
alpha = model.params['const']

st.write(f"**Alpha:** {alpha:.4f}")
st.subheader("📉 Annualized Volatility")

volatility = returns.std() * (252 ** 0.5)
st.write(f"**Volatility:** {volatility:.2%}")
st.subheader("📊 Moving Averages")

df['MA20'] = df['Close'].rolling(window=20).mean()
df['MA50'] = df['Close'].rolling(window=50).mean()

st.line_chart(df[['Close', 'MA20', 'MA50']])


    

