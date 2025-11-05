# streamlit_app.py
# PSP Finance — Working build with images & expanded knowledge library
# -------------------------------------------------
# Run:
#   pip install streamlit yfinance pandas plotly
#   streamlit run streamlit_app.py

from typing import Dict, Optional, List, Tuple
import io
import pandas as pd
import streamlit as st
import plotly.express as px
from PyPDF2 import PdfReader
import requests

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
# IMAGES (royalty-free Unsplash links)
# -------------------------
IMG = {
    "sidebar": "https://images.unsplash.com/photo-1553729784-e91953dec042?q=80&w=1200&auto=format&fit=crop",
    "hero": "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?q=80&w=1200&auto=format&fit=crop",
    "research": "https://images.unsplash.com/photo-1551281044-8b18c1d09f43?q=80&w=1200&auto=format&fit=crop",
    "ai": "https://images.unsplash.com/photo-1545239351-1141bd82e8a6?q=80&w=1200&auto=format&fit=crop",
}

TOPIC_IMAGES = {
    "Financial Crises — A Short Story": "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=1200&auto=format&fit=crop",
    "Basel I → Basel III (Why it matters)": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=1200&auto=format&fit=crop",
    "Risk Management (inspired by Hull)": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?q=80&w=1200&auto=format&fit=crop",
    "How to Trade — Safely for Students": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?q=80&w=1200&auto=format&fit=crop",
    "1997 Asian Financial Crisis": "https://images.unsplash.com/photo-1533903345306-15d1c30952de?q=80&w=1200&auto=format&fit=crop",
    "2000 Dot‑Com Bust": "https://images.unsplash.com/photo-1556157382-97eda2d62296?q=80&w=1200&auto=format&fit=crop",
    "2008 Global Financial Crisis": "https://images.unsplash.com/photo-1476357471311-43c0db9fb2b4?q=80&w=1200&auto=format&fit=crop",
    "2010–2012 Eurozone Debt Crisis": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1200&auto=format&fit=crop",
    "2020 COVID‑19 Market Shock": "https://images.unsplash.com/photo-1583324113626-70df0f4deaab?q=80&w=1200&auto=format&fit=crop",
    "2023 U.S. Regional Bank Stress": "https://images.unsplash.com/photo-1459257868276-5e65389e2722?q=80&w=1200&auto=format&fit=crop",
}

# -------------------------
# KNOWLEDGE LIBRARY CONTENT (expanded, event‑based)
# -------------------------
STORIES = {
    "Financial Crises — A Short Story": """
**Pattern.** In calm times, credit expands and leverage builds. A shock (rate hikes, default waves, policy error) exposes weak balance sheets. Fire‑sales follow, liquidity vanishes, and losses feed on themselves.

**Policy lessons.** Move fast to stabilize funding markets, protect deposits, and avoid pro‑cyclical tightening. Use lender‑of‑last‑resort tools and fiscal backstops carefully, paired with reforms that raise resilience.
""",
    "1997 Asian Financial Crisis": """
**What happened.** Several Asian economies with fixed/managed exchange rates (Thailand, Indonesia, South Korea) faced rapid capital outflows after currency pressures in 1997. Devaluations, corporate debt in foreign currency, and fragile banking systems led to recessions.

**Why it mattered.** Currency mismatches turned FX moves into solvency problems. IMF programs emphasized stabilization and reforms. **Lesson:** avoid excessive short‑term foreign‑currency borrowing and build credible reserves.
""",
    "2000 Dot‑Com Bust": """
**What happened.** Tech valuations surged in the late 1990s despite thin profits. When growth expectations reset in 2000–2002, the Nasdaq fell ~75% from its peak. Funding dried up for unprofitable firms.

**Lesson.** Distinguish structural innovation from speculative pricing. Cash generation and runway matter when markets tighten.
""",
    "2008 Global Financial Crisis": """
**What happened.** U.S. housing losses spread through highly levered banks and shadow banks holding mortgage‑linked securities. After Bear Stearns was rescued, **Lehman Brothers** failed (Sep 2008), freezing global credit. Central banks created emergency facilities; governments recapitalized banks.

**Reforms.** Higher-quality capital (CET1), leverage backstops, liquidity rules (LCR/NSFR), stress tests, and resolution plans ("living wills").
""",
    "2010–2012 Eurozone Debt Crisis": """
**What happened.** Rising sovereign spreads (Greece, Ireland, Portugal, later Spain/Italy) stressed banks that held government bonds. Bailouts and the ECB’s interventions (including LTRO/OMT) contained the crisis.

**Lesson.** Sovereign risk and bank risk can reinforce each other. A credible lender of last resort and fiscal backstops reduce tail scenarios.
""",
    "2020 COVID‑19 Market Shock": """
**What happened.** A sudden global stop in March 2020 triggered a dash for cash: equities fell, credit spreads widened, and even Treasury markets were strained. Policymakers responded with rate cuts, asset purchases, and emergency lending programs; fiscal policy supported households and firms.

**Lesson.** Liquidity can vanish even in core markets. Diverse funding and buffers matter.
""",
    "2023 U.S. Regional Bank Stress": """
**What happened.** A rapid rise in interest rates hurt banks holding long‑duration securities and concentrated deposits. **Silicon Valley Bank** and others faced runs; authorities guaranteed deposits at failed institutions and created liquidity facilities against high‑quality collateral.

**Lesson.** Interest‑rate risk and concentrated funding are dangerous together; hedging and diversified deposits are key.
""",
    "Basel I → Basel III (Why it matters)": """
- **Basel I (late 1980s):** simple risk‑weighted capital rules across countries.  
- **Basel II:** more granular risk weights, use of internal models under supervision; introduced model‑risk concerns.  
- **Basel III (post‑2008):** higher CET1, leverage ratio, liquidity coverage (**LCR**), net stable funding (**NSFR**), capital buffers for systemically important banks.
""",
    "Risk Management (inspired by Hull)": """
- **Market risk:** control with limits, hedges (futures/options/swaps), VaR/Expected Shortfall, and scenario tests.  
- **Credit risk:** price via spreads; mitigate with collateral, netting, and diversification.  
- **Liquidity risk:** hold cash‑like assets, stagger maturities, test survival horizons.  
- **Operational risk:** strong controls and culture.

**Derivatives for hedging:** futures (lock prices), options (insurance‑like payoff), swaps (exchange risk profiles). **Position sizing** and **stop‑loss** rules keep mistakes small.
""",
    "How to Trade — Safely for Students": """
1) Thesis first (drivers & catalysts).  
2) Small risk per trade.  
3) Define exits (profit target/stop).  
4) Hedge big exposures.  
5) Review process, not just P&L.
""",
}

