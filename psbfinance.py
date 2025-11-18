# pspfinance.py
# PSP Finance — professional terminal (clean build, no emojis)

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

# --------------------------
# Page config
# --------------------------
st.set_page_config(page_title="PSP Finance", layout="wide")

st.title("PSP Finance Intelligence Terminal")
st.subheader("Where future analysts discover financial truths")

st.markdown("""
PSP Finance is a student-built platform that unifies real-time market data, multi-year financials, comparisons, and global news in one dashboard.
It is designed for clarity, speed, and practical insight—helping students and analysts focus on decisions, not data hunting.
""")

# --------------------------
# Helper utilities
# --------------------------

def apply_theme(fig):
    theme = st.session_state.get("ui_theme", "Light")
    if theme == "Dark":
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="black",
            plot_bgcolor="black",
            font_color="white"
        )
    else:
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="white",
            plot_bgcolor="white",
            font_color="black"
        )
    return fig


def compute_simple_return(symbol: str, period: str = "1mo") -> float | None:
    """
    Computes simple % return over the given horizon.
    'period' here is a logical horizon ('1d', '5d', '1mo', '3mo', '6mo', '1y').
    We map it to a yfinance period that gives enough bars.
    """
    # Map logical horizon -> yfinance period
    yf_period_map = {
        "1d": "5d",
        "5d": "1mo",
        "1mo": "1mo",
        "3mo": "3mo",
        "6mo": "6mo",
        "1y": "1y",
    }
    yf_period = yf_period_map.get(period, "1mo")

    df = load_price_history(symbol, period=yf_period, interval="1d")
    if df.empty or "Close" not in df.columns:
        return None

    closes = df["Close"].dropna()
    if len(closes) < 2:
        return None

    # For 1d and 5d horizons: compare last vs previous close
    if period in ["1d", "5d"]:
        last = float(closes.iloc[-1])
        prev = float(closes.iloc[-2])
        if prev == 0:
            return None
        return (last / prev - 1.0) * 100.0

    # For longer horizons: last vs first
    first = float(closes.iloc[0])
    last = float(closes.iloc[-1])
    if first == 0:
        return None
    return (last / first - 1.0) * 100.0



def safe_ticker_df(stock: yf.Ticker, attr: str) -> pd.DataFrame:
    """
    Safely get a DataFrame attribute from yfinance Ticker, e.g. 'financials', 'balance_sheet',
    'cashflow', 'earnings'. Returns empty DataFrame on any error or if not a DataFrame.
    """
    try:
        df = getattr(stock, attr)
        if isinstance(df, pd.DataFrame):
            return df
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def fmt_big(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
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
    return f"{x:.0f}"

def pct(x):
    try:
        return f"{float(x)*100:.2f}%"
    except Exception:
        return "–"

def safe_info(tk: yf.Ticker):
    try:
        return tk.info or {}
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def load_price_history(ticker: str, period="1y", interval="1d"):
    try:
        df = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            threads=False,
        )

        if isinstance(df, pd.DataFrame) and not df.empty:
            # Flatten MultiIndex columns if present
            if isinstance(df.columns, pd.MultiIndex):
                # keep only the first level: ('Close', '^GSPC') -> 'Close'
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns.values]

            # Ensure we have a Date column
            if df.index.name is None:
                df.index.name = "Date"
            df = df.reset_index()

            # Extra fallback: if we *still* don't have 'Date', rename first column
            if "Date" not in df.columns:
                first_col = df.columns[0]
                df = df.rename(columns={first_col: "Date"})
        else:
            df = pd.DataFrame()

        return df
    except Exception:
        return pd.DataFrame()

def get_return(ticker, period="1y"):
    df = load_price_history(ticker, period=period, interval="1d")
    if df.empty or "Close" not in df.columns:
        return None
    prices = df["Close"].dropna()
    if len(prices) < 2:
        return None
    return (prices.iloc[-1] / prices.iloc[0] - 1) * 100


@st.cache_data(show_spinner=False)
def get_ticker_info(ticker: str):
    tk = yf.Ticker(ticker)
    return safe_info(tk)

@st.cache_data(show_spinner=False)
def get_fast_info(ticker: str):
    try:
        tk = yf.Ticker(ticker)
        fi = getattr(tk, "fast_info", {})
        return dict(fi) if fi is not None else {}
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def get_fx_rate(from_ccy: str, to_ccy: str = "USD"):
    if not from_ccy or from_ccy == to_ccy:
        return 1.0
    pair = f"{from_ccy}{to_ccy}=X"
    df = load_price_history(pair, period="5d", interval="1d")
    if df.empty or "Close" not in df.columns:
        return None
    return float(df["Close"].iloc[-1])

def get_theme():
    return st.session_state.get("theme", "Light")

def apply_theme(fig):
    theme = get_theme()
    template = "plotly_dark" if theme == "Dark" else "plotly_white"
    fig.update_layout(template=template)
    return fig

def compute_risk_metrics(ticker: str, benchmark: str, period: str = "1y"):
    prices = load_price_history(ticker, period=period, interval="1d")
    bench = load_price_history(benchmark, period=period, interval="1d")

    if prices.empty or bench.empty or "Close" not in prices.columns or "Close" not in bench.columns:
        return None

    asset = prices[["Date", "Close"]].rename(columns={"Close": "asset"})
    bench = bench[["Date", "Close"]].rename(columns={"Close": "bench"})
    df = pd.merge(asset, bench, on="Date", how="inner")

    df["asset_ret"] = df["asset"].pct_change()
    df["bench_ret"] = df["bench"].pct_change()
    df = df.dropna()
    if df.empty:
        return None

    vol = df["asset_ret"].std() * np.sqrt(252)
    bench_vol = df["bench_ret"].std() * np.sqrt(252)
    corr = df["asset_ret"].corr(df["bench_ret"])

    cum = (1 + df["asset_ret"]).cumprod()
    running_max = cum.cummax()
    drawdowns = cum / running_max - 1
    max_dd = float(drawdowns.min()) if not drawdowns.empty else None

    return {
        "vol": vol,
        "bench_vol": bench_vol,
        "corr": corr,
        "max_dd": max_dd,
        "series": df,
    }

