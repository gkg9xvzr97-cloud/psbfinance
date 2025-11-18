import streamlit as st
import yfinance as yf
import pandas as pd
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
# HELPERS
# =======================================================
def safe_float(value):
    try:
        return float(value)
    except Exception:
        return None


def safe_percent(x):
    if x is None:
        return "–"
    try:
        return f"{x * 100:.2f}%"
    except Exception:
        return "–"


def fmt_big(x):
    if x is None:
        return "–"
    try:
        x = float(x)
    except Exception:
        return "–"
    if abs(x) >= 1e12:
        return f"{x/1e12:.2f}T"
    if abs(x) >= 1e9:
        return f"{x/1e9:.2f}B"
    if abs(x) >= 1e6:
        return f"{x/1e6:.2f}M"
    if abs(x) >= 1e3:
        return f"{x/1e3:.2f}K"
    return f"{x:.2f}"


# =======================================================
# SIDEBAR
# =======================================================
with st.sidebar:
    st.title("💹 FinSight Terminal")

    ticker = st.text_input("Main Ticker", "AAPL").upper().strip()

    today = date.today()
    default_end = today
    default_start = today - timedelta(days=365)

    # date_input returns a list of 2 dates
    start_end = st.date_input("Date Range", [default_start, default_end])
    if isinstance(start_end, list) and len(start_end) == 2:
        start_date, end_date = start_end
    else:
        start_date, end_date = default_start, default_end

    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"])


# =======================================================
# LOAD TICKER
# =======================================================
if not ticker:
    st.error("Please enter a ticker symbol in the sidebar.")
    st.stop()

try:
    stock = yf.Ticker(ticker)
    info = getattr(stock, "info", {}) or {}
except Exception:
    st.error("Invalid ticker symbol or data unavailable.")
    st.stop()

# =======================================================
# LOAD PRICE DATA
# =======================================================
try:
    price = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        interval=interval,
        progress=False,
    )
except Exception:
    price = pd.DataFrame()

if price is None or price.empty:
    st.error("❌ No price data available for this ticker and date range.")
    st.stop()

# =======================================================
# LATEST PRICE (SAFE)
# =======================================================
if "Close" in price.columns:
    try:
        # For normal columns, this is a Series; for MultiIndex, this is a DataFrame
        close_obj = price["Close"]
        if isinstance(close_obj, pd.DataFrame):
            close_series = close_obj.iloc[:, 0]
        else:
            close_series = close_obj

        last_close = safe_float(close_series.iloc[-1])
        prev_close = safe_float(close_series.iloc[-2]) if len(close_series) > 1 else None
    except Exception:
        last_close = None
        prev_close = None
else:
    last_close = None
    prev_close = None

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
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Overview", "📊 Financials", "📐 Ratios", "📰 News"]
)

# =======================================================
# TAB 1 – OVERVIEW (SAFE PRICE CHART)
# =======================================================
with tab1:
    st.subheader("Price Chart")

    # Reset index safely
    try:
        df = price.reset_index()
    except Exception:
        df = price.copy()
        df = df.reset_index()

    # Ensure Date column exists
    if "Date" not in df.columns:
        # Sometimes the index name might be something else like Datetime
        # If first column looks like dates, rename it
        if df.columns.size > 0:
            df = df.rename(columns={df.columns[0]: "Date"})

    if "Date" not in df.columns:
        st.warning("⚠️ Could not find a Date column to plot.")
        st.write(df.head())
    else:
        # Extract Close safely even if MultiIndex
        close_obj = None
        if "Close" in df.columns:
            close_obj = df["Close"]
        elif isinstance(df.columns, pd.MultiIndex):
            # try take level 0 named 'Close'
            try:
                close_obj = df.xs("Close", axis=1, level=0)
            except Exception:
                close_obj = None

        if close_obj is None:
            st.warning("⚠️ Close price column missing; cannot plot price chart.")
            st.write(df.head())
        else:
            # If DataFrame, take first column
            if isinstance(close_obj, pd.DataFrame):
                close_series = close_obj.iloc[:, 0]
            else:
                close_series = close_obj

            # Convert to numeric safely
            close_series = pd.to_numeric(close_series, errors="coerce")

            # Attach back to df
            df["Close"] = close_series

            # Drop NaNs
            df = df.dropna(subset=["Close"])

            if df.empty:
                st.warning("⚠️ Not enough valid Close price data to plot.")
            else:
                try:
                    fig = px.area(df, x="Date", y="Close", title=f"{ticker} Price Chart")
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error("❌ Could not render chart.")
                    st.write("Error:", str(e))

# =======================================================
# TAB 2 – FINANCIAL STATEMENTS
# =======================================================
with tab2:
    st.subheader("Financial Statements")

    fin = stock.financials if isinstance(stock.financials, pd.DataFrame) else pd.DataFrame()
    bs = stock.balance_sheet if isinstance(stock.balance_sheet, pd.DataFrame) else pd.DataFrame()
    cf = stock.cashflow if isinstance(stock.cashflow, pd.DataFrame) else pd.DataFrame()
    earn = stock.earnings if isinstance(stock.earnings, pd.DataFrame) else pd.DataFrame()

    choice = st.radio(
        "Choose Statement",
        ["Income", "Balance Sheet", "Cash Flow", "Earnings"],
        horizontal=True,
    )

    if choice == "Income":
        if fin.empty:
            st.info("No income statement data available.")
        else:
            st.dataframe(fin)
    elif choice == "Balance Sheet":
        if bs.empty:
            st.info("No balance sheet data available.")
        else:
            st.dataframe(bs)
    elif choice == "Cash Flow":
        if cf.empty:
            st.info("No cash flow data available.")
        else:
            st.dataframe(cf)
    else:
        if earn.empty:
            st.info("No earnings data available.")
        else:
            st.dataframe(earn)

# =======================================================
# TAB 3 – RATIOS
# =======================================================
with tab3:
    st.subheader("Key Ratios & Valuation")

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
# TAB 4 – NEWS
# =======================================================
with tab4:
    st.subheader("Latest News")

    try:
        news = stock.news
    except Exception:
        news = []

    if not news:
        st.info("No news available for this ticker.")
    else:
        for item in news[:10]:
            title = item.get("title", "No title")
            link = item.get("link", "#")
            pub = item.get("publisher", "Unknown")
            st.write(f"### [{title}]({link})")
            st.caption(pub)
            st.write("---")
