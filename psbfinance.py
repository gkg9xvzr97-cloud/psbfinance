import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

# =======================================================
# PAGE CONFIG
# =======================================================
st.set_page_config(
    page_title="FinSight Terminal",
    page_icon="💹",
    layout="wide",
)

# =======================================================
# STYLE (Bloomberg-like)
# =======================================================
st.markdown("""
<style>
body, .stApp {
    background-color: #111217;
    color: white;
}
section[data-testid="stSidebar"] {
    background-color: #050608;
}
.metric-card {
    background: #191b22;
    padding: 1rem;
    border-radius: 0.5rem;
    border: 1px solid #333;
}
.accent { color: #F3BA2F; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# =======================================================
# SAFE HELPERS
# =======================================================
def safe_float(value):
    try: return float(value)
    except: return None

def safe_percent(x):
    if x is None: return "–"
    try: return f"{x * 100:.2f}%"
    except: return "–"

def fmt_big(x):
    if x is None: return "–"
    try: x = float(x)
    except: return "–"
    if abs(x) >= 1e12: return f"{x/1e12:.2f}T"
    if abs(x) >= 1e9:  return f"{x/1e9:.2f}B"
    if abs(x) >= 1e6:  return f"{x/1e6:.2f}M"
    if abs(x) >= 1e3:  return f"{x/1e3:.2f}K"
    return f"{x:.2f}"

# =======================================================
# SIDEBAR
# =======================================================
with st.sidebar:
    st.title("💹 FinSight Terminal")

    ticker = st.text_input("Main Ticker", "AAPL").upper()

    default_end = date.today()
    default_start = default_end - timedelta(days=365)
    start_date, end_date = st.date_input("Date Range", [default_start, default_end])

    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])

# =======================================================
# LOAD TICKER (NO CACHING)
# =======================================================
try:
    stock = yf.Ticker(ticker)
    info = stock.info
except Exception:
    st.error("Invalid ticker symbol or data unavailable.")
    st.stop()

# =======================================================
# LOAD PRICE DATA SAFELY
# =======================================================
try:
    price = yf.download(ticker, start=start_date, end=end_date,
                        interval=interval, progress=False)
except:
    price = pd.DataFrame()

if price.empty:
    st.error("❌ No price data available for this ticker.")
    st.stop()

# Extract price values safely
last_close = safe_float(price["Close"].iloc[-1]) if "Close" in price else None
prev_close = safe_float(price["Close"].iloc[-2]) if "Close" in price and len(price) > 1 else None

if last_close is None or prev_close is None:
    change = None
    change_pct = None
else:
    change = last_close - prev_close
    change_pct = (change / prev_close * 100) if prev_close != 0 else None

# =======================================================
# HEADER
# =======================================================
name = info.get("longName", ticker)
sector = info.get("sector", "–")
industry = info.get("industry", "–")

st.markdown(f"## <span class='accent'>{name}</span> ({ticker})", unsafe_allow_html=True)
st.caption(f"{sector} — {industry}")

if last_close is None:
    st.write("Latest price unavailable.")
else:
    arrow = "🟢" if (change is not None and change >= 0) else "🔻"
    change_val = f"{change:.2f}" if change is not None else "–"
    change_p = f"{change_pct:.2f}%" if change_pct is not None else "–"
    st.write(f"**{last_close:.2f} USD** ({arrow} {change_val}, {change_p})")

st.divider()

# =======================================================
# TABS
# =======================================================
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📊 Financials", "📐 Ratios", "📰 News"])

# =======================================================
# TAB 1: SAFE PRICE CHART (UNBREAKABLE)
# =======================================================
with tab1:
    st.subheader("Price Chart")

    # Safely convert price data
    try:
        df = price.reset_index()
    except:
        df = pd.DataFrame()

    # Check required columns
    if "Date" not in df.columns or "Close" not in df.columns:
        st.warning("⚠️ Price data missing required columns to draw chart.")
        st.write(df.head())
    else:
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["Close"])

        if df.empty:
            st.warning("⚠️ No valid price data available for chart.")
        else:
            try:
                fig = px.area(df, x="Date", y="Close",
                              title=f"{ticker} Price Chart")
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error("❌ Plot could not be generated.")
                st.write("Error:", str(e))

# =======================================================
# TAB 2: FINANCIAL STATEMENTS
# =======================================================
with tab2:
    st.subheader("Financial Statements")

    fin = stock.financials if isinstance(stock.financials, pd.DataFrame) else pd.DataFrame()
    bs  = stock.balance_sheet if isinstance(stock.balance_sheet, pd.DataFrame) else pd.DataFrame()
    cf  = stock.cashflow if isinstance(stock.cashflow, pd.DataFrame) else pd.DataFrame()
    earn = stock.earnings if isinstance(stock.earnings, pd.DataFrame) else pd.DataFrame()

    choice = st.radio("Choose Statement",
                      ["Income", "Balance Sheet", "Cash Flow", "Earnings"],
                      horizontal=True)

    if choice == "Income":
        st.dataframe(fin)
    elif choice == "Balance Sheet":
        st.dataframe(bs)
    elif choice == "Cash Flow":
        st.dataframe(cf)
    else:
        st.dataframe(earn)

# =======================================================
# TAB 3: RATIOS
# =======================================================
with tab3:
    st.subheader("Key Ratios")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Market Cap:**", fmt_big(info.get("marketCap")))
        st.write("**P/E:**", info.get("trailingPE", "–"))
        st.write("**Forward P/E:**", info.get("forwardPE", "–"))

    with col2:
        st.write("**Dividend Yield:**", safe_percent(info.get("dividendYield")))
        st.write("**Profit Margin:**", safe_percent(info.get("profitMargins")))
        st.write("**Operating Margin:**", safe_percent(info.get("operatingMargins")))

    with col3:
        st.write("**ROE:**", safe_percent(info.get("returnOnEquity")))
        st.write("**ROA:**", safe_percent(info.get("returnOnAssets")))

# =======================================================
# TAB 4: NEWS
# =======================================================
with tab4:
    st.subheader("Latest News")

    try:
        news = stock.news
    except:
        news = []

    if not news:
        st.info("No news available for this ticker.")
    else:
        for item in news[:10]:
            st.write(f"### [{item.get('title')}]({item.get('link')})")
            st.caption(item.get("publisher"))
            st.write("---")