def is_valid_ticker(ticker: str):
    info = get_ticker_info(ticker)
    hist = load_price_history(ticker, period="5d", interval="1d")
    return bool(info) or (not hist.empty)



# --------------------------
# Sidebar: Settings + Navigation
# --------------------------
st.sidebar.markdown("### User Settings")

default_theme = st.sidebar.selectbox(
    "Theme",
    ["Light", "Dark"],
    index=0,
    key="ui_theme"
)

default_benchmark = st.sidebar.selectbox(
    "Benchmark index",
    ["^GSPC", "^NDX", "^DJI", "^STOXX50E", "BTC-USD"],
    index=0,
    key="ui_benchmark"
)

section = st.sidebar.radio("Navigate", [
    "Home",
    "Company Search",
    "AI Comparison",
    "SEC Filings",
    "News Feed",
    "Global Markets",
    "Portfolio"
], key="nav_radio")

# --------------------------
# Home
# --------------------------
if section == "Home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Quick start")
        st.write("- Enter a ticker in Company Search")
        st.write("- Add peer tickers in AI Comparison")
        st.write("- Review recent documents in SEC Filings")
    with col2:
        st.markdown("### Why it helps")
        st.write("- Multi-year statements in seconds")
        st.write("- Clear plots for valuation and profitability")
        st.write("- Concise summaries to accelerate insights")
    with col3:
        st.markdown("### Roadmap")
        st.write("- Options implied volatility and skew")
        st.write("- Corporate bonds and CDS spreads")
        st.write("- Macro dashboards and alerts")

