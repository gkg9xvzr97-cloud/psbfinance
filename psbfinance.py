# PSP Finance — Global Market Dashboard + Portfolio Optimizer
# Clean, guided, and academically rigorous.
# -----------------------------------------------------------
# How to run:
#   pip install -r requirements.txt
#   streamlit run app.py

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import streamlit as st
import yfinance as yf
from scipy.optimize import minimize

# ---------------------- Page Config & Styling ----------------------
st.set_page_config(page_title="PSP Finance — Dashboard & Optimizer", layout="wide")

# Subtle professional CSS
st.markdown("""
<style>
:root{
  --ink:#0e1a2b; --muted:#6b7b91; --card:#f6f8fb; --accent:#0d6efd; --accent-2:#204080;
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
  background: var(--card); border: 1px solid #e6ebf2; border-radius: 14px; padding: 16px 18px; height: 100%;
}
.kpi { font-size: 28px; font-weight: 800; margin-top: 6px; }
.kpi-note { color: var(--muted); font-size: 12px; margin-top: -4px; }
.pipe { height: 24px; width: 3px; background: var(--accent); display:inline-block; margin-right: 8px; border-radius: 2px; }
.header-hero {
  border: 1px solid #e6ebf2; background: linear-gradient(180deg,#ffffff, #f7faff);
  border-radius: 18px; padding: 22px 24px; margin-bottom: 8px;
}
.smallnote { color: var(--muted); font-size: 13px; }
hr { border-color: #e8eef6; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar Navigation ----------------------
st.sidebar.title("PSP Finance")
page = st.sidebar.radio("Navigate", ["Dashboard", "Portfolio Optimizer", "About"])

with st.sidebar.expander("How to use", expanded=True):
    st.markdown("""
**Dashboard**
1) Type tickers in the search bar, e.g. `AAPL, MSFT, NVDA`.
2) Review normalized performance, index KPIs, and sector returns.

**Portfolio Optimizer**
1) Enter tickers and choose history period.
2) Set bounds and risk-free rate.
3) Click **Run Optimization** to see the efficient frontier, Min-Var, and Max-Sharpe portfolios.
4) Optional: upload your current weights (CSV: `Ticker,Weight`) to compare.
    """)

# ---------------------- Helpers & Cache ----------------------
@st.cache_data(ttl=300)
def load_prices(tickers, period="3y", interval="1d"):
    """Download adjusted close prices for tickers."""
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
    mu = returns.mean() * periods_per_year         # annualized expected returns
    cov = returns.cov() * periods_per_year         # annualized covariance
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
    cons = [{'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum}]
    obj = lambda w: np.dot(w, cov @ w)  # variance
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

def efficient_frontier(mu, cov, bounds, points=31, w_sum=1.0):
    """Target-return frontier via variance minimization."""
    mu_values = np.array(mu)
    tgt = np.linspace(mu_values.min(), mu_values.max(), points)
    rets, vols = [], []
    n = len(mu_values)
    x0 = np.repeat(1.0/n, n)
    for tr in tgt:
        cons = [
            {'type': 'eq', 'fun': lambda w, tr=tr: np.dot(w, mu_values) - tr},
            {'type': 'eq', 'fun': lambda w: np.sum(w) - w_sum},
        ]
        res = minimize(lambda w: np.dot(w, cov @ w), x0, method="SLSQP", bounds=bounds, constraints=cons)
        if res.success:
            r, v, _ = portfolio_perf(res.x, mu_values, cov, rf=0.0)
            rets.append(r); vols.append(v)
    return np.array(rets), np.array(vols)

def kpi_card(title: str, value: str, note: str = ""):
    st.markdown(f"""
    <div class="card">
      <div><span class="pipe"></span><strong>{title}</strong></div>
      <div class="kpi">{value}</div>
      <div class="kpi-note">{note}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------- PAGE: Dashboard ----------------------
