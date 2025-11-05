# streamlit_app.py
# PSP Finance — Redesigned: clear English, built‑in knowledge library, reliable research (with tickers), easy downloads
# Run locally:
#   pip install streamlit yfinance pandas requests plotly PyPDF2
#   streamlit run streamlit_app.py

import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PyPDF2 import PdfReader

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="PSP Finance",
    page_icon="💹",
    layout="wide",
)

# -------------------------------------------------
# SMALL, RELIABLE TICKER LOOKUP (no SEC dependency)
# -------------------------------------------------
# A compact, curated mapping for quick name→ticker search.
# You can expand this list or load a CSV later.
TICKER_MAP = pd.DataFrame([
    {"name":"Apple Inc.", "ticker":"AAPL", "exchange":"NASDAQ"},
    {"name":"Microsoft Corporation", "ticker":"MSFT", "exchange":"NASDAQ"},
    {"name":"Amazon.com, Inc.", "ticker":"AMZN", "exchange":"NASDAQ"},
    {"name":"Alphabet Inc. (Google) Class A", "ticker":"GOOGL", "exchange":"NASDAQ"},
    {"name":"Meta Platforms, Inc.", "ticker":"META", "exchange":"NASDAQ"},
    {"name":"NVIDIA Corporation", "ticker":"NVDA", "exchange":"NASDAQ"},
    {"name":"Tesla, Inc.", "ticker":"TSLA", "exchange":"NASDAQ"},
    {"name":"JPMorgan Chase & Co.", "ticker":"JPM", "exchange":"NYSE"},
    {"name":"Bank of America Corporation", "ticker":"BAC", "exchange":"NYSE"},
    {"name":"Walmart Inc.", "ticker":"WMT", "exchange":"NYSE"},
    {"name":"The Coca-Cola Company", "ticker":"KO", "exchange":"NYSE"},
    {"name":"PepsiCo, Inc.", "ticker":"PEP", "exchange":"NASDAQ"},
    {"name":"Netflix, Inc.", "ticker":"NFLX", "exchange":"NASDAQ"},
    {"name":"Nestlé S.A.", "ticker":"NESN.SW", "exchange":"SIX"},
    {"name":"LVMH Moët Hennessy Louis Vuitton", "ticker":"MC.PA", "exchange":"EPA"},
    {"name":"TotalEnergies SE", "ticker":"TTE.PA", "exchange":"EPA"},
    {"name":"Kering", "ticker":"KER.PA", "exchange":"EPA"},
    {"name":"Sanofi", "ticker":"SAN.PA", "exchange":"EPA"},
    {"name":"KPMG (private)", "ticker":"—", "exchange":"—"},
])

# -------------------------------------------------
# IMAGE BANNERS
# -------------------------------------------------
HERO_URL = "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?q=80&w=1200&auto=format&fit=crop"
SIDEBAR_URL = "https://images.unsplash.com/photo-1553729784-e91953dec042?q=80&w=1200&auto=format&fit=crop"

