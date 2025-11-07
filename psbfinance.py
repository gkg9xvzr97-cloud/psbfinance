import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import yfinance as yf
from scipy.optimize import minimize

# ---------------------- Page & Sidebar ----------------------
st.set_page_config(page_title="Market Dashboard + Portfolio Optimizer", layout="wide")

st.sidebar.title("Navigate")
page = st.sidebar.radio("Go to", ["Dashboard", "Portfolio Optimizer", "About"])

# ---------------------- Helpers & Cache ----------------------
@st.cache_data(ttl=300)
def load_prices(tickers, period="3y", interval="1d"):
    if isinstance(tickers, str):
        tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not tickers:
        return pd.DataFrame()
    df = yf.download(tickers, period=period, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    return df.dropna(how="all")

def to_returns(prices: pd.DataFrame, method="log"):
    prices = prices.dropna()
    if method == "log":
        rets = np.log(prices / prices.shift(1))
    else:
        rets = prices.pct_change()
    return rets.dropna()

def annualize_stats(returns: pd.DataFrame, periods_per_year=252):
    mu = returns.mean() * periods_per_year
    cov = returns.cov() * periods_per_year
    return mu, cov

def portfolio_perf(weights, mu, cov, rf=0.0):
    w = np.array(weights)
    ret = float(np.dot(w, mu))
    vol = float(np.sqrt(np.dot(w, np.dot(cov, w))))
    sharpe = (ret - rf) / vol if vol > 0 else np.nan
    return ret, vol, sharpe

def solve_min_variance(mu, cov, bounds, rf=0.0, w_sum=1.0):
    n = len(mu)
    x0 = np.repeat(1.0/n, n)
    cons = (
        {'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum},
    )
    res = minimize(lambda w: np.dot(w, cov @ w), x0, method="SLSQP", bounds=bounds, constraints=cons)
    return res.x

def solve_max_sharpe(mu, cov, bounds, rf=0.0, w_sum=1.0):
    n = len(mu)
    x0 = np.repeat(1.0/n, n)
    cons = (
        {'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum},
    )
    def neg_sharpe(w):
        ret, vol, _ = portfolio_perf(w, mu, cov, rf)
        return -(ret - rf) / vol if vol > 0 else 1e6
    res = minimize(neg_sharpe, x0, method="SLSQP", bounds=bounds, constraints=cons)
    return res.x

def efficient_frontier(mu, cov, bounds, points=30, w_sum=1.0):
    # target-return frontier using SLSQP
    n = len(mu)
    target_rets = np.linspace(mu.min(), mu.max(), points)
    vols = []
    rets = []
    for tr in target_rets:
        x0 = np.repeat(1.0/n, n)
        cons = (
            {'type': 'eq', 'fun': lambda w, tr=tr: np.dot(w, mu) - tr},
            {'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum},
        )
        res = minimize(lambda w: np.dot(w, cov @ w), x0, method="SLSQP", bounds=bounds, constraints=cons)
        if res.success:
            r, v, _ = portfolio_perf(res.x, mu, cov)
            rets.append(r); vols.append(v)
    return np.array(rets), np.array(vols)

def format_kpi(title, value, suffix="", helptext=None):
    with st.container():
        st.markdown(f"**{title}**")
        st.markdown(f"<h3 style='margin-top:-8px'>{value}{suffix}</h3>", unsafe_allow_html=True)
        if helptext:
            st.caption(helptext)

# ---------------------- PAGE: Dashboard ----------------------
if page == "Dashboard":
    st.title("Global Market Intelligence")
    st.caption("Indices, FX, crypto, sectors, and multi-ticker performance — powered by Yahoo Finance.")

    colA, colB, colC, colD = st.columns(4)
    indices = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI", "Bitcoin": "BTC-USD"}
    # Fetch last 5 sessions to compute 1d change
    for idx, (label, sym) in enumerate(indices.items()):
        df = load_prices([sym], period="5d")
        if df.empty:
            continue
        price = df.iloc[-1, 0]
        prev = df.iloc[-2, 0] if len(df) > 1 else np.nan
        chg = (price/prev - 1)*100 if prev and not np.isnan(prev) else np.nan
        block = [colA, colB, colC, colD][idx]
        with block:
            format_kpi(label, f"{price:,.2f}", "", f"1D: {chg:+.2f}%")

    st.markdown("---")

    st.subheader("Multi-Ticker Normalized Chart")
    default = "AAPL, MSFT, NVDA, GOOGL"
    raw = st.text_input("Enter tickers (comma-separated)", value=default, key="dash_tickers")
    period = st.selectbox("Period", ["6mo", "1y", "2y", "3y", "5y"], index=2, key="dash_period")
    if raw:
        prices = load_prices(raw, period=period)
        if not prices.empty:
            norm = prices / prices.iloc[0] * 100
            st.line_chart(norm)
        else:
            st.info("No price data returned.")

    st.markdown("---")

    st.subheader("Sectors (SPDR)")
    sector_map = {
        "SPY (Market)": "SPY", "XLK (Tech)": "XLK", "XLF (Financials)": "XLF",
        "XLE (Energy)": "XLE", "XLY (Cons. Discr.)": "XLY", "XLV (Health)": "XLV",
        "XLP (Cons. Staples)": "XLP", "XLI (Industrials)": "XLI", "XLU (Utilities)": "XLU"
    }
    sec_prices = load_prices(list(sector_map.values()), period="6mo")
    if not sec_prices.empty:
        perf = (sec_prices.iloc[-1] / sec_prices.iloc[0] - 1).sort_values(ascending=False)
        perf = perf.rename(index={v: k for k, v in sector_map.items()})
        fig = px.bar(perf * 100, labels={"value": "Return %", "index": "Sector"})
        st.plotly_chart(fig, use_container_width=True)

# ---------------------- PAGE: Portfolio Optimizer ----------------------
elif page == "Portfolio Optimizer":
    st.title("Portfolio Optimizer — Efficient Frontier, Min-Variance, Max-Sharpe")
    st.caption("Long-only mean–variance optimization using daily data from Yahoo Finance.")

    left, right = st.columns([1.2, 1])

    with left:
        st.subheader("Universe")
        default = "AAPL, MSFT, NVDA, AMZN, JPM, XOM, UNH, JNJ"
        raw = st.text_input("Tickers (comma-separated)", value=default)
        period = st.selectbox("History period", ["1y", "2y", "3y", "5y"], index=2)
        freq = st.selectbox("Return type", ["log", "simple"], index=0)
        rf = st.number_input("Risk-free rate (annual, as decimal)", value=0.02, step=0.005, format="%.3f")
        lb = st.number_input("Weight lower bound", value=0.0, step=0.05, format="%.2f")
        ub = st.number_input("Weight upper bound", value=1.0, step=0.05, format="%.2f")
        points = st.slider("Frontier points", min_value=10, max_value=60, value=30, step=5)

        uploaded = st.file_uploader("Optional: upload current portfolio CSV with columns: Ticker,Weight", type=["csv"])
        current_w = None
        if uploaded is not None:
            dfw = pd.read_csv(uploaded)
            dfw["Ticker"] = dfw["Ticker"].str.upper()
            # align to input universe
            tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
            weights = []
            for t in tickers:
                row = dfw[dfw["Ticker"] == t]
                weights.append(float(row["Weight"].iloc[0]) if not row.empty else 0.0)
            s = sum(weights)
            if s > 0:
                current_w = np.array(weights) / s

        run = st.button("Run Optimization")

    with right:
        st.subheader("Notes")
        st.write(
            "This optimizer uses daily close prices, computes annualized mean and covariance, "
            "and solves constrained SLSQP problems for min-variance and max-Sharpe portfolios."
        )
        st.write("Constraints: long-only by default, sum of weights equals 1. Adjust bounds to allow concentration limits.")

    if run:
        tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
        prices = load_prices(tickers, period=period)
        if prices.empty or prices.shape[1] < 2:
            st.error("Not enough price data. Try different tickers/period.")
        else:
            rets = to_returns(prices, method=freq)
            mu, cov = annualize_stats(rets)
            bounds = tuple((lb, ub) for _ in tickers)

            w_minv = solve_min_variance(mu.values, cov.values, bounds=bounds, rf=rf)
            w_msr  = solve_max_sharpe(mu.values, cov.values, bounds=bounds, rf=rf)
            r_minv, v_minv, s_minv = portfolio_perf(w_minv, mu.values, cov.values, rf=rf)
            r_msr,  v_msr,  s_msr  = portfolio_perf(w_msr,  mu.values, cov.values, rf=rf)

            ef_ret, ef_vol = efficient_frontier(mu.values, cov.values, bounds=bounds, points=points)

            st.markdown("### Efficient Frontier")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ef_vol, y=ef_ret, mode="lines", name="Frontier"))
            fig.add_trace(go.Scatter(x=[v_minv], y=[r_minv], mode="markers", name="Min-Var", marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=[v_msr], y=[r_msr], mode="markers", name="Max-Sharpe", marker=dict(size=10)))
            if current_w is not None:
                rc, vc, sc = portfolio_perf(current_w, mu.values, cov.values, rf=rf)
                fig.add_trace(go.Scatter(x=[vc], y=[rc], mode="markers", name="Current", marker=dict(size=10)))
            fig.update_layout(xaxis_title="Volatility (annualized)", yaxis_title="Return (annualized)")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Optimal Weights")
            dfw = pd.DataFrame({
                "Ticker": tickers,
                "Min-Variance": np.round(w_minv, 4),
                "Max-Sharpe":   np.round(w_msr, 4)
            })
            if current_w is not None:
                dfw["Current"] = np.round(current_w, 4)
            st.dataframe(dfw.set_index("Ticker"))

            st.markdown("### Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write("Min-Variance")
                st.write(f"Return: {r_minv:.2%}")
                st.write(f"Volatility: {v_minv:.2%}")
                st.write(f"Sharpe: {s_minv:.2f}")
            with col2:
                st.write("Max-Sharpe")
                st.write(f"Return: {r_msr:.2%}")
                st.write(f"Volatility: {v_msr:.2%}")
                st.write(f"Sharpe: {s_msr:.2f}")
            if current_w is not None:
                with col3:
                    st.write("Current")
                    st.write(f"Return: {rc:.2%}")
                    st.write(f"Volatility: {vc:.2%}")
                    st.write(f"Sharpe: {sc:.2f}")

            st.markdown("### Correlation Heatmap")
            corr = rets.corr()
            figc = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", origin="lower")
            st.plotly_chart(figc, use_container_width=True)

# ---------------------- PAGE: About ----------------------
elif page == "About":
    st.title("About this Project")
    st.write(
        "This app blends a Bloomberg-style market dashboard with a Modern Portfolio Theory optimizer. "
        "It’s designed for academic evaluation: clear data sourcing (Yahoo Finance), transparent math (mean–variance), "
        "and professional visualization (Plotly/Streamlit)."
    )
    st.write(
        "Extend it by adding: factor models (Fama-French), rolling risk metrics, transaction costs, shorting constraints, "
        "and portfolio backtests against benchmarks."
    )
