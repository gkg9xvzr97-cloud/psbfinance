import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import date, timedelta
import plotly.express as px

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="FinSight Terminal",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# CUSTOM STYLING (Bloomberg / Yahoo Finance inspired)
# ---------------------------------------------------------
custom_css = """
<style>
/* Global background and text */
body, .stApp {
    background-color: #111217;
    color: #f5f5f5;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #050608;
    border-right: 1px solid #333;
}

/* Metric cards */
.metric-card {
    background: #191b22;
    padding: 1rem 1.25rem;
    border-radius: 0.75rem;
    border: 1px solid #333;
}

/* Titles */
h1, h2, h3, h4 {
    color: #f5f5f5;
}

/* Accent color similar to Bloomberg yellow */
.accent {
    color: #f3ba2f;
    font-weight: 700;
}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_price_history(ticker: str, start: date, end: date, interval: str = "1d"):
    try:
        data = yf.download(ticker, start=start, end=end, interval=interval, progress=False)
        if data.empty:
            return None
        data.dropna(inplace=True)
        return data
    except Exception:
        return None


@st.cache_data(show_spinner=False)
def load_ticker_object(ticker: str):
    try:
        t = yf.Ticker(ticker)
        # Access something to force fetch
        _ = t.info
        return t
    except Exception:
        return None


def safe_get(dct, key, default=None):
    value = dct.get(key, default)
    return value if value not in [None, "None", "nan"] else default


def compute_basic_ratios(info: dict, financials: pd.DataFrame, balance_sheet: pd.DataFrame):
    ratios = {}

    # Profitability & valuation
    ratios["Market Cap"] = safe_get(info, "marketCap")
    ratios["Trailing P/E"] = safe_get(info, "trailingPE")
    ratios["Forward P/E"] = safe_get(info, "forwardPE")
    ratios["PEG Ratio"] = safe_get(info, "pegRatio")
    ratios["Price to Book"] = safe_get(info, "priceToBook")
    ratios["Dividend Yield"] = safe_get(info, "dividendYield")
    ratios["Return on Assets"] = safe_get(info, "returnOnAssets")
    ratios["Return on Equity"] = safe_get(info, "returnOnEquity")
    ratios["Profit Margin"] = safe_get(info, "profitMargins")
    ratios["Operating Margin"] = safe_get(info, "operatingMargins")

    # Leverage & liquidity from balance sheet
    try:
        latest_bs = balance_sheet.iloc[:, 0]
        current_assets = latest_bs.get("Total Current Assets")
        current_liabilities = latest_bs.get("Total Current Liabilities")
        total_liabilities = latest_bs.get("Total Liab")
        total_equity = latest_bs.get("Total Stockholder Equity")

        if current_assets and current_liabilities and current_liabilities != 0:
            ratios["Current Ratio"] = current_assets / current_liabilities

        if total_liabilities and total_equity and total_equity != 0:
            ratios["Debt to Equity"] = total_liabilities / total_equity

    except Exception:
        pass

    return ratios


def format_large_number(x):
    if x is None or pd.isna(x):
        return "–"
    try:
        x = float(x)
    except Exception:
        return "–"
    abs_x = abs(x)
    if abs_x >= 1_000_000_000_000:
        return f"{x/1_000_000_000_000:.2f}T"
    if abs_x >= 1_000_000_000:
        return f"{x/1_000_000_000:.2f}B"
    if abs_x >= 1_000_000:
        return f"{x/1_000_000:.2f}M"
    if abs_x >= 1_000:
        return f"{x/1_000:.2f}K"
    return f"{x:.2f}"


def format_percent(x):
    if x is None or pd.isna(x):
        return "–"
    try:
        return f"{float(x) * 100:.2f}%"
    except Exception:
        return "–"


# ---------------------------------------------------------
# SIDEBAR CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 💹 FinSight Terminal")
    st.markdown("### A mini Bloomberg-style dashboard")
    st.caption("Powered by Streamlit & Yahoo Finance data (yfinance).")

    primary_ticker = st.text_input("Main Ticker (e.g. AAPL, MSFT, TSLA)", value="AAPL").upper().strip()

    st.markdown("---")
    st.markdown("#### Time Range")
    default_end = date.today()
    default_start = default_end - timedelta(days=365)
    start_date, end_date = st.date_input(
        "Date range",
        value=(default_start, default_end),
        max_value=date.today(),
    )

    interval = st.selectbox(
        "Price Interval",
        options=[
            "1d",
            "5d",
            "1wk",
            "1mo",
            "3mo",
        ],
        format_func=lambda x: {
            "1d": "Daily",
            "5d": "5-Day",
            "1wk": "Weekly",
            "1mo": "Monthly",
            "3mo": "Quarterly",
        }[x],
        index=0,
    )

    st.markdown("---")
    comparison_tickers = st.text_input(
        "Comparison Tickers (comma separated)",
        value="MSFT, GOOGL"
    )
    comparison_list = [t.strip().upper() for t in comparison_tickers.split(",") if t.strip()]

    st.markdown("---")
    st.markdown("#### Display Options")
    show_volume = st.checkbox("Show Volume on Price Chart", value=True)
    log_scale = st.checkbox("Log Scale Price", value=False)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
if not primary_ticker:
    st.warning("Please enter a main ticker symbol in the sidebar to begin.")
    st.stop()

if isinstance(start_date, tuple):
    # Older versions may return a tuple
    start_date, end_date = start_date

price_data = load_price_history(primary_ticker, start_date, end_date + timedelta(days=1), interval)
ticker_obj = load_ticker_object(primary_ticker)

if price_data is None or ticker_obj is None:
    st.error("Could not load data for this ticker. Please check the symbol and your internet connection.")
    st.stop()

info = ticker_obj.info
financials = ticker_obj.financials or pd.DataFrame()
balance_sheet = ticker_obj.balance_sheet or pd.DataFrame()
cashflow = ticker_obj.cashflow or pd.DataFrame()
earnings = ticker_obj.earnings or pd.DataFrame()
sustainability = getattr(ticker_obj, "sustainability", pd.DataFrame())

ratios = compute_basic_ratios(info, financials, balance_sheet)

# ---------------------------------------------------------
# TOP SECTION – OVERVIEW
# ---------------------------------------------------------
company_name = safe_get(info, "longName", primary_ticker)
exchange = safe_get(info, "exchange", "")
currency = safe_get(info, "currency", "")
sector = safe_get(info, "sector", "–")
industry = safe_get(info, "industry", "–")

last_close = price_data["Close"].iloc[-1]
prev_close = price_data["Close"].iloc[-2] if len(price_data) > 1 else last_close
daily_change = last_close - prev_close
daily_pct = daily_change / prev_close * 100 if prev_close != 0 else 0

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown(f"### <span class='accent'>{company_name}</span> ({primary_ticker})", unsafe_allow_html=True)
    st.caption(f"{sector} · {industry} · {exchange} · {currency}")

with col_right:
    st.markdown("#### Last Close")
    change_color = "🟢" if daily_change >= 0 else "🔻"
    st.markdown(
        f"**{last_close:.2f} {currency}**  \n"
        f"{change_color} {daily_change:.2f} ({daily_pct:.2f}%)"
    )

st.markdown("---")

# ---------------------------------------------------------
# LAYOUT: TABS
# ---------------------------------------------------------
tab_overview, tab_financials, tab_ratios, tab_comparisons, tab_news = st.tabs(
    ["📈 Overview", "📊 Financial Statements", "📐 Ratios & Valuation", "📊 Comparisons", "📰 News"]
)

# ---------------------------------------------------------
# TAB 1 – OVERVIEW
# ---------------------------------------------------------
with tab_overview:
    price_col, metrics_col = st.columns([2.3, 1.2])

    with price_col:
        st.subheader("Price Performance")

        chart_df = price_data.reset_index()[["Date", "Close", "Volume"]]
        if log_scale:
            chart_df["Close"] = np.log(chart_df["Close"])

        fig_price = px.area(
            chart_df,
            x="Date",
            y="Close",
            title="Price History",
        )
        fig_price.update_traces(opacity=0.7)
        fig_price.update_layout(
            xaxis_title="Date",
            yaxis_title="Log Price" if log_scale else "Price",
            margin=dict(l=10, r=10, t=30, b=10),
        )
        st.plotly_chart(fig_price, use_container_width=True)

        if show_volume:
            fig_vol = px.bar(
                chart_df,
                x="Date",
                y="Volume",
                title="Volume",
            )
            fig_vol.update_layout(
                xaxis_title="Date",
                yaxis_title="Volume",
                margin=dict(l=10, r=10, t=30, b=10),
            )
            st.plotly_chart(fig_vol, use_container_width=True)

    with metrics_col:
        st.subheader("Key Snapshot")

        mkt_cap = format_large_number(ratios.get("Market Cap"))
        pe = ratios.get("Trailing P/E")
        fpe = ratios.get("Forward P/E")
        div = format_percent(ratios.get("Dividend Yield"))
        roe = format_percent(ratios.get("Return on Equity"))
        margin = format_percent(ratios.get("Profit Margin"))

        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Market Cap**")
        st.markdown(f"{mkt_cap}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Valuation**")
        st.markdown(f"• Trailing P/E: **{pe if pe is not None else '–'}**")
        st.markdown(f"• Forward P/E: **{fpe if fpe is not None else '–'}**")
        st.markdown(f"• Dividend Yield: **{div}**")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("**Profitability**")
        st.markdown(f"• ROE: **{roe}**")
        st.markdown(f"• Net Margin: **{margin}**")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

        st.subheader("52 Week Range")
        fifty_two_week_high = safe_get(info, "fiftyTwoWeekHigh")
        fifty_two_week_low = safe_get(info, "fiftyTwoWeekLow")

        if fifty_two_week_low and fifty_two_week_high:
            pos = (last_close - fifty_two_week_low) / (fifty_two_week_high - fifty_two_week_low)
            progress = max(0, min(1, pos))
            st.write(f"Low: {fifty_two_week_low:.2f} · High: {fifty_two_week_high:.2f}")
            st.progress(progress)
        else:
            st.write("52-week range data not available.")

# ---------------------------------------------------------
# TAB 2 – FINANCIAL STATEMENTS
# ---------------------------------------------------------
with tab_financials:
    st.subheader("Financial Statements")

    fs_tab = st.radio(
        "Select Statement",
        options=["Income Statement", "Balance Sheet", "Cash Flow", "Earnings"],
        horizontal=True,
    )

    def show_statement(df: pd.DataFrame, name: str):
        if df is None or df.empty:
            st.info(f"{name} data not available for {primary_ticker}.")
        else:
            st.dataframe(df.style.format("{:,.0f}"), use_container_width=True)

    if fs_tab == "Income Statement":
        show_statement(financials, "Income Statement")
    elif fs_tab == "Balance Sheet":
        show_statement(balance_sheet, "Balance Sheet")
    elif fs_tab == "Cash Flow":
        show_statement(cashflow, "Cash Flow")
    elif fs_tab == "Earnings":
        if earnings is None or earnings.empty:
            st.info("Earnings data not available.")
        else:
            st.dataframe(earnings.style.format("{:,.0f}"), use_container_width=True)
            st.markdown("##### Earnings Trend")
            earnings_chart = earnings.reset_index().melt(id_vars="Year", var_name="Metric", value_name="Value")
            fig_earn = px.bar(
                earnings_chart,
                x="Year",
                y="Value",
                color="Metric",
                barmode="group",
                title="Earnings & Revenue",
            )
            fig_earn.update_layout(margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_earn, use_container_width=True)

# ---------------------------------------------------------
# TAB 3 – RATIOS & VALUATION
# ---------------------------------------------------------
with tab_ratios:
    st.subheader("Ratios & Valuation Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### Profitability")
        st.write("Return on Assets:", format_percent(ratios.get("Return on Assets")))
        st.write("Return on Equity:", format_percent(ratios.get("Return on Equity")))
        st.write("Net Profit Margin:", format_percent(ratios.get("Profit Margin")))
        st.write("Operating Margin:", format_percent(ratios.get("Operating Margin")))

    with col2:
        st.markdown("##### Valuation")
        st.write("Market Cap:", format_large_number(ratios.get("Market Cap")))
        st.write("Trailing P/E:", ratios.get("Trailing P/E", "–"))
        st.write("Forward P/E:", ratios.get("Forward P/E", "–"))
        st.write("PEG Ratio:", ratios.get("PEG Ratio", "–"))
        st.write("Price to Book:", ratios.get("Price to Book", "–"))

    with col3:
        st.markdown("##### Leverage & Liquidity")
        st.write("Current Ratio:", f"{ratios.get('Current Ratio'):.2f}" if ratios.get("Current Ratio") else "–")
        st.write("Debt to Equity:", f"{ratios.get('Debt to Equity'):.2f}" if ratios.get("Debt to Equity") else "–")

    st.markdown("---")
    st.markdown("##### Valuation vs 52 Week Range")

    if fifty_two_week_low and fifty_two_week_high:
        range_df = pd.DataFrame({
            "Label": ["52W Low", "Current Price", "52W High"],
            "Price": [fifty_two_week_low, last_close, fifty_two_week_high],
        })
        fig_range = px.scatter(
            range_df,
            x="Price",
            y=["Val"] * len(range_df),
            text="Label",
            title="52 Week Range Positioning",
        )
        fig_range.update_yaxes(visible=False, showticklabels=False)
        fig_range.update_layout(margin=dict(l=10, r=10, t=30, b=10))
        st.plotly_chart(fig_range, use_container_width=True)
    else:
        st.info("52-week range data not available.")

# ---------------------------------------------------------
# TAB 4 – COMPARISONS
# ---------------------------------------------------------
with tab_comparisons:
    st.subheader("Peer Comparison")

    if not comparison_list:
        st.info("Add comparison tickers in the sidebar to see peer analysis.")
    else:
        all_tickers = [primary_ticker] + comparison_list
        rows = []
        for t in all_tickers:
            tobj = load_ticker_object(t)
            if tobj is None:
                continue
            inf = tobj.info or {}
            row = {
                "Ticker": t,
                "Name": safe_get(inf, "shortName", t),
                "Sector": safe_get(inf, "sector", "–"),
                "Market Cap": safe_get(inf, "marketCap"),
                "Trailing P/E": safe_get(inf, "trailingPE"),
                "Forward P/E": safe_get(inf, "forwardPE"),
                "Dividend Yield": safe_get(inf, "dividendYield"),
                "Profit Margin": safe_get(inf, "profitMargins"),
                "ROE": safe_get(inf, "returnOnEquity"),
            }
            rows.append(row)

        if not rows:
            st.info("Could not load data for comparison tickers.")
        else:
            comp_df = pd.DataFrame(rows)
            display_df = comp_df.copy()
            display_df["Market Cap"] = display_df["Market Cap"].apply(format_large_number)
            display_df["Dividend Yield"] = display_df["Dividend Yield"].apply(format_percent)
            display_df["Profit Margin"] = display_df["Profit Margin"].apply(format_percent)
            display_df["ROE"] = display_df["ROE"].apply(format_percent)

            st.markdown("##### Key Multiples Table")
            st.dataframe(display_df.set_index("Ticker"), use_container_width=True)

            st.markdown("##### Market Cap vs P/E")
            mc_pe_df = comp_df.dropna(subset=["Market Cap", "Trailing P/E"])
            if not mc_pe_df.empty:
                fig_comp = px.scatter(
                    mc_pe_df,
                    x="Trailing P/E",
                    y="Market Cap",
                    text="Ticker",
                    size="Market Cap",
                    hover_name="Name",
                    title="Market Cap vs Trailing P/E",
                    size_max=60,
                )
                fig_comp.update_layout(margin=dict(l=10, r=10, t=30, b=10))
                st.plotly_chart(fig_comp, use_container_width=True)
            else:
                st.info("Not enough data to plot Market Cap vs P/E.")

# ---------------------------------------------------------
# TAB 5 – NEWS
# ---------------------------------------------------------
with tab_news:
    st.subheader(f"Latest News for {company_name}")

    news_items = []
    try:
        # Newer yfinance versions provide a .news attribute
        news_items = ticker_obj.news or []
    except Exception:
        news_items = []

    if not news_items:
        st.info("No news found via yfinance for this ticker. Consider integrating a news API (e.g. NewsAPI.org) for richer headlines.")
    else:
        for item in news_items[:15]:
            title = item.get("title", "Untitled")
            link = item.get("link", "#")
            publisher = item.get("publisher", "Unknown source")
            st.markdown(f"**[{title}]({link})**")
            st.caption(publisher)
            st.markdown("---")