# -------------------------------------------------
# HELPERS
# -------------------------------------------------
@st.cache_data(ttl=60 * 60)
def wikipedia_summary(company_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (summary, image_url) from Wikipedia REST API if available."""
    try:
        search = requests.get(
            f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={company_name}&limit=1"
        ).json()
        if not search.get("pages"):
            return None, None
        page = search["pages"][0]
        summary = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{page.get('title')}"
        ).json()
        desc = summary.get("extract")
        img = None
        if summary.get("thumbnail"):
            img = summary["thumbnail"].get("source")
        return desc, img
    except Exception:
        return None, None

@st.cache_data(ttl=60 * 60)
def yf_load_financials(ticker: str) -> Dict[str, pd.DataFrame]:
    """Load annual statements via yfinance. Availability depends on the exchange and Yahoo Finance."""
    import yfinance as yf
    t = yf.Ticker(ticker)
    income = t.income_stmt
    balance = t.balance_sheet
    cash = t.cashflow

    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        cols = []
        for c in df.columns:
            try:
                year = pd.to_datetime(c).year
            except Exception:
                try:
                    year = int(str(c)[:4])
                except Exception:
                    year = str(c)
            cols.append(year)
        df2 = df.copy()
        df2.columns = cols
        df2 = df2.reindex(sorted(df2.columns), axis=1)
        # keep up to 10 most recent years if available
        if len(df2.columns) > 10:
            df2 = df2.iloc[:, -10:]
        return df2

    return {"income": normalize(income), "balance": normalize(balance), "cashflow": normalize(cash)}

@st.cache_data(ttl=60 * 60)
def parse_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            pass
    return "\n".join(texts)

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.image(SIDEBAR_URL, caption="Finance • Analysis • Learning", use_column_width=True)

st.sidebar.title("PSP Finance")
st.sidebar.caption("A student-built hub for researching companies, downloading financials, and learning core finance.")

# Quick search box (name or ticker)
q = st.sidebar.text_input("Search company (name or ticker)", value="Apple")

# -------------------------------------------------
# HEADER
# -------------------------------------------------
col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("<h1 style='margin-bottom:0'>PSP Finance</h1>", unsafe_allow_html=True)
    st.write("Built for students: simple research, fast downloads, and a readable knowledge library.")
with col2:
    st.image(HERO_URL, use_column_width=True)

st.divider()

# -------------------------------------------------
# TABS
# -------------------------------------------------
TAB_HOME, TAB_KNOW, TAB_RESEARCH, TAB_MATERIALS = st.tabs([
    "🏠 Home",
    "📚 Knowledge Library",
    "🔎 Research",
    "📦 Materials & Templates",
])

# -------------------------------------------------
# HOME
# -------------------------------------------------
with TAB_HOME:
    st.subheader("About the Project")
    st.write(
        """
        **PSP Finance** is a student project from a Business & Tech class. Our mission is to make financial learning **clear** and **practical**. 
        You can research companies, download income statements, balance sheets, and cash flows, and read approachable explanations of big finance ideas.
        """
    )
    st.markdown(
        """
        **Why this matters**  
        As finance students, we often need multi‑year statements fast. Hunting across websites is slow. PSP Finance brings it into one friendly dashboard with export buttons.
        """
    )
    st.info("Tip: Use the **Research** tab for company overviews & financials. The **Knowledge Library** tells the story behind the numbers.")

# -------------------------------------------------
# KNOWLEDGE LIBRARY (original summaries & stories)
# -------------------------------------------------
STORIES = {
    "The Story of Financial Crises": """
**What causes financial crises?**  
Crises usually grow in calm times. Credit expands, asset prices rise, and risk feels small. Banks lend more, investors accept weaker protections, and leverage quietly builds. Then a shock hits—rates rise, defaults climb, or confidence breaks—and balance sheets that looked fine suddenly look fragile. When many institutions try to sell at once, prices fall, losses amplify, and liquidity disappears.

**Lehman Brothers (2008)**  
Lehman was deeply exposed to U.S. housing. When mortgage values dropped and funding dried up, its collateral wasn’t trusted and counterparties stepped back. With no buyer and no government backstop, Lehman filed for bankruptcy in September 2008. The immediate aftermath was a global dash for cash: money‑market funds broke the buck, interbank lending froze, and central banks opened emergency facilities to replace vanished private liquidity.

**The Great Depression (1929–1933)**  
A stock‑market boom ended in a crash. Bank failures, falling prices (deflation), and policy mistakes turned a recession into a depression. One lasting lesson: in a panic, policy must act quickly to stabilize banks, support demand, and restore confidence. Deposit insurance, lender‑of‑last‑resort lending, and automatic stabilizers are all responses to that era.

**How regulators try to prevent repeats**  
- **Capital**: Banks must fund themselves with enough equity to absorb losses.  
- **Liquidity**: They must hold cash‑like assets to survive funding stress.  
- **Stress tests**: Portfolios are tested against severe scenarios.  
- **Resolution**: Plans for how a failing bank can be wound down without taxpayer bailouts.
""",
    "From Basel I to Basel III (and why it matters)": """
**Basel I (late 1980s)** introduced simple risk‑weighted capital rules: riskier assets required more capital. It was a huge step forward—common definitions and a floor for resilience across countries.

**Basel II** refined risk weights and allowed internal models (with safeguards). But model risk appeared: if risk is measured too softly in good times, required capital can be too low exactly when it should be high.

**Basel III (post‑2008)** added higher quality capital (Common Equity Tier 1), leverage ratio backstops, liquidity standards (**LCR** for 30‑day stress and **NSFR** for stable funding), and buffers for systemically important banks and macro‑prudential needs. The big idea: **more loss‑absorbing capacity and more stable funding** so stress doesn’t cascade.
""",
    "Risk Management in Practice (inspired by Hull)": """
**Core ideas**  
- **Market risk**: prices move. Manage with limits, hedges (futures, options, swaps), and scenario tests.  
- **Credit risk**: counterparties may default. Price it (spreads), mitigate it (collateral/CSA, netting), and diversify it.  
- **Liquidity risk**: you can be solvent on paper but unable to roll funding. Hold liquid assets and stagger maturities.  
- **Operational risk**: processes fail; controls and culture matter.

**Value at Risk (VaR)** estimates a worst‑loss threshold over a horizon (e.g., 1‑day 99%). VaR is not a promise; combine it with **expected shortfall**, stress tests, and expert judgment.

**Hedging with derivatives**  
- **Futures** lock prices and reduce earnings volatility.  
- **Options** provide insurance‑like payoff: limited downside with upside kept.  
- **Swaps** exchange risks (e.g., fixed‑for‑floating interest).  
**Position sizing** and **stop‑loss rules** prevent small mistakes from becoming big ones.

**Global standards & culture**  
Rules set the floor; culture sets the ceiling. Clear incentives, independent risk teams, and transparent reporting turn rules into real resilience.
""",
    "How to Trade—Safely, as a Student": """
1) **Have a thesis**: what moves the asset and why now?  
2) **Size small**: never risk more than a tiny fraction of capital per trade.  
3) **Know your hedge**: use options or futures to cap downside.  
4) **Use checklists**: catalyst, valuation, risk, liquidity, exit plan.  
5) **Review outcomes**: was the thesis right, or just the result? Improve the process, not just the P&L.
""",
}

with TAB_KNOW:
    st.subheader("Knowledge Library — readable, story‑first explanations")

    topic = st.selectbox("Choose a topic", list(STORIES.keys()))
    st.markdown(STORIES[topic])

    st.divider()
    st.caption("Have class notes as PDF? Upload and search inside them.")
    uploaded = st.file_uploader("Upload PDF notes (optional)", type=["pdf"])
    if uploaded is not None:
        text = parse_pdf_bytes(uploaded.read())
        st.session_state["kb_text"] = text
        st.success(f"Loaded {uploaded.name} — {len(text):,} characters.")

    query = st.text_input("Search your uploaded notes (keyword)")
    kb_text = st.session_state.get("kb_text", "")
    if query and kb_text:
        lower = kb_text.lower(); ql = query.lower()
        snippets = []
        start = 0
        while True:
            idx = lower.find(ql, start)
            if idx == -1 or len(snippets) >= 5:
                break
            s = max(0, idx - 120); e = min(len(kb_text), idx + 120)
            snippets.append("…" + kb_text[s:e].replace("\n", " ") + "…")
            start = idx + len(ql)
        st.write("**Matches:**")
        for i, sn in enumerate(snippets, 1):
            st.write(f"{i}. {sn}")
        if not snippets:
            st.warning("No matches found.")

# -------------------------------------------------
# RESEARCH
# -------------------------------------------------
with TAB_RESEARCH:
    st.subheader("Company Research & Financials")
    st.caption("Search by name or ticker. For non‑public or private firms (e.g., KPMG), financial statements may not be available.")

    # Resolve name→ticker if needed
    input_text = q.strip()
    guess = TICKER_MAP[TICKER_MAP["name"].str.contains(input_text, case=False, na=False) | (TICKER_MAP["ticker"].str.contains(input_text, case=False, na=False))]

    colA, colB = st.columns([2,1])
    with colA:
        company_name = st.text_input("Company name", value= guess.iloc[0]["name"] if not guess.empty else input_text)
    with colB:
        ticker = st.text_input("Ticker (add exchange suffix for non‑US, e.g., NESN.SW)", value= guess.iloc[0]["ticker"] if not guess.empty else "AAPL")

    # Overview
    if company_name:
        desc, img = wikipedia_summary(company_name)
        c1, c2 = st.columns([1,3])
        with c1:
            if img:
                st.image(img, width=180)
        with c2:
            st.markdown(f"### {company_name}")
            if desc:
                st.write(desc)
            else:
                st.info("No short summary found. Try a more specific name.")

    # Financials
    st.divider()
    st.markdown(f"### Financial Statements — `{ticker}`")

    if ticker.strip() and ticker.strip() != "—":
        fin = yf_load_financials(ticker.strip())

        def tidy(df: pd.DataFrame, label: str) -> pd.DataFrame:
            if df.empty:
                return df
            dft = df.copy()
            dft.index.name = "Line Item"
            dft.attrs["label"] = label
            return dft

        income = tidy(fin["income"], "Income Statement")
        balance = tidy(fin["balance"], "Balance Sheet")
        cash = tidy(fin["cashflow"], "Cash Flow")

        def show_and_download(df: pd.DataFrame, slug: str):
            if df.empty:
                st.warning("Not available from Yahoo Finance for this ticker.")
                return
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv().encode("utf-8")
            st.download_button(
                label=f"Download {slug} (CSV)",
                data=csv,
                file_name=f"{ticker}_{slug.replace(' ','_').lower()}.csv",
                mime="text/csv",
            )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Income Statement (annual)**")
            show_and_download(income, "Income Statement")
        with col2:
            st.markdown("**Balance Sheet (annual)**")
            show_and_download(balance, "Balance Sheet")
        st.markdown("**Cash Flow (annual)**")
        show_and_download(cash, "Cash Flow")

        # Quick visualization if revenue/net income rows exist
        try:
            def pick(df, names):
                for n in names:
                    if n in df.index:
                        return df.loc[n]
                return None
            rev = pick(income, ["Total Revenue","Operating Revenue","Revenue"]) if not income.empty else None
            ni = pick(income, ["Net Income","Net Income Common Stockholders","NetIncome"]) if not income.empty else None
            chart_df = pd.DataFrame()
            if rev is not None:
                chart_df["Revenue"] = rev
            if ni is not None:
                chart_df["Net Income"] = ni
            if not chart_df.empty:
                chart_df.index.name = "Year"
                chart_df = chart_df.reset_index()
                fig = px.line(chart_df, x="Year", y=list(chart_df.columns[1:]), markers=True, title=f"{ticker} — Revenue & Net Income")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.caption(f"(Chart unavailable: {e})")

    else:
        st.warning("Enter a public ticker to load statements. Private firms may not have downloadable data.")

    st.info("**Data availability**: Yahoo Finance typically provides 3–10 years of annual data depending on the company and exchange.")

# -------------------------------------------------
# MATERIALS & TEMPLATES (replaces fragile SEC tab)
# -------------------------------------------------
with TAB_MATERIALS:
    st.subheader("Materials & Templates for Students")
    st.write(
        """
        Use these quick starters in class projects:
        - **Case Study Outline**: Problem → Facts → Analysis → Risks → Recommendation → Lessons.
        - **Earnings Call Notes**: Thesis, surprises vs. expectations, guidance, risks, action items.
        - **Risk Register**: Risk, probability, impact, owner, mitigation, residual risk.
        """
    )

    # Simple downloadable CSV templates generated in-app
    templates = {
        "risk_register.csv": pd.DataFrame({
            "Risk": ["FX move", "Funding stress"],
            "Probability": ["Medium", "Low"],
            "Impact": ["High", "High"],
            "Owner": ["Treasury", "CFO"],
            "Mitigation": ["Hedge with forwards", "Maintain liquidity buffer"],
        }),
        "case_study_outline.csv": pd.DataFrame({
            "Section": ["Problem", "Facts", "Analysis", "Risks", "Recommendation", "Lessons"],
        }),
    }

    for fname, df in templates.items():
        st.write(f"**{fname}**")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), file_name=fname, mime="text/csv")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.divider()
st.caption("PSP Finance — educational project. Data from Wikipedia & Yahoo Finance. Not investment advice.")