# -------------------------
# Helpers: Wikipedia summary & PDF parsing
# -------------------------
@st.cache_data(ttl=60*60)
def wikipedia_summary(company_name: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        s = requests.get(f"https://www.wikipedia.org/w/index.php?search={company_name}", timeout=10)
        # Use REST summary for the first title hit
        sr = requests.get(f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={company_name}&limit=1", timeout=10).json()
        if not sr.get("pages"):
            return None, None
        title = sr["pages"][0]["title"]
        js = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}", timeout=10).json()
        desc = js.get("extract")
        img = js.get("thumbnail", {}).get("source")
        return desc, img
    except Exception:
        return None, None

@st.cache_data(ttl=60*60)
def parse_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "
".join([(p.extract_text() or "") for p in reader.pages])
    return text

# -------------------------
# yfinance loaders
# -------------------------
@st.cache_data(ttl=60*30)
def load_financials(ticker: str) -> Dict[str, pd.DataFrame]:
    import yfinance as yf
    t = yf.Ticker(ticker)
    income = getattr(t, 'financials', pd.DataFrame())
    if income.empty:
        income = getattr(t, 'income_stmt', pd.DataFrame())
    balance = getattr(t, 'balance_sheet', pd.DataFrame())
    cash = getattr(t, 'cashflow', pd.DataFrame())

    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        cols = []
        for c in df.columns:
            try:
                cols.append(int(str(c)[:4]))
            except Exception:
                cols.append(str(c))
        out = df.copy()
        out.columns = cols
        out = out.reindex(sorted(out.columns), axis=1)
        if out.shape[1] > 10:
            out = out.iloc[:, -10:]
        out.index.name = "Line Item"
        return out

    return {'income': normalize(income), 'balance': normalize(balance), 'cashflow': normalize(cash)}

@st.cache_data(ttl=60*30)
def load_history(tickers: List[str], period: str = "5y") -> pd.DataFrame:
    import yfinance as yf
    if not tickers:
        return pd.DataFrame()
    data = yf.download(tickers, period=period, auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data = data['Close']
    return data

# -------------------------
# SIDEBAR & HEADER IMAGES
# -------------------------
st.sidebar.image(IMG["sidebar"], caption="Finance • Analysis • Learning", use_column_width=True)
st.sidebar.title("PSP Finance")
st.sidebar.caption("Student‑built finance learning platform.")
q = st.sidebar.text_input("Search company (name or ticker)", value="Apple")

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("<h1 style='margin-bottom:0'>PSP Finance</h1>", unsafe_allow_html=True)
    st.write("Research, learn, and analyze companies with images, stories, and charts.")
with col2:
    st.image(IMG["hero"], use_column_width=True)

st.divider()

# -------------------------
# TABS
# -------------------------
TAB_HOME, TAB_KNOW, TAB_RESEARCH, TAB_AI = st.tabs([
    "🏠 Home",
    "📚 Knowledge Library",
    "🔎 Research",
    "📅 Historical Performance & 🧠 Insights",
])

# HOME
with TAB_HOME:
    st.image(IMG["hero"], use_column_width=True)
    st.markdown(ABOUT_MD)

# KNOWLEDGE
with TAB_KNOW:
    st.subheader("Knowledge Library — Real events, clear lessons")
    topic = st.selectbox("Topic", list(STORIES.keys()), index=0)
    st.image(TOPIC_IMAGES.get(topic, IMG["sidebar"]), use_column_width=True)
    st.markdown(STORIES[topic])

    st.divider()
    st.caption("Have class notes? Upload and search inside them.")
    uploaded = st.file_uploader("Upload PDF notes (optional)", type=["pdf"])
    if uploaded is not None:
        text = parse_pdf_bytes(uploaded.read())
        st.session_state["kb_text"] = text
        st.success(f"Loaded {uploaded.name} — {len(text):,} characters.")
    query = st.text_input("Search uploaded notes (keyword)")
    kb_text = st.session_state.get("kb_text", "")
    if query and kb_text:
        lower = kb_text.lower(); ql = query.lower()
        hits = []
        start = 0
        while True:
            idx = lower.find(ql, start)
            if idx == -1 or len(hits) >= 5:
                break
            s = max(0, idx-120); e = min(len(kb_text), idx+120)
            snippet = "…" + kb_text[s:e].replace("
"," ") + "…"
            hits.append(snippet)
            start = idx + len(ql)
        st.write("**Matches:**")
        for i, h in enumerate(hits, 1):
            st.write(f"{i}. {h}")
        if not hits:
            st.info("No matches found.")

# RESEARCH
with TAB_RESEARCH:
    st.subheader("Company Research & Financials")
    st.image(IMG["research"], use_column_width=True)

    name = st.text_input("Company name", value=q)
    ticker = st.text_input("Ticker (e.g., AAPL, MSFT, NESN.SW)", value="AAPL").strip()

    # Overview with image from Wikipedia if available
    def wiki(company: str) -> Tuple[Optional[str], Optional[str]]:
        return wikipedia_summary(company)

    if name:
        desc, img = wiki(name)
        c1, c2 = st.columns([1,3])
        with c1:
            if img:
                st.image(img, width=180)
        with c2:
            st.markdown(f"### {name}")
            st.write(desc or "No short summary found.")

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

        # Quick visualization: Revenue vs Net Income if present
        try:
            inc = fin['income']
            rev_row = next((r for r in inc.index if 'Revenue' in r), None)
            ni_row  = next((r for r in inc.index if 'Net' in r and 'Income' in r), None)
            if rev_row and ni_row:
                df = pd.DataFrame({"Revenue": inc.loc[rev_row], "Net Income": inc.loc[ni_row]})
                df.index.name = "Year"
                fig = px.line(df.reset_index(), x="Year", y=["Revenue", "Net Income"], markers=True, title=f"{ticker} — Revenue vs Net Income")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.caption(f"(Chart unavailable: {e})")

# AI / PORTFOLIOS
with TAB_AI:
    st.subheader("📅 Historical Performance Charts & 🧠 Insights")
    st.image(IMG["ai"], use_column_width=True)

    raw = st.text_input("Tickers (comma‑separated)", value="AAPL, MSFT, NVDA").strip()
    tickers = [t.strip().upper() for t in raw.split(',') if t.strip()]

    hist = load_history(tickers, period="5y")
    if hist.empty:
        st.info("No price data returned. Try different tickers.")
    else:
        norm = hist / hist.iloc[0] * 100
        fig = px.line(norm, title="Normalized 5‑Year Performance (100 = start)")
        st.plotly_chart(fig, use_container_width=True)

        # Simple insights
        last = norm.iloc[-1].sort_values(ascending=False)
        best = last.index[0]
        worst = last.index[-1]
        ret = hist.pct_change().dropna()
        vol = ret.std().sort_values()
        st.markdown("### 🧠 Insight Summary")
        st.write(f"Top performer: **{best}**. Lagging performer: **{worst}**.")
        st.write(f"Lower historical volatility among inputs: **{vol.index[0]}**; higher volatility: **{vol.index[-1]}**.")
        st.caption("Educational insights only — not investment advice.")

st.divider()
st.caption("PSP Finance — Images + expanded knowledge. Data from Yahoo Finance & Wikipedia. Not investment advice.")
