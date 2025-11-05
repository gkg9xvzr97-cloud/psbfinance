# streamlit_app.py
# PSP Finance — Minimal, stable, and working version
# -------------------------------------------------
# How to run:
#   pip install streamlit yfinance pandas plotly
#   streamlit run streamlit_app.py
# (PyPDF2 and requests are optional; this build avoids fragile web calls.)

from typing import Dict, Optional
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="PSP Finance", page_icon="💹", layout="wide")

# -------------------------
# ABOUT (your provided copy)
# -------------------------
ABOUT_MD = """
## 📘 About the Project

**PSP Finance** is a student-led initiative developed in a Business & Technology class. Our mission is to make financial education clear, accessible, and practical for everyone. The platform allows users to:

- 🔍 Research public companies  
- 📊 View and download financial statements (income, balance sheet, cash flow)  
- 🧠 Explore simplified explanations of complex financial concepts  

---

## 💡 Why It Matters

As finance students, we often need multi-year financial data quickly — but searching across multiple websites is time-consuming and inefficient. **PSP Finance solves this by bringing everything into one intuitive dashboard**, complete with export buttons for instant downloads.

Whether you're studying for exams, building a report, or exploring investment ideas, PSP Finance helps you focus on learning — not searching.
"""

# -------------------------
# KNOWLEDGE LIBRARY CONTENT
# (concise, readable, no external calls)
# -------------------------
STORIES = {
    "Financial Crises — A Short Story": """
**Calm before the storm.** Credit grows, asset prices rise, and risk feels small. Leverage builds quietly. A shock hits—rates rise, defaults start, confidence breaks. Forced selling pushes prices down, losses amplify, and liquidity disappears.

**Lehman Brothers (2008).** Heavy housing exposure + short-term funding = vulnerability. When collateral lost trust and funding dried up, the firm failed. Aftermath: credit markets froze; central banks provided emergency liquidity and governments strengthened bank rules.

**Great Depression (1929–1933).** A market crash turned into a depression through bank failures, deflation, and policy mistakes. Lasting lessons: act fast in crises, protect deposits, support demand.

**How regulators respond.** More capital (to absorb losses), more liquidity (to survive funding stress), stress tests (check portfolios), and credible resolution plans (fail without taxpayer bailouts).
""",
    "Basel I → Basel III (Why it matters)": """
- **Basel I** set basic risk‑weighted capital rules: riskier assets need more equity.  
- **Basel II** refined risk weights and allowed internal models—powerful but model‑risk sensitive.  
- **Basel III** (post‑2008) added higher‑quality capital (CET1), a leverage ratio backstop, and liquidity rules (**LCR** & **NSFR**). Goal: stronger, more stable banks across countries.
""",
    "Risk Management (inspired by Hull)": """
**Market risk**: prices move—use limits, hedges (futures/options/swaps), and stress tests.  
**Credit risk**: counterparties may default—price via spreads, mitigate with collateral & netting, diversify exposures.  
**Liquidity risk**: solvent on paper, illiquid in reality—hold liquid assets, stagger maturities.  
**Operational risk**: process/control failures—culture and checks matter.

**VaR & Expected Shortfall**: quantify tail risk, but combine with scenarios and judgment.  
**Trading discipline**: small position sizes, defined exits, hedges, and post‑trade reviews.
""",
    "How to Trade — Safely for Students": """
1) Start with a thesis (what moves it and why now).  
2) Size small (risk a tiny % per trade).  
3) Hedge big risks (options/futures).  
4) Use a checklist (catalyst, valuation, risks, exit).  
5) Review results (process > outcome).
""",
}

# -------------------------
# YFINANCE HELPERS — robust to version differences
# -------------------------
@st.cache_data(ttl=60*30)
def load_financials(ticker: str) -> Dict[str, pd.DataFrame]:
    import yfinance as yf
    t = yf.Ticker(ticker)

    # Try both old and new attribute names
    income = getattr(t, 'financials', pd.DataFrame())
    if income.empty:
        income = getattr(t, 'income_stmt', pd.DataFrame())
    balance = getattr(t, 'balance_sheet', pd.DataFrame())
    cash = getattr(t, 'cashflow', pd.DataFrame())

    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        # Columns are dates; keep last up to 10 annual periods
        cols = []
        for c in df.columns:
            try:
                year = int(str(c)[:4])
            except Exception:
                year = str(c)
            cols.append(year)
        out = df.copy()
        out.columns = cols
        # Sort ascending and limit to 10 most recent
        out = out.reindex(sorted(out.columns), axis=1)
        if out.shape[1] > 10:
            out = out.iloc[:, -10:]
        out.index.name = "Line Item"
        return out

    return {
        'income': normalize(income),
        'balance': normalize(balance),
        'cashflow': normalize(cash)
    }