# --------------------------
# Company Search
# --------------------------
if section == "Company Search":
    st.header("Company search and detailed analysis")

    query = st.text_input(
        "Enter a company ticker or name (e.g., AAPL, MSFT, AIR.PA):",
        key="company_search_input"
    ).strip().upper()

    tabs = st.tabs(["Overview", "Financials", "Ratios and decomposition", "Peers", "Summary"])

    if query:
        if not is_valid_ticker(query):
            st.error("Could not retrieve data for this ticker. Please check the symbol or try another one.")
        else:
            # --- core objects ---
            stock = yf.Ticker(query)
            info = get_ticker_info(query)
            fast_info = get_fast_info(query)
            default_period_for_calc = st.session_state.get("setting_default_period", "1y") or "1y"

            # --------------------------
            # Overview tab
            # --------------------------
            with tabs[0]:
                st.subheader(f"Overview — {info.get('longName', query)} ({query})")

                # Live price snapshot
                st.markdown("#### Live snapshot")
                prices_3m = load_price_history(query, period="3mo", interval="1d")
                last_price = fast_info.get("lastPrice") or fast_info.get("last_price")
                prev_close = fast_info.get("previousClose")
                bid = fast_info.get("bid")
                ask = fast_info.get("ask")
                currency = fast_info.get("currency") or info.get("currency", "–")

                # Fallback from history if fast_info incomplete
                if last_price is None and not prices_3m.empty and "Close" in prices_3m.columns:
                    last_price = float(prices_3m["Close"].iloc[-1])
                    if prev_close is None and len(prices_3m) >= 2:
                        prev_close = float(prices_3m["Close"].iloc[-2])

                change = None
                change_pct = None
                if last_price is not None and prev_close is not None and prev_close != 0:
                    change = last_price - prev_close
                    change_pct = change / prev_close * 100

                snap_col1, snap_col2, snap_col3, snap_col4 = st.columns(4)
                with snap_col1:
                    st.metric(
                        "Last price",
                        f"{last_price:.2f} {currency}" if last_price is not None else "–",
                        f"{change:+.2f}" if change is not None else None
                    )
                with snap_col2:
                    st.metric(
                        "Day change (%)",
                        f"{change_pct:+.2f}%" if change_pct is not None else "–"
                    )
                with snap_col3:
                    st.write(f"Bid: {bid:.2f} {currency}" if bid is not None else "Bid: –")
                    st.write(f"Ask: {ask:.2f} {currency}" if ask is not None else "Ask: –")
                with snap_col4:
                    st.write(
                        f"Previous close: {prev_close:.2f} {currency}"
                        if prev_close is not None
                        else "Previous close: –"
                    )

                # Multi-currency (approximate)
                st.markdown("#### Currency and market value")
                fx_rate = None
                if currency and currency not in ["USD", "–"]:
                    fx_rate = get_fx_rate(currency, "USD")

                mc_local = info.get("marketCap")
                col_fx1, col_fx2, col_fx3 = st.columns(3)
                with col_fx1:
                    st.write(f"Currency: {currency}")
                    st.write(f"Market capitalization (local): {fmt_big(mc_local)} {currency}")
                with col_fx2:
                    if fx_rate and mc_local:
                        mc_usd = mc_local * fx_rate
                        st.write(f"FX {currency}/USD: {fx_rate:.4f}")
                        st.write(f"Market capitalization (USD): {fmt_big(mc_usd)}")
                    else:
                        st.write("FX rate to USD: –")
                        st.write("Market capitalization (USD): –")
                with col_fx3:
                    if last_price is not None and fx_rate:
                        st.write(f"Price in USD (approx.): {last_price * fx_rate:.2f} USD")
                    else:
                        st.write("Price in USD (approx.): –")

                overview_cols = st.columns(4)
                with overview_cols[0]:
                    st.write(f"Sector: {info.get('sector', '–')}")
                    st.write(f"Industry: {info.get('industry', '–')}")
                    st.write(f"Country: {info.get('country', '–')}")
                with overview_cols[1]:
                    st.write(f"Market capitalization: {fmt_big(info.get('marketCap'))}")
                    st.write(f"Shares outstanding: {fmt_big(info.get('sharesOutstanding'))}")
                    st.write(f"Beta: {info.get('beta', '–')}")
                with overview_cols[2]:
                    st.write(f"Trailing P/E: {info.get('trailingPE', '–')}")
                    st.write(f"Price/Sales (TTM): {info.get('priceToSalesTrailing12Months', '–')}")
                    st.write(f"EV/EBITDA: {info.get('enterpriseToEbitda', '–')}")
                with overview_cols[3]:
                    st.write(f"Dividend yield: {pct(info.get('dividendYield'))}")
                    st.write(f"52-week high: {info.get('fiftyTwoWeekHigh', '–')}")
                    st.write(f"52-week low: {info.get('fiftyTwoWeekLow', '–')}")

                st.markdown("#### Price performance")
                period_options = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
                default_period = st.session_state.get("setting_default_period", "1y")
                if default_period not in period_options:
                    default_period = "1y"
                default_idx = period_options.index(default_period)

                period = st.selectbox(
                    "Period",
                    period_options,
                    index=default_idx,
                    key="price_period"
                )
                interval = st.selectbox("Interval", ["1d", "1wk"], index=0, key="price_interval")
                prices = load_price_history(query, period=period, interval=interval)
                if prices.empty or "Close" not in prices.columns or "Date" not in prices.columns:
                    st.warning("Price data unavailable.")
                else:
                    try:
                        fig_price = go.Figure()
                        fig_price.add_trace(go.Scatter(
                            x=prices["Date"], y=prices["Close"],
                            name=query, mode="lines"
                        ))

                        # Benchmark overlay
                        bench = default_benchmark
                        bench_df = load_price_history(bench, period=period, interval=interval)

                        if not bench_df.empty and "Close" in bench_df.columns:
                            fig_price.add_trace(go.Scatter(
                                x=bench_df["Date"], y=bench_df["Close"],
                                name=f"{bench} (Benchmark)",
                                mode="lines",
                                line=dict(dash="dash")
                            ))

                        fig_price.update_layout(title=f"{query} vs {bench} ({period})")

                        fig_price = apply_theme(fig_price)
                        st.plotly_chart(fig_price, use_container_width=True)
                    except ValueError:
                        st.warning("Could not render price chart due to unexpected data format.")


            # --------------------------
            # Financials tab
            # --------------------------
            with tabs[1]:
                st.subheader("Financial statements (annual)")
                fin_cols = st.columns(3)

                # Income statement
                with fin_cols[0]:
                    st.markdown("Income statement")
                    inc = safe_ticker_df(stock, "financials")
                    if inc.empty:
                        st.info("Income statement unavailable.")
                    else:
                        st.dataframe(inc)
                        st.download_button(
                            "Download income (CSV)",
                            inc.to_csv().encode(),
                            "income_statement.csv",
                            key="dl_income"
                        )

                # Balance sheet
                with fin_cols[1]:
                    st.markdown("Balance sheet")
                    bal = safe_ticker_df(stock, "balance_sheet")
                    if bal.empty:
                        st.info("Balance sheet unavailable.")
                    else:
                        st.dataframe(bal)
                        st.download_button(
                            "Download balance (CSV)",
                            bal.to_csv().encode(),
                            "balance_sheet.csv",
                            key="dl_balance"
                        )

                # Cash flow
                with fin_cols[2]:
                    st.markdown("Cash flow statement")
                    cf = safe_ticker_df(stock, "cashflow")
                    if cf.empty:
                        st.info("Cash flow statement unavailable.")
                    else:
                        st.dataframe(cf)
                        st.download_button(
                            "Download cash flow (CSV)",
                            cf.to_csv().encode(),
                            "cash_flow.csv",
                            key="dl_cashflow"
                        )

                st.markdown("#### Growth trends (revenue and earnings)")

                # Try loading annual income statement (Yahoo changed APIs)
                try:
                    inc = stock.income_stmt.copy()
                except Exception:
                    inc = pd.DataFrame()

                if not inc.empty:
                    # Check revenue & earnings rows
                    if "TotalRevenue" in inc.index and "NetIncome" in inc.index:
                        rev = inc.loc["TotalRevenue"].dropna()
                        net = inc.loc["NetIncome"].dropna()

                        if not rev.empty and not net.empty:
                            fig_growth = go.Figure()
                            fig_growth.add_trace(go.Bar(
                                x=rev.index.astype(str),
                                y=rev.values,
                                name="Revenue"
                            ))
                            fig_growth.add_trace(go.Bar(
                                x=net.index.astype(str),
                                y=net.values,
                                name="Net income"
                            ))
                            fig_growth.update_layout(
                                barmode="group",
                                title="Revenue and Net Income (Annual)"
                            )
                            st.plotly_chart(fig_growth, use_container_width=True)
                        else:
                            st.info("Revenue/Earnings series unavailable.")
                    else:
                        st.info("Revenue/Earnings series unavailable.")
                else:
                    st.info("Revenue/Earnings series unavailable.")

            # --------------------------
            # Ratios and decomposition tab
            # --------------------------
            with tabs[2]:
                st.subheader("Valuation, profitability, and risk decomposition")

                pe = info.get("trailingPE", None)
                ps = info.get("priceToSalesTrailing12Months", None)
                ev_ebitda = info.get("enterpriseToEbitda", None)
                profit_margin = info.get("profitMargins", None)
                op_margin = info.get("operatingMargins", None)
                roe = info.get("returnOnEquity", None)
                roa = info.get("returnOnAssets", None)
                fcf = info.get("freeCashflow", None)

                colA, colB = st.columns([2, 1])
                with colA:
                    val_df = pd.DataFrame({
                        "Metric": ["P/E", "Price/Sales (TTM)", "EV/EBITDA"],
                        "Value": [pe, ps, ev_ebitda]
                    }).dropna()
                    if val_df.empty:
                        st.info("Valuation metrics unavailable.")
                    else:
                        fig_val = px.bar(val_df, x="Metric", y="Value", title="Valuation metrics")
                        fig_val = apply_theme(fig_val)
                        st.plotly_chart(fig_val, use_container_width=True)

                    prof_df = pd.DataFrame({
                        "Metric": ["Profit margin", "Operating margin", "Return on equity", "Return on assets"],
                        "Value": [profit_margin, op_margin, roe, roa]
                    }).dropna()
                    if prof_df.empty:
                        st.info("Profitability metrics unavailable.")
                    else:
                        prof_df["Value_pct"] = prof_df["Value"] * 100
                        fig_prof = px.bar(prof_df, x="Metric", y="Value_pct", title="Profitability (%)")
                        fig_prof.update_yaxes(title="Percent")
                        fig_prof = apply_theme(fig_prof)
                        st.plotly_chart(fig_prof, use_container_width=True)

                with colB:
                    st.markdown("##### Key facts")
                    st.write(f"Market capitalization: {fmt_big(info.get('marketCap'))}")
                    st.write(f"Free cash flow: {fmt_big(fcf)}")
                    st.write(f"Dividend yield: {pct(info.get('dividendYield'))}")
                    st.write(f"Beta: {info.get('beta', '–')}")

                st.markdown("#### Risk metrics vs benchmark")
                risk_period = st.selectbox(
                    "Risk lookback period",
                    ["6mo", "1y", "2y", "5y"],
                    index=["6mo", "1y", "2y", "5y"].index(
                        default_period_for_calc if default_period_for_calc in ["6mo", "1y", "2y", "5y"] else "1y"
                    ),
                    key="risk_period"
                )
                benchmark = st.session_state.get("setting_default_benchmark", "^GSPC")
                metrics = compute_risk_metrics(query, benchmark, period=risk_period)

                if metrics is None:
                    st.info("Risk metrics unavailable for this ticker/benchmark combination.")
                else:
                    rcol1, rcol2, rcol3, rcol4 = st.columns(4)
                    with rcol1:
                        st.metric("Volatility (annualized)", f"{metrics['vol']*100:.2f}%")
                    with rcol2:
                        st.metric("Benchmark vol (annualized)", f"{metrics['bench_vol']*100:.2f}%")
                    with rcol3:
                        st.metric("Correlation vs benchmark", f"{metrics['corr']:.2f}")
                    with rcol4:
                        if metrics["max_dd"] is not None:
                            st.metric("Max drawdown", f"{metrics['max_dd']*100:.2f}%")
                        else:
                            st.metric("Max drawdown", "–")

                    df_r = metrics["series"].copy()
                    df_r["asset_index"] = (1 + df_r["asset_ret"]).cumprod()
                    df_r["bench_index"] = (1 + df_r["bench_ret"]).cumprod()
                    fig_risk = go.Figure()
                    fig_risk.add_trace(go.Scatter(x=df_r["Date"], y=df_r["asset_index"], name=query))
                    fig_risk.add_trace(go.Scatter(x=df_r["Date"], y=df_r["bench_index"], name=benchmark))
                    fig_risk.update_layout(title=f"Normalized performance ({risk_period})")
                    fig_risk = apply_theme(fig_risk)
                    st.plotly_chart(fig_risk, use_container_width=True)

            # --------------------------
            # Peers tab
            # --------------------------
            with tabs[3]:
                st.subheader("Peer comparison")
                peer_input = st.text_input(
                    "Enter peer tickers (comma-separated), e.g., MSFT, GOOG, AMZN",
                    key="peer_input"
                )
                peers = [p.strip().upper() for p in peer_input.split(",") if p.strip()]
                rows = []
                for tk in peers:
                    try:
                        pi = get_ticker_info(tk)
                        if not pi:
                            continue
                        rows.append({
                            "Ticker": tk,
                            "Name": pi.get("longName", tk),
                            "Sector": pi.get("sector", "–"),
                            "Industry": pi.get("industry", "–"),
                            "MarketCap": pi.get("marketCap", None),
                            "P/E": pi.get("trailingPE", None),
                            "Price/Sales": pi.get("priceToSalesTrailing12Months", None),
                            "EV/EBITDA": pi.get("enterpriseToEbitda", None),
                            "ProfitMargin": pi.get("profitMargins", None),
                            "OperatingMargin": pi.get("operatingMargins", None),
                            "ROE": pi.get("returnOnEquity", None),
                            "ROA": pi.get("returnOnAssets", None)
                        })
                    except Exception:
                        continue
                peer_df = pd.DataFrame(rows)
                if peer_df.empty:
                    st.info("Add peer tickers to see comparisons.")
                else:
                    st.dataframe(peer_df)

                    cap_df = peer_df[["Ticker", "MarketCap"]].dropna()
                    if not cap_df.empty:
                        fig_cap = px.bar(cap_df, x="Ticker", y="MarketCap", title="Market capitalization comparison")
                        fig_cap = apply_theme(fig_cap)
                        st.plotly_chart(fig_cap, use_container_width=True)

                    pe_df = peer_df[["Ticker", "P/E"]].dropna()
                    if not pe_df.empty:
                        fig_pe = px.bar(pe_df, x="Ticker", y="P/E", title="P/E comparison")
                        fig_pe = apply_theme(fig_pe)
                        st.plotly_chart(fig_pe, use_container_width=True)

                    pm_df = peer_df[["Ticker", "ProfitMargin"]].dropna()
                    if not pm_df.empty:
                        pm_df["ProfitMargin_pct"] = pm_df["ProfitMargin"] * 100
                        fig_pm = px.bar(pm_df, x="Ticker", y="ProfitMargin_pct", title="Profit margin (%)")
                        fig_pm.update_yaxes(title="Percent")
                        fig_pm = apply_theme(fig_pm)
                        st.plotly_chart(fig_pm, use_container_width=True)
            # --------------------------
            #  Benchmark comparison
            # --------------------------
            st.markdown("### Benchmark comparison")

            stock_ret = get_return(query, "1y")
            benchmark = st.session_state.get("setting_default_benchmark", "^GSPC")
            bench_ret = get_return(benchmark, "1y")

            if stock_ret is not None and bench_ret is not None:
                rel = stock_ret - bench_ret

                st.write(f"**1Y return for {query}:** {stock_ret:.2f}%")
                st.write(f"**1Y return for benchmark ({default_benchmark}):** {bench_ret:.2f}%")
                st.write(f"**Relative performance:** {rel:+.2f}%")
            else:
                st.info("Return comparison unavailable.")




            # --------------------------
            # Summary tab (7 sentences)
            # --------------------------
            with tabs[4]:
                st.subheader("Analyst-style summary")

                earn_sum = safe_ticker_df(stock, "earnings")
                if not earn_sum.empty:
                    trend_line = "Revenue and earnings trends indicate the direction of growth across recent years."
                else:
                    trend_line = "Historical revenue and earnings detail is limited or unavailable via this data source."

                # reuse pe/ps/ev_ebitda from ratios tab
                lines = []
                lines.append(f"{info.get('longName', query)} operates in {info.get('sector', '–')} with a focus on {info.get('industry', '–')}.")
                lines.append(f"Market capitalization is {fmt_big(info.get('marketCap'))}; core valuation metrics include P/E={pe or '–'}, Price/Sales={ps or '–'}, and EV/EBITDA={ev_ebitda or '–'}.")
                lines.append(f"Profitability indicates profit margin {pct(info.get('profitMargins'))} and operating margin {pct(info.get('operatingMargins'))}.")
                lines.append(f"Returns on capital include return on equity {pct(info.get('returnOnEquity'))} and return on assets {pct(info.get('returnOnAssets'))}.")
                lines.append(f"Dividend yield stands at {pct(info.get('dividendYield'))}, while free cash flow is {fmt_big(info.get('freeCashflow'))}.")
                lines.append(trend_line)
                lines.append("Overall positioning reflects valuation, margin durability, cash generation, and sector dynamics relative to peers and a chosen benchmark.")
                st.info(" ".join(lines))