if page == "Dashboard":
    st.markdown("""
    <div class="header-hero">
      <h2 style="margin:0;">Global Market Intelligence</h2>
      <div class="smallnote">A professional overview of indices, equities, sectors, and trends — built for academic and investment analysis.</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI row: S&P 500, NASDAQ, Dow, Bitcoin
    idx_map = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI", "Bitcoin": "BTC-USD"}
    c1, c2, c3, c4 = st.columns(4)
    for i, (name, sym) in enumerate(idx_map.items()):
        prices = load_prices(sym, period="5d")
        if prices.empty:
            continue
        latest = float(prices.iloc[-1, 0])
        prev = float(prices.iloc[-2, 0]) if len(prices) > 1 else np.nan
        chg = ((latest/prev)-1)*100 if prev and not np.isnan(prev) else np.nan
        block = [c1, c2, c3, c4][i]
        with block:
            kpi_card(name, f"{latest:,.2f}", f"1-day change: {chg:+.2f}%")

    st.markdown("### Multi-Ticker Normalized Performance")
    raw = st.text_input(
        "Search or compare (examples: AAPL, MSFT, NVDA, AMZN, XOM, JPM, GOOGL, META)",
        value="AAPL, MSFT, NVDA, AMZN",
        help="Type symbols separated by commas."
    )
    period = st.selectbox("Period", ["6mo", "1y", "2y", "3y", "5y"], index=2, key="dash_period")
    if raw:
        pxs = load_prices(raw, period=period)
        if not pxs.empty:
            norm = pxs / pxs.iloc[0] * 100.0
            st.line_chart(norm)
        else:
            st.info("No price data returned for the chosen inputs.")

    st.markdown("### Sector Snapshot (SPDR ETFs)")
    sector_map = {
        "SPY (Market)": "SPY", "XLK (Tech)": "XLK", "XLF (Financials)": "XLF",
        "XLE (Energy)": "XLE", "XLY (Cons. Discr.)": "XLY", "XLV (Health)": "XLV",
        "XLP (Cons. Staples)": "XLP", "XLI (Industrials)": "XLI", "XLU (Utilities)": "XLU"
    }
    sec_df = load_prices(list(sector_map.values()), period="6mo")
    if not sec_df.empty:
        perf = (sec_df.iloc[-1] / sec_df.iloc[0] - 1).sort_values(ascending=False)
        perf = perf.rename(index={v: k for k, v in sector_map.items()})
        fig = px.bar(perf * 100, labels={"value": "Return (%)", "index": "Sector"}, height=380)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown(
        "<div class='smallnote'>Tip: Use the Optimizer page to convert views into weights, "
        "compare Min-Variance vs Max-Sharpe, and justify allocations quantitatively.</div>",
        unsafe_allow_html=True
    )

# ---------------------- PAGE: Portfolio Optimizer ----------------------
elif page == "Portfolio Optimizer":
    st.markdown("""
    <div class="header-hero">
      <h2 style="margin:0;">Modern Portfolio Theory Optimizer</h2>
      <div class="smallnote">Long-only mean–variance optimization with efficient frontier, min-variance, and max-Sharpe solutions.</div>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Universe & Settings")
        default_universe = "AAPL, MSFT, NVDA, AMZN, JPM, XOM, UNH, JNJ"
        raw_u = st.text_input("Tickers (comma-separated)", value=default_universe)
        period = st.selectbox("History period", ["1y", "2y", "3y", "5y"], index=2)
        ret_type = st.selectbox("Return type", ["log", "simple"], index=0)
        rf = st.number_input("Risk-free rate (annual, decimal)", value=0.02, step=0.005, format="%.3f")
        lb = st.number_input("Weight lower bound", value=0.00, step=0.05, format="%.2f")
        ub = st.number_input("Weight upper bound", value=1.00, step=0.05, format="%.2f")
        points = st.slider("Frontier density", min_value=15, max_value=60, value=31, step=3)

        st.markdown("Upload current weights (optional) — CSV columns: `Ticker,Weight`")
        up = st.file_uploader("Upload weights CSV", type="csv")
        current_w = None
        if up is not None:
            dfw = pd.read_csv(up)
            dfw["Ticker"] = dfw["Ticker"].str.upper()
            tickers_u = [t.strip().upper() for t in raw_u.split(",") if t.strip()]
            weights = []
            for t in tickers_u:
                row = dfw[dfw["Ticker"] == t]
                weights.append(float(row["Weight"].iloc[0]) if not row.empty else 0.0)
            s = sum(weights)
            if s > 0:
                current_w = np.array(weights) / s

        run = st.button("Run Optimization")

    with right:
        st.subheader("Methodology")
        st.markdown("""
- Prices from Yahoo Finance (adjusted close).
- Annualization: mean and covariance × 252.
- Optimization: SLSQP with equality ∑w=1 and bounds.
- Outputs: Min-Variance, Max-Sharpe, and the efficient frontier.
        """)
        st.markdown("<div class='smallnote'>Interpretation: Min-Var targets the lowest volatility; Max-Sharpe maximizes excess return per unit of risk.</div>", unsafe_allow_html=True)

    if run:
        tickers = [t.strip().upper() for t in raw_u.split(",") if t.strip()]
        prices = load_prices(tickers, period=period)
        if prices.empty or prices.shape[1] < 2:
            st.error("Not enough price data. Try different tickers or a longer period.")
        else:
            rets = to_returns(prices, method=ret_type)
            mu, cov = annualize_stats(rets)
            bounds = tuple((lb, ub) for _ in tickers)

            # Optimize
            w_minv = solve_min_variance(mu.values, cov.values, bounds=bounds, rf=rf)
            w_msr  = solve_max_sharpe(mu.values, cov.values, bounds=bounds, rf=rf)

            r_minv, v_minv, s_minv = portfolio_perf(w_minv, mu.values, cov.values, rf=rf)
            r_msr,  v_msr,  s_msr  = portfolio_perf(w_msr,  mu.values, cov.values, rf=rf)

            # Frontier
            ef_ret, ef_vol = efficient_frontier(mu.values, cov.values, bounds=bounds, points=points)

            # Plots
            st.subheader("Efficient Frontier")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ef_vol, y=ef_ret, mode="lines", name="Frontier"))
            fig.add_trace(go.Scatter(x=[v_minv], y=[r_minv], mode="markers", name="Min-Var", marker=dict(size=10)))
            fig.add_trace(go.Scatter(x=[v_msr], y=[r_msr], mode="markers", name="Max-Sharpe", marker=dict(size=10)))
            if current_w is not None:
                rc, vc, sc = portfolio_perf(current_w, mu.values, cov.values, rf=rf)
                fig.add_trace(go.Scatter(x=[vc], y=[rc], mode="markers", name="Current", marker=dict(size=10)))
            fig.update_layout(xaxis_title="Volatility (annualized)", yaxis_title="Return (annualized)")
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Optimal Weights")
            out = pd.DataFrame({
                "Ticker": tickers,
                "Min-Variance": np.round(w_minv, 4),
                "Max-Sharpe":   np.round(w_msr, 4)
            })
            if current_w is not None:
                out["Current"] = np.round(current_w, 4)
            st.dataframe(out.set_index("Ticker"))

            csv = out.to_csv(index=False).encode("utf-8")
            st.download_button("Download weights (CSV)", data=csv, file_name="optimal_weights.csv", mime="text/csv")

            st.subheader("Summary Metrics")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("**Min-Variance**")
                st.write(f"Return: {r_minv:.2%}")
                st.write(f"Volatility: {v_minv:.2%}")
                st.write(f"Sharpe: {s_minv:.2f}")
            with c2:
                st.markdown("**Max-Sharpe**")
                st.write(f"Return: {r_msr:.2%}")
                st.write(f"Volatility: {v_msr:.2%}")
                st.write(f"Sharpe: {s_msr:.2f}")
            if current_w is not None:
                with c3:
                    st.markdown("**Current**")
                    st.write(f"Return: {rc:.2%}")
                    st.write(f"Volatility: {vc:.2%}")
                    st.write(f"Sharpe: {sc:.2f}")

            st.subheader("Correlation Heatmap")
            corr = rets.corr()
            figc = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", origin="lower", height=520)
            st.plotly_chart(figc, use_container_width=True)

            st.markdown("---")
            st.markdown(
                "<div class='smallnote'>Use cases in class: discuss trade-offs along the frontier, "
                "effect of bounds, and how the risk-free rate shifts Max-Sharpe.</div>",
                unsafe_allow_html=True
            )

# ---------------------- PAGE: About ----------------------
elif page == "About":
    st.markdown("""
    <div class="header-hero">
      <h2 style="margin:0;">About this Project</h2>
      <div class="smallnote">This app blends a Bloomberg-style market dashboard with a Modern Portfolio Theory optimizer.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
**Design goals**
- Appealing to a finance professor: clean structure, correct methodology, and clear interpretation.
- Professional UX: guided inputs, KPIs, sector lens, and publishable charts.
- Academic rigor: transparent assumptions (annualization, constraints, objective functions).

**Suggested extensions**
- Factor models (Fama-French 3/5), rolling beta and volatility.
- Transaction costs and turnover penalties.
- Sector and single-name concentration caps.
- Benchmark comparison and out-of-sample backtests.
    """)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center; color:#6b7b91'>PSP Finance — Global Market Intelligence & Portfolio Optimization</div>",
        unsafe_allow_html=True
    )