@st.cache_data(ttl=60*30)
def load_history(tickers: list, period: str = "5y") -> pd.DataFrame:
    import yfinance as yf
    if not tickers:
        return pd.DataFrame()
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data = data['Close']
    return data

# -------------------------
# UI
# -------------------------
TAB_HOME, TAB_KNOW, TAB_RESEARCH, TAB_AI = st.tabs([
    "🏠 Home",
    "📚 Knowledge Library",
    "🔎 Research",
    "📅 Historical Performance & 🧠 Insights",
])

# HOME
with TAB_HOME:
    st.markdown(ABOUT_MD)

# KNOWLEDGE
with TAB_KNOW:
    st.subheader("Knowledge Library — Story‑based, short, and clear")
    topic = st.selectbox("Topic", list(STORIES.keys()))
    st.write(STORIES[topic])

# RESEARCH
with TAB_RESEARCH:
    st.subheader("Company Research & Financials")
    ticker = st.text_input("Enter a public ticker (e.g., AAPL, MSFT, NESN.SW)", value="AAPL").strip()
    if ticker:
        fin = load_financials(ticker)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Income Statement (annual)**")
            if fin['income'].empty:
                st.info("Income statement not available from Yahoo Finance for this ticker.")
            else:
                st.dataframe(fin['income'], use_container_width=True)
                st.download_button("Download Income (CSV)", fin['income'].to_csv().encode('utf-8'), file_name=f"{ticker}_income.csv")
        with col2:
            st.markdown("**Balance Sheet (annual)**")
            if fin['balance'].empty:
                st.info("Balance sheet not available from Yahoo Finance for this ticker.")
            else:
                st.dataframe(fin['balance'], use_container_width=True)
                st.download_button("Download Balance (CSV)", fin['balance'].to_csv().encode('utf-8'), file_name=f"{ticker}_balance.csv")

        st.markdown("**Cash Flow (annual)**")
        if fin['cashflow'].empty:
            st.info("Cash flow not available from Yahoo Finance for this ticker.")
        else:
            st.dataframe(fin['cashflow'], use_container_width=True)
            st.download_button("Download Cash Flow (CSV)", fin['cashflow'].to_csv().encode('utf-8'), file_name=f"{ticker}_cashflow.csv")

# AI / PORTFOLIOS
with TAB_AI:
    st.subheader("📅 Historical Performance Charts & 🧠 Insights")
    raw = st.text_input("Tickers (comma‑separated)", value="AAPL, MSFT, NVDA").strip()
    tickers = [t.strip().upper() for t in raw.split(',') if t.strip()]

    hist = load_history(tickers, period="5y")
    if hist.empty:
        st.info("No price data returned. Try different tickers.")
    else:
        norm = hist / hist.iloc[0] * 100
        fig = px.line(norm, title="Normalized 5‑Year Performance (100 = start)")
        st.plotly_chart(fig, use_container_width=True)

        # Simple stats
        last = norm.iloc[-1].sort_values(ascending=False)
        best = last.index[0]
        worst = last.index[-1]
        st.markdown("### 🧠 Insight Summary")
        st.write(f"Top performer over the period: **{best}**. Lagging performer: **{worst}**. ")
        # Volatility proxy (stdev of daily % changes)
        ret = hist.pct_change().dropna()
        vol = ret.std().sort_values()
        st.write(f"Lower historical volatility among inputs: **{vol.index[0]}**. Higher volatility: **{vol.index[-1]}**. ")
        st.caption("These are simplified, educational insights — not investment advice.")

st.divider()
st.caption("PSP Finance — Minimal working build. Data from Yahoo Finance (yfinance). Not investment advice.")