# --------------------------
# AI Comparison (multi-ticker)
# --------------------------
if section == "AI Comparison":
    st.header("Multi-ticker comparison")
    tickers = st.text_input("Enter tickers (comma-separated), e.g., AAPL, MSFT, NVDA", key="compare_input")
    ts = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if ts:
        data = []
        for tk in ts:
            try:
                ii = get_ticker_info(tk)
                if not ii:
                    continue
                data.append({
                    "Ticker": tk,
                    "Name": ii.get("longName", tk),
                    "Sector": ii.get("sector", "–"),
                    "MarketCap": ii.get("marketCap", None),
                    "P/E": ii.get("trailingPE", None),
                    "Price/Sales": ii.get("priceToSalesTrailing12Months", None),
                    "EV/EBITDA": ii.get("enterpriseToEbitda", None),
                    "ProfitMargin": ii.get("profitMargins", None),
                    "OperatingMargin": ii.get("operatingMargins", None),
                    "ROE": ii.get("returnOnEquity", None),
                    "ROA": ii.get("returnOnAssets", None)
                })
            except Exception:
                pass
        df = pd.DataFrame(data)
        if df.empty:
            st.info("No data for these tickers.")
        else:
            st.dataframe(df)

            for col in ["MarketCap", "P/E", "Price/Sales", "EV/EBITDA"]:
                sub = df[["Ticker", col]].dropna()
                if not sub.empty:
                    fig = px.bar(sub, x="Ticker", y=col, title=f"{col} comparison")
                    fig = apply_theme(fig)
                    st.plotly_chart(fig, use_container_width=True)

            st.markdown("#### Comparison summary")
            biggest = df.loc[df["MarketCap"].idxmax(), "Ticker"] if df["MarketCap"].notna().any() else ts[0]
            lowest_pe = df.loc[df["P/E"].idxmin(), "Ticker"] if df["P/E"].notna().any() else ts[0]
            highest_margin = df.loc[df["ProfitMargin"].idxmax(), "Ticker"] if df["ProfitMargin"].notna().any() else ts[0]
            lines = []
            lines.append(f"This comparison covers {', '.join(ts)}.")
            lines.append(f"The largest by market capitalization is {biggest}.")
            lines.append(f"On valuation, {lowest_pe} shows the lowest P/E among the group.")
            lines.append(f"Profitability leadership is {highest_margin} by profit margin.")
            lines.append("Growth trajectories and margin profiles differ, influencing risk-adjusted attractiveness.")
            lines.append("Relative valuation (P/E, Price/Sales, EV/EBITDA) frames expectations for returns.")
            lines.append("Overall positioning depends on cash generation, margin durability, and sector tailwinds.")
            st.info(" ".join(lines))

