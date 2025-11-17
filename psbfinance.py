# PSP Finance — Global Market Dashboard + Portfolio Optimizer + News
# -------------------------------------------------------------------
# How to run:
#   pip install streamlit yfinance pandas numpy plotly scipy feedparser
#   streamlit run app.py

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import yfinance as yf
import feedparser
from scipy.optimize import minimize

# ---------------------- Page Config & Styling ----------------------
st.sidebar.title("PSP Finance")
page = st.sidebar.radio("Navigate", [
    "Home",
    "Dashboard",
    "Portfolio Optimizer",
    "Failed Companies",
    "Unpopular Investments",
    "Why Financial Models Fail",
    "Charts & Data",
    "Lessons for the Future",
    "News Feed",
    "Public Company Financials Lookup",
    "About"
])
if page == "Home":
    st.title("Welcome to PSP Finance")
    st.write("Explore dashboards, optimizers, company case studies, and live market data.")

# --- Custom CSS ---
st.markdown("""
<style>
:root{
  --ink:#0e1a2b; --muted:#6b7b91; --card:#f6f8fb; --accent:#0d6efd;
}
html, body, .block-container { color: var(--ink); }
h1,h2,h3 { letter-spacing: 0.2px; }
.stTextInput > div > div > input {
  border: 1.5px solid #cfd7e3; border-radius: 10px; padding: 8px 10px;
}
.stSelectbox > div > div {
  border: 1.5px solid #cfd7e3; border-radius: 10px;
}
.stButton>button {
  background: var(--accent); color: #fff; border: 0; border-radius: 10px;
  padding: 10px 18px; font-weight: 600;
}
.card {
  background: var(--card); border: 1px solid #e6ebf2; border-radius: 14px; padding: 16px 18px;
}
.kpi { font-size: 28px; font-weight: 800; margin-top: 6px; }
.kpi-note { color: var(--muted); font-size: 12px; margin-top: -4px; }
.pipe { height: 24px; width: 3px; background: var(--accent); display:inline-block; margin-right: 8px; border-radius: 2px; }
.header-hero {
  border: 1px solid #e6ebf2; background: linear-gradient(180deg,#ffffff, #f7faff);
  border-radius: 18px; padding: 22px 24px; margin-bottom: 8px;
}
.smallnote { color: var(--muted); font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar Navigation ----------------------
st.sidebar.title("PSP Finance")
page = st.sidebar.radio("Navigate", ["Dashboard", "Portfolio Optimizer", "News", "About"])

# Watchlist (persistent)
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["AAPL", "MSFT", "NVDA"]

st.sidebar.subheader("My Watchlist")
add_t = st.sidebar.text_input("Add ticker", value="")
if st.sidebar.button("Add") and add_t.strip():
    sym = add_t.strip().upper()
    if sym not in st.session_state.watchlist:
        st.session_state.watchlist.append(sym)
if st.sidebar.button("Clear Watchlist"):
    st.session_state.watchlist = []

@st.cache_data(ttl=300)
def load_prices(tickers, period="3y", interval="1d"):
    # Accept string "AAPL, MSFT" or list ["AAPL","MSFT"]
    if isinstance(tickers, str):
        tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not tickers:
        return pd.DataFrame()
    df = yf.download(tickers, period=period, interval=interval, auto_adjust=True, progress=False)
    # If multiple tickers, yfinance returns a MultiIndex; select Close level
    if isinstance(df.columns, pd.MultiIndex):
        # Safely select Close; if not present, fallback to first level
        if "Close" in df.columns.get_level_values(0):
            df = df["Close"]
        elif "Adj Close" in df.columns.get_level_values(0):
            df = df["Adj Close"]
        else:
            # unexpected structure; try to flatten
            df = df.droplevel(0, axis=1)
    return df.dropna(how="all")

# Show watchlist mini-table
if st.session_state.watchlist:
    wl_px = load_prices(st.session_state.watchlist, period="5d")
    if not wl_px.empty and len(wl_px) >= 2:
        last = wl_px.iloc[-1]
        prev = wl_px.iloc[-2]
        table = pd.DataFrame({
            "Price": last,
            "1d %": ((last/prev - 1.0) * 100.0).round(2)
        })
        st.sidebar.dataframe(table)
    elif not wl_px.empty:
        st.sidebar.info("Not enough data points for daily change yet.")

# ---------------------- Utility Functions ----------------------
def to_returns(prices, method="log"):
    if prices is None or prices.empty:
        return pd.DataFrame()
    if method == "log":
        rets = np.log(prices / prices.shift(1))
    else:
        rets = prices.pct_change()
    return rets.dropna(how="all")

def annualize_stats(returns, periods_per_year=252):
    if returns is None or returns.empty:
        return np.array([]), np.array([[]])
    mu = returns.mean() * periods_per_year
    cov = returns.cov() * periods_per_year
    return mu.values, cov.values

def portfolio_perf(weights, mu, cov, rf=0.0):
    w = np.array(weights)
    ret = float(np.dot(w, mu))
    vol = float(np.sqrt(np.dot(w, np.dot(cov, w))))
    sharpe = (ret - rf) / vol if vol > 0 else np.nan
    return ret, vol, sharpe

def solve_min_variance(mu, cov, bounds, w_sum=1.0):
    n = len(mu)
    x0 = np.repeat(1.0/n, n)
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum}]
    obj = lambda w: np.dot(w, cov @ w)
    res = minimize(obj, x0, method="SLSQP", bounds=bounds, constraints=cons)
    return res.x

def solve_max_sharpe(mu, cov, bounds, rf=0.0, w_sum=1.0):
    n = len(mu)
    x0 = np.repeat(1.0/n, n)
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum}]
    def neg_sharpe(w):
        r, v, _ = portfolio_perf(w, mu, cov, rf)
        return -(r - rf) / v if v > 0 else 1e6
    res = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds, constraints=cons)
    return res.x

def efficient_frontier(mu, cov, bounds, points=30):
    mu_vals = np.array(mu)
    tgt = np.linspace(mu_vals.min(), mu_vals.max(), points)
    rets, vols = [], []
    n = len(mu_vals)
    x0 = np.repeat(1.0/n, n)
    for tr in tgt:
        cons = [
            {'type': 'eq', 'fun': lambda w, tr=tr: np.dot(w, mu_vals) - tr},
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]
        res = minimize(lambda w: np.dot(w, cov @ w), x0, method="SLSQP", bounds=bounds, constraints=cons)
        if res.success:
            r, v, _ = portfolio_perf(res.x, mu_vals, cov)
            rets.append(r); vols.append(v)
    return np.array(rets), np.array(vols)

def kpi_card(title, value, note=""):
    st.markdown(f"""
<div class="card">
  <div><span class="pipe"></span><strong>{title}</strong></div>
  <div class="kpi">{value}</div>
  <div class="kpi-note">{note}</div>
</div>
""", unsafe_allow_html=True)

# Rolling stats
def rolling_vol(series, window=60):
    rets = series.pct_change().dropna()
    out = (rets.rolling(window).std() * np.sqrt(252)).dropna()
    return out

def rolling_beta(asset, benchmark, window=60):
    ar = asset.pct_change().dropna()
    br = benchmark.pct_change().dropna()
    idx = ar.index.intersection(br.index)
    if idx.empty:
        return pd.Series(dtype=float)
    ar, br = ar.loc[idx], br.loc[idx]
    cov = ar.rolling(window).cov(br)
    var = br.rolling(window).var()
    beta = (cov / var).dropna()
    return beta

def max_drawdown(series):
    if series.empty:
        return np.nan
    cummax = series.cummax()
    dd = (series / cummax) - 1.0
    return float(dd.min())

# ---------------------- DASHBOARD ----------------------
if page == "Dashboard":
    st.markdown("""
    <div class="header-hero">
      <h2>Global Market Intelligence</h2>
      <div class="smallnote">A research-grade dashboard for multi-asset monitoring and risk insights.</div>
    </div>
    """, unsafe_allow_html=True)

    # Preset ticker groups
    st.caption("💡 Try presets or enter your own tickers.")
    cols = st.columns(5)
    presets = {
        "US Tech": "AAPL, MSFT, NVDA, AMZN, GOOGL",
        "US Banks": "JPM, BAC, WFC, C",
        "Energy": "XOM, CVX, SLB, BP",
        "Europe": "NESN.SW, ASML.AS, SAP.DE, SIE.DE",
        "Crypto": "BTC-USD, ETH-USD"
    }
    for i, (label, tick) in enumerate(presets.items()):
        if cols[i].button(label):
            st.session_state["dash_tickers"] = tick

    raw = st.text_input("Tickers (comma-separated)", value=st.session_state.get("dash_tickers", "AAPL, MSFT, NVDA, AMZN"))
    period = st.selectbox("Period", ["6mo", "1y", "2y", "3y", "5y"], index=2)

    pxs = load_prices(raw, period=period)
    if not pxs.empty:
        norm = pxs / pxs.iloc[0] * 100
        st.line_chart(norm)
        st.download_button("Download Data", data=pxs.to_csv().encode("utf-8"), file_name="prices.csv")
    else:
        st.info("No price data found for the selected tickers/period.")

    # Rolling risk
    st.markdown("### Rolling Risk Analysis")
    try:
        t_sel = [t.strip() for t in raw.split(",") if t.strip()][0]
        bench = "SPY"
        prices_risk = load_prices([t_sel, bench], period=period)
        if prices_risk.empty or prices_risk.shape[1] < 2:
            raise ValueError("Insufficient data for risk metrics.")
        a, b = prices_risk.iloc[:, 0], prices_risk.iloc[:, 1]
        vol60 = rolling_vol(a)
        beta60 = rolling_beta(a, b)
        dd = max_drawdown(a)
        c1, c2, c3 = st.columns(3)
        c1.metric("Max Drawdown", f"{dd:.2%}" if not np.isnan(dd) else "N/A")
        c2.metric("Current 60d Vol", f"{vol60.iloc[-1]:.2%}" if len(vol60) else "N/A")
        c3.metric("Current 60d Beta vs SPY", f"{beta60.iloc[-1]:.2f}" if len(beta60) else "N/A")
        if len(vol60) and len(beta60):
            st.line_chart(pd.DataFrame({"60d Vol": vol60, "60d Beta": beta60}))
    except Exception:
        st.info("Select at least one ticker for risk metrics.")

    # Sector snapshot
    st.markdown("### Sector Snapshot (SPDR ETFs)")
    sector_map = {"SPY":"S&P 500","XLK":"Tech","XLF":"Financials","XLE":"Energy","XLY":"Consumer Discretionary","XLV":"Health Care","XLP":"Consumer Staples"}
    sec_df = load_prices(list(sector_map.keys()), period="6mo")
    if not sec_df.empty:
        perf = (sec_df.iloc[-1] / sec_df.iloc[0] - 1).sort_values(ascending=False)
        perf.index = [sector_map.get(k, k) for k in perf.index]
        fig = px.bar(perf * 100, labels={"value": "Return (%)", "index": "Sector"}, height=380)
        st.plotly_chart(fig, use_container_width=True)
    with st.expander("Methodology"):
        st.markdown("""
        - **Prices:** Yahoo Finance (adjusted close)
        - **Rolling metrics:** 60-day window, annualized volatility
        - **Beta:** covariance(asset, SPY) / variance(SPY)
        - **Drawdown:** min(Price/CumMax - 1)
        - **Sectors:** SPDR ETF family
        """)

# ---------------------- PORTFOLIO OPTIMIZER ----------------------
elif page == "Portfolio Optimizer":
    st.markdown("## Modern Portfolio Theory Optimizer")

    raw_u = st.text_input("Tickers", "AAPL, MSFT, NVDA, AMZN, JPM, XOM")
    period = st.selectbox("History period", ["1y", "2y", "3y", "5y"], 2)

    # Risk-free input with sensible bounds and format
    rf = st.number_input("Risk-free rate (annualized, e.g., 0.02 = 2%)",
                         min_value=0.0, max_value=0.10, value=0.02, step=0.005, format="%.3f")

    # Allocation bounds: ensure lb <= ub and both in [0,1]
    lb = st.number_input("Lower bound per asset weight", min_value=0.0, max_value=1.0, value=0.0, step=0.05)
    ub = st.number_input("Upper bound per asset weight", min_value=lb, max_value=1.0, value=1.0, step=0.05)

    run = st.button("Run Optimization")

    if run:
        tickers = [t.strip().upper() for t in raw_u.split(",") if t.strip()]
        prices = load_prices(tickers, period=period)
        if prices.empty:
            st.error("No price data available. Check tickers and period.")
        else:
            rets = to_returns(prices)
            if rets.empty:
                st.error("Insufficient returns data to compute statistics.")
            else:
                mu, cov = annualize_stats(rets)
                n = len(tickers)
                bounds = tuple((lb, ub) for _ in range(n))

                try:
                    w_minv = solve_min_variance(mu, cov, bounds)
                    w_msr = solve_max_sharpe(mu, cov, bounds, rf)
                    ef_ret, ef_vol = efficient_frontier(mu, cov, bounds)
                    r_m, v_m, s_m = portfolio_perf(w_msr, mu, cov, rf)

                    fig = go.Figure()
                    if len(ef_vol) and len(ef_ret):
                        fig.add_trace(go.Scatter(x=ef_vol, y=ef_ret, mode="lines", name="Frontier"))
                    fig.add_trace(go.Scatter(x=[v_m], y=[r_m], mode="markers", name=f"Max Sharpe (S={s_m:.2f})", marker=dict(size=10)))
                    fig.update_layout(xaxis_title="Volatility (σ)", yaxis_title="Return (μ)")
                    st.plotly_chart(fig, use_container_width=True)

                    st.dataframe(
                        pd.DataFrame({"Ticker": tickers,
                                      "MinVar": np.round(w_minv, 4),
                                      "MaxSharpe": np.round(w_msr, 4)}).set_index("Ticker")
                    )
                except Exception as e:
                    st.error(f"Optimization failed: {e}")

# ---------------------- NEWS ----------------------
elif page == "News":
    st.title("Finance News")
    feeds = {
        "Reuters Business": "http://feeds.reuters.com/reuters/businessNews",
        "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml"
    }
    src = st.selectbox("Source", list(feeds.keys()))
    q = st.text_input("Keyword filter", "")
    try:
        f = feedparser.parse(feeds[src])
        count = 0
        for e in f.entries:
            if count >= 15:
                break
            title = e.get("title","")
            summ = e.get("summary","")
            link = e.get("link","#")
            blob = (title + " " + summ).lower()
            if q and q.lower() not in blob:
                continue
            st.markdown(f"**[{title}]({link})**")
            st.caption(e.get("published",""))
            st.write(summ[:300] + ("..." if len(summ)>300 else ""))
            st.markdown("---")
            count += 1
        if count == 0:
            st.info("No articles matched the filter.")
    except Exception:
        st.error("Failed to load the news feed. Try another source.")

# ---------------------- ABOUT ----------------------
elif page == "About":
    st.markdown("## About PSP Finance")
    st.write("""
    This is a finance research and learning platform built to impress even the most detail-oriented professors.
    It replicates Bloomberg-style dashboards and MPT analytics.
    - **Dashboard:** multi-ticker, sectors, rolling risk, watchlist.
    - **Optimizer:** mean-variance with efficient frontier.
    - **News:** real-time feeds for global financial updates.
    """)
if page == "Failed Companies":
    st.header("Case Studies: Failed Companies")
    company = st.selectbox("Choose a company", ["Enron", "Lehman Brothers", "Wirecard"])
    st.write(f"Showing financial history for {company}...")
    # Placeholder for chart
    st.line_chart(pd.DataFrame({"Revenue":[...], "Net Income":[...]}))
if page == "Unpopular Investments":
    st.header("Unpopular Investments")
    st.write("Explore assets that lost investor confidence.")
    # Example: show chart of a failed ETF
if page == "Why Financial Models Fail":
    st.header("Why Financial Models Fail")
    st.markdown("""
    - Overfitting historical data
    - Ignoring black swan events
    - Unrealistic assumptions
    """)
if page == "Charts & Data":
    st.header("Charts & Data")
    chart_type = st.selectbox("Choose chart", [
        "Company Comparison", "Stock History", "Index Performance", "Risk/Return Scatter"
    ])
    if chart_type == "Index Performance":
        indices = load_prices(["^GSPC","^IXIC","^DJI","^FCHI","^FTSE"], period="1y")
        st.line_chart(indices / indices.iloc[0] * 100)
if page == "Lessons for the Future":
    st.header("Lessons for the Future")
    st.write("Diversification, realistic assumptions, and risk management are key.")
if page == "News Feed":
    st.header("Finance News")
    feeds = {
        "Yahoo Finance": "https://finance.yahoo.com/rss/",
        "Google News Finance": "https://news.google.com/rss/search?q=finance"
    }
    src = st.selectbox("Source", list(feeds.keys()))
    f = feedparser.parse(feeds[src])
    for e in f.entries[:10]:
        st.markdown(f"**[{e.title}]({e.link})**")
        st.caption(e.get("published",""))
        st.write(e.get("summary",""))
if page == "Public Company Financials Lookup":
    st.header("Company Financials Lookup")
    ticker = st.text_input("Enter ticker (e.g., AAPL)")
    if ticker:
        stock = yf.Ticker(ticker)
        st.subheader("Income Statement")
        st.dataframe(stock.financials.T)
        st.subheader("Balance Sheet")
        st.dataframe(stock.balance_sheet.T)
        st.subheader("Cash Flow")
        st.dataframe(stock.cashflow.T)