# --------------------------
# SEC Filings
# --------------------------
if section == "SEC Filings":
    st.header("SEC filings viewer")
    sec_ticker = st.text_input("Enter a US company ticker (e.g., AAPL, MSFT, TSLA)", key="sec_input").strip().upper()
    if sec_ticker:
        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={sec_ticker}&type=&owner=exclude&count=20&action=getcompany"
        try:
            resp = requests.get(
                base_url,
                headers={"User-Agent": "PSPFinance/1.0 (contact: example@student.edu)"},
                timeout=10
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            rows = soup.find_all("tr")
            found = False
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    form_type = cols[0].text.strip()
                    filing_date = cols[3].text.strip()
                    link_tag = cols[1].find("a")
                    if link_tag:
                        filing_link = "https://www.sec.gov" + link_tag["href"]
                        if form_type in ["10-K", "10-Q", "8-K", "S-1", "DEF 14A"]:
                            st.markdown(f"- {form_type} filed on {filing_date} — [View filing]({filing_link})")
                            found = True
            if not found:
                st.warning("No recent 10-K, 10-Q, 8-K, S-1, or DEF 14A filings found.")
        except requests.exceptions.RequestException:
            st.error("Network error while retrieving SEC filings.")
        except Exception:
            st.error("Unexpected error. Please try again.")


# --------------------------
# News Feed (Yahoo RSS reliable)
# --------------------------
if section == "News Feed":
    st.header("News feed")
    st.write("Enter a ticker to fetch recent headlines (Yahoo Finance RSS).")

    news_ticker = st.text_input(
        "Ticker for news (e.g., AAPL, MSFT, GOOG)",
        key="news_input_rss"
    ).strip().upper()

    if news_ticker:
        rss_url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={news_ticker}&region=US&lang=en-US"

        try:
            resp = requests.get(rss_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "xml")
            items = soup.find_all("item")

            if not items:
                st.warning("No news found. RSS feed returned no articles.")
            else:
                for item in items[:15]:
                    title = item.title.text if item.title else "No title"
                    link = item.link.text if item.link else "#"
                    pub = item.pubDate.text if item.pubDate else ""
                    st.markdown(f"- **{title}** — {pub} — [Read]({link})")

        except Exception as e:
            st.error(f"Could not load RSS news feed: {e}")

# --------------------------
# Global Markets — full dashboard
# --------------------------
if section == "Global Markets":
    st.header("Global markets dashboard")
    st.write("""
    A quick view across global equity indices, FX, commodities, and crypto.
    Explore performance over different horizons, inspect individual charts, and scan macro headlines.
    """)

    # ------- Controls -------
    horizon = st.selectbox(
        "Performance horizon",
        ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
        index=3,
        key="gm_horizon"
    )

    st.markdown("### Market groups")

    # ------- Symbol groups -------
    index_symbols = {
        "US": ["^GSPC", "^NDX", "^DJI"],
        "Europe": ["^STOXX50E", "^FTSE", "^GDAXI"],
        "Asia": ["^N225", "^HSI", "000001.SS"],  # Nikkei, Hang Seng, Shanghai Comp
    }

    index_labels = {
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "^DJI": "Dow Jones",
        "^STOXX50E": "Euro Stoxx 50",
        "^FTSE": "FTSE 100",
        "^GDAXI": "DAX",
        "^N225": "Nikkei 225",
        "^HSI": "Hang Seng",
        "000001.SS": "Shanghai Composite",
    }

    commodity_symbols = ["GC=F", "SI=F", "CL=F", "NG=F"]
    commodity_labels = {
        "GC=F": "Gold",
        "SI=F": "Silver",
        "CL=F": "WTI Crude",
        "NG=F": "Nat. Gas",
    }

    fx_symbols = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "EURGBP=X", "EURJPY=X"]
    fx_labels = {
        "EURUSD=X": "EUR/USD",
        "GBPUSD=X": "GBP/USD",
        "USDJPY=X": "USD/JPY",
        "EURGBP=X": "EUR/GBP",
        "EURJPY=X": "EUR/JPY",
    }

    crypto_symbols = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD"]
    crypto_labels = {
        "BTC-USD": "Bitcoin",
        "ETH-USD": "Ethereum",
        "SOL-USD": "Solana",
        "BNB-USD": "BNB",
    }

    # ------- Build performance table for all assets -------
    perf_rows = []

    # Indices
    for region, syms in index_symbols.items():
        for s in syms:
            ret = compute_simple_return(s, period=horizon)
            perf_rows.append({
                "Symbol": s,
                "Name": index_labels.get(s, s),
                "Region/Group": region,
                "Type": "Index",
                f"Return {horizon}": ret,
            })

    # Commodities
    for s in commodity_symbols:
        ret = compute_simple_return(s, period=horizon)
        perf_rows.append({
            "Symbol": s,
            "Name": commodity_labels.get(s, s),
            "Region/Group": "Commodities",
            "Type": "Commodity",
            f"Return {horizon}": ret,
        })

    # FX
    for s in fx_symbols:
        ret = compute_simple_return(s, period=horizon)
        perf_rows.append({
            "Symbol": s,
            "Name": fx_labels.get(s, s),
            "Region/Group": "FX",
            "Type": "FX",
            f"Return {horizon}": ret,
        })

    # Crypto
    for s in crypto_symbols:
        ret = compute_simple_return(s, period=horizon)
        perf_rows.append({
            "Symbol": s,
            "Name": crypto_labels.get(s, s),
            "Region/Group": "Crypto",
            "Type": "Crypto",
            f"Return {horizon}": ret,
        })

    perf_df = pd.DataFrame(perf_rows)

    # ---- Performance "heatmap" ----
    st.markdown("### Performance map")

    if perf_df.empty or perf_df[f"Return {horizon}"].isna().all():
        st.info("Performance data unavailable for the selected horizon.")
    else:
        perf_df_sorted = perf_df.sort_values(by=f"Return {horizon}", ascending=False)

        # Display colored table (heatmap-like)
        def color_ret(val):
            if pd.isna(val):
                return ""
            if val > 0:
                return "background-color: rgba(0, 150, 0, 0.3);"
            elif val < 0:
                return "background-color: rgba(200, 0, 0, 0.3);"
            else:
                return ""

        styled = perf_df_sorted.style.format({f"Return {horizon}": "{:+.2f}%"}) \
            .applymap(color_ret, subset=[f"Return {horizon}"])

        st.dataframe(styled, use_container_width=True)

        # Bar chart of returns
        chart_df = perf_df_sorted.dropna(subset=[f"Return {horizon}"])
        if not chart_df.empty:
            fig_heat = px.bar(
                chart_df,
                x="Name",
                y=f"Return {horizon}",
                color=f"Return {horizon}",
                title=f"Returns by asset ({horizon})",
            )
            fig_heat.update_yaxes(title="Percent")
            fig_heat.update_layout(xaxis_tickangle=-45)
            fig_heat = apply_theme(fig_heat)
            st.plotly_chart(fig_heat, use_container_width=True)

    # ------- Focused chart for one chosen market -------
    st.markdown("### Focus chart")

    # Build flat list of all symbols safely
    all_symbols = []
    for region_syms in index_symbols.values():
        all_symbols.extend(region_syms)
    all_symbols.extend(commodity_symbols)
    all_symbols.extend(fx_symbols)
    all_symbols.extend(crypto_symbols)

    # Name map for display
    all_name_map = {}
    all_name_map.update(index_labels)
    all_name_map.update(commodity_labels)
    all_name_map.update(fx_labels)
    all_name_map.update(crypto_labels)

    focus_symbol = st.selectbox(
        "Select a market to chart (1 year)",
        options=all_symbols,
        format_func=lambda s: f"{all_name_map.get(s, s)} ({s})",
        key="gm_focus_symbol"
    )

    focus_data = load_price_history(focus_symbol, period="1y", interval="1d")

    if (
        focus_data.empty
        or "Date" not in focus_data.columns
        or "Close" not in focus_data.columns
    ):
        st.info("No historical data available for this symbol.")
    else:
        try:
            fig_focus = px.line(
                focus_data,
                x="Date",
                y="Close",
                title=f"{all_name_map.get(focus_symbol, focus_symbol)} — 1-year price"
            )
            fig_focus = apply_theme(fig_focus)
            st.plotly_chart(fig_focus, use_container_width=True)
        except ValueError:
            st.warning("Could not render focus chart due to unexpected data format.")

    # ------- FX snapshot -------
    st.markdown("### FX snapshot")

    fx_rows = []
    for s in fx_symbols:
        df_fx = load_price_history(s, period="5d", interval="1d")
        if df_fx.empty or "Close" not in df_fx.columns:
            last = change = None
        else:
            closes = df_fx["Close"].dropna()
            if len(closes) >= 2:
                last = float(closes.iloc[-1])
                prev = float(closes.iloc[-2])
                change = (last / prev - 1.0) * 100.0 if prev != 0 else None
            elif len(closes) == 1:
                last = float(closes.iloc[-1])
                change = None
            else:
                last = change = None

        fx_rows.append({
            "Pair": fx_labels.get(s, s),
            "Last": last,
            "1D %": change,
        })
    fx_df = pd.DataFrame(fx_rows)
    if fx_df.empty:
        st.info("FX data unavailable.")
    else:
        fx_disp = fx_df.copy()
        fx_disp["Last"] = fx_disp["Last"].map(lambda x: f"{x:,.4f}" if pd.notna(x) else "–")
        fx_disp["1D %"] = fx_disp["1D %"].map(lambda x: f"{x:+.2f}%" if pd.notna(x) else "–")
        st.dataframe(fx_disp, use_container_width=True)

    # ------- Crypto snapshot -------
    st.markdown("### Crypto snapshot")

    crypto_rows = []
    for s in crypto_symbols:
        df_c = load_price_history(s, period="5d", interval="1d")
        if df_c.empty or "Close" not in df_c.columns:
            last = change = None
        else:
            closes = df_c["Close"].dropna()
            if len(closes) >= 2:
                last = float(closes.iloc[-1])
                prev = float(closes.iloc[-2])
                change = (last / prev - 1.0) * 100.0 if prev != 0 else None
            elif len(closes) == 1:
                last = float(closes.iloc[-1])
                change = None
            else:
                last = change = None

        crypto_rows.append({
            "Asset": crypto_labels.get(s, s),
            "Last (USD)": last,
            "1D %": change,
        })
    crypto_df = pd.DataFrame(crypto_rows)
    if crypto_df.empty:
        st.info("Crypto data unavailable.")
    else:
        c_disp = crypto_df.copy()
        c_disp["Last (USD)"] = c_disp["Last (USD)"].map(
            lambda x: f"{x:,.2f}" if pd.notna(x) else "–"
        )
        c_disp["1D %"] = c_disp["1D %"].map(
            lambda x: f"{x:+.2f}%" if pd.notna(x) else "–"
        )
        st.dataframe(c_disp, use_container_width=True)

    # ------- Global macro news -------
    st.markdown("### Global macro news")

    macro_rss = "https://billmitchell.org/blog/?feed=rss2"

    try:
        resp = requests.get(macro_rss, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        items = soup.find_all("item")

        if not items:
            st.info("No macro news articles found.")
        else:
            for item in items[:10]:
                title = item.title.text if item.title else "No title"
                link = item.link.text if item.link else "#"
                pub = item.pubDate.text if item.pubDate else ""
                st.markdown(f"- **{title}** — {pub} — [Read]({link})")
    except Exception as e:
        st.error(f"Could not load macro news feed: {e}")





# --------------------------
# Portfolio (with quantities, P/L, weights, performance & risk)
# --------------------------
if section == "Portfolio":
    st.header("Portfolio tracker")

    st.write("""
    Enter your holdings with quantity and cost basis per share.
    You can edit the table directly or upload a CSV with columns:
    **Ticker, Quantity, CostBasis** (CostBasis = cost per share).
    """)

    # Optional CSV upload
    uploaded_file = st.file_uploader(
        "Upload portfolio CSV (Ticker, Quantity, CostBasis)",
        type=["csv"],
        key="portfolio_csv"
    )

    if "portfolio_df" not in st.session_state:
        # Start with an example portfolio
        st.session_state["portfolio_df"] = pd.DataFrame({
            "Ticker": ["AAPL", "MSFT"],
            "Quantity": [10, 5],
            "CostBasis": [150.0, 280.0],  # cost per share
        })

    if uploaded_file is not None:
        try:
            df_upload = pd.read_csv(uploaded_file)
            df_upload.columns = [c.strip() for c in df_upload.columns]
            required_cols = {"Ticker", "Quantity", "CostBasis"}
            if not required_cols.issubset(set(df_upload.columns)):
                st.error("CSV must contain columns: Ticker, Quantity, CostBasis")
            else:
                st.session_state["portfolio_df"] = df_upload[list(required_cols)]
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

    # Editable table for portfolio
    port_df = st.data_editor(
        st.session_state["portfolio_df"],
        num_rows="dynamic",
        key="portfolio_editor",
        use_container_width=True
    )

    # Save back to session state
    st.session_state["portfolio_df"] = port_df

    # Clean and compute base metrics
    port_df = port_df.copy()
    if port_df.empty:
        st.info("Use the table above to add your first holding.")
    else:
        port_df["Ticker"] = port_df["Ticker"].astype(str).str.upper().str.strip()
        port_df["Quantity"] = pd.to_numeric(port_df["Quantity"], errors="coerce").fillna(0.0)
        port_df["CostBasis"] = pd.to_numeric(port_df["CostBasis"], errors="coerce").fillna(0.0)

        port_df = port_df[port_df["Ticker"] != ""]
        if port_df.empty:
            st.info("Add at least one valid ticker.")
        else:
            rows = []
            for _, row in port_df.iterrows():
                tk = row["Ticker"]
                qty = float(row["Quantity"])
                cost_basis = float(row["CostBasis"])

                if qty <= 0:
                    continue

                hist = load_price_history(tk, period="1y", interval="1d")
                if hist.empty or "Close" not in hist.columns:
                    last_price = None
                else:
                    last_price = float(hist["Close"].iloc[-1])

                if last_price is None:
                    market_value = None
                    pl = None
                    pl_pct = None
                    total_cost = qty * cost_basis if cost_basis is not None else None
                else:
                    market_value = qty * last_price
                    total_cost = qty * cost_basis
                    pl = market_value - total_cost
                    pl_pct = (pl / total_cost) * 100 if total_cost != 0 else None

                rows.append({
                    "Ticker": tk,
                    "Quantity": qty,
                    "CostBasis": cost_basis,
                    "LastPrice": last_price,
                    "MarketValue": market_value,
                    "TotalCost": total_cost,
                    "P/L": pl,
                    "P/L %": pl_pct,
                })

            if not rows:
                st.info("No valid positions to display.")
            else:
                result_df = pd.DataFrame(rows)

                # Compute weights
                total_mv = result_df["MarketValue"].sum(skipna=True)
                if total_mv and total_mv > 0:
                    result_df["Weight %"] = (result_df["MarketValue"] / total_mv) * 100
                else:
                    result_df["Weight %"] = None

                # ---- Display snapshot table ----
                display_df = result_df.copy()
                for col in ["LastPrice", "MarketValue", "TotalCost", "P/L"]:
                    display_df[col] = display_df[col].map(
                        lambda x: f"{x:,.2f}" if pd.notna(x) else "–"
                    )
                display_df["P/L %"] = display_df["P/L %"].map(
                    lambda x: f"{x:.2f}%" if pd.notna(x) else "–"
                )
                display_df["Weight %"] = display_df["Weight %"].map(
                    lambda x: f"{x:.2f}%" if pd.notna(x) else "–"
                )

                st.markdown("### Portfolio snapshot")
                st.dataframe(display_df, use_container_width=True)

                if total_mv and total_mv > 0:
                    st.markdown(f"**Total market value:** {total_mv:,.2f}")

                    # Weight chart
                    weight_df = result_df[["Ticker", "MarketValue"]].dropna()
                    if not weight_df.empty:
                        weight_df["Weight %"] = (weight_df["MarketValue"] / total_mv) * 100
                        fig_w = px.bar(
                            weight_df,
                            x="Ticker",
                            y="Weight %",
                            title="Portfolio weights (%)"
                        )
                        fig_w.update_yaxes(title="Percent")
                        fig_w = apply_theme(fig_w)
                        st.plotly_chart(fig_w, use_container_width=True)
                else:
                    st.info("Total market value is zero or unavailable.")

                # ==========================
                # Performance & risk vs benchmark
                # ==========================
                st.markdown("### Portfolio performance and risk vs benchmark")

                risk_period = st.selectbox(
                    "Lookback period",
                    ["6mo", "1y", "2y", "5y"],
                    index=1,
                    key="portfolio_risk_period"
                )
                benchmark = st.session_state.get("setting_default_benchmark", "^GSPC")

                # Build price history matrix for all tickers
                price_panel = None
                for _, r in result_df.iterrows():
                    tk = r["Ticker"]
                    df = load_price_history(tk, period=risk_period, interval="1d")
                    if df.empty or "Close" not in df.columns or "Date" not in df.columns:
                        continue
                    df = df[["Date", "Close"]].copy()
                    df = df.rename(columns={"Close": tk})
                    df = df.set_index("Date")
                    if price_panel is None:
                        price_panel = df
                    else:
                        price_panel = price_panel.join(df, how="outer")

                if price_panel is None or price_panel.empty:
                    st.info("Insufficient price history to compute portfolio performance.")
                else:
                    # Align and forward-fill missing prices
                    price_panel = price_panel.sort_index().ffill().dropna(how="all")

                    # Map quantities to tickers
                    qty_map = result_df.set_index("Ticker")["Quantity"].to_dict()

                    # Compute portfolio value time series
                    for tk in list(price_panel.columns):
                        if tk not in qty_map:
                            price_panel = price_panel.drop(columns=[tk])
                    if price_panel.empty:
                        st.info("Could not align holdings with price data.")
                    else:
                        # Multiply each column by its quantity
                        for tk, qty in qty_map.items():
                            if tk in price_panel.columns:
                                price_panel[tk] = price_panel[tk] * qty

                        price_panel["PortfolioValue"] = price_panel.sum(axis=1)

                        # Benchmark prices
                        bench_df = load_price_history(benchmark, period=risk_period, interval="1d")
                        if bench_df.empty or "Close" not in bench_df.columns or "Date" not in bench_df.columns:
                            st.info("Benchmark data unavailable for performance comparison.")
                        else:
                            bench_df = bench_df[["Date", "Close"]].rename(columns={"Close": "Benchmark"})
                            bench_df = bench_df.set_index("Date").sort_index()

                            # Align portfolio and benchmark
                            merged = price_panel[["PortfolioValue"]].join(bench_df, how="inner").dropna()
                            if merged.empty:
                                st.info("Could not align portfolio and benchmark dates.")
                            else:
                                # Normalized performance index
                                merged["PortRet"] = merged["PortfolioValue"].pct_change()
                                merged["BenchRet"] = merged["Benchmark"].pct_change()
                                merged = merged.dropna()

                                if merged.empty:
                                    st.info("Not enough overlapping data to compute performance.")
                                else:
                                    merged["PortIndex"] = (1 + merged["PortRet"]).cumprod()
                                    merged["BenchIndex"] = (1 + merged["BenchRet"]).cumprod()

                                    # Performance chart
                                    fig_perf = go.Figure()
                                    fig_perf.add_trace(
                                        go.Scatter(
                                            x=merged.index,
                                            y=merged["PortIndex"],
                                            name="Portfolio"
                                        )
                                    )
                                    fig_perf.add_trace(
                                        go.Scatter(
                                            x=merged.index,
                                            y=merged["BenchIndex"],
                                            name=benchmark
                                        )
                                    )
                                    fig_perf.update_layout(
                                        title=f"Portfolio vs {benchmark} (normalized, {risk_period})"
                                    )
                                    fig_perf = apply_theme(fig_perf)
                                    st.plotly_chart(fig_perf, use_container_width=True)

                                    # Risk metrics
                                    port_vol = merged["PortRet"].std() * np.sqrt(252)
                                    bench_vol = merged["BenchRet"].std() * np.sqrt(252)
                                    corr = merged["PortRet"].corr(merged["BenchRet"])

                                    cum = (1 + merged["PortRet"]).cumprod()
                                    running_max = cum.cummax()
                                    drawdowns = cum / running_max - 1
                                    max_dd = float(drawdowns.min()) if not drawdowns.empty else None

                                    r1, r2, r3, r4 = st.columns(4)
                                    with r1:
                                        st.metric("Portfolio vol (annualized)", f"{port_vol*100:.2f}%")
                                    with r2:
                                        st.metric("Benchmark vol (annualized)", f"{bench_vol*100:.2f}%")
                                    with r3:
                                        st.metric("Correlation vs benchmark", f"{corr:.2f}")
                                    with r4:
                                        if max_dd is not None:
                                            st.metric("Portfolio max drawdown", f"{max_dd*100:.2f}%")
                                        else:
                                            st.metric("Portfolio max drawdown", "–")
