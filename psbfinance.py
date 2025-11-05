# streamlit_app.py
# PSP Finance — Educational finance research and AI insight dashboard

import io
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PyPDF2 import PdfReader

st.set_page_config(page_title="PSP Finance", page_icon="💹", layout="wide")

# -------------------------------------------------
# Ticker Map (expandable)
# -------------------------------------------------
TICKER_MAP = pd.DataFrame([
    {"name":"Apple Inc.", "ticker":"AAPL"},
    {"name":"Microsoft Corporation", "ticker":"MSFT"},
    {"name":"Amazon.com, Inc.", "ticker":"AMZN"},
    {"name":"Alphabet Inc.", "ticker":"GOOGL"},
    {"name":"Meta Platforms, Inc.", "ticker":"META"},
    {"name":"NVIDIA Corporation", "ticker":"NVDA"},
    {"name":"Tesla, Inc.", "ticker":"TSLA"},
    {"name":"JPMorgan Chase & Co.", "ticker":"JPM"},
    {"name":"Bank of America Corporation", "ticker":"BAC"},
    {"name":"Nestlé S.A.", "ticker":"NESN.SW"},
])

# -------------------------------------------------
# Helpers
# -------------------------------------------------
@st.cache_data(ttl=60 * 60)
def wikipedia_summary(company_name: str) -> Tuple[Optional[str], Optional[str]]:
    try:
        search = requests.get(f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={company_name}&limit=1").json()
        if not search.get("pages"):
            return None, None
        page = search["pages"][0]
        summary = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{page.get('title')}").json()
        desc = summary.get("extract")
        img = summary.get("thumbnail", {}).get("source")
        return desc, img
    except Exception:
        return None, None

@st.cache_data(ttl=60 * 60)
def yf_load_financials(ticker: str) -> Dict[str, pd.DataFrame]:
    import yfinance as yf
    t = yf.Ticker(ticker)
    income = t.income_stmt
    balance = t.balance_sheet
    cash = t.cashflow

    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        cols = [pd.to_datetime(c).year if str(c)[:4].isdigit() else c for c in df.columns]
        df.columns = cols
        df = df.reindex(sorted(df.columns), axis=1)
        return df.iloc[:, -10:] if len(df.columns) > 10 else df

    return {"income": normalize(income), "balance": normalize(balance), "cashflow": normalize(cash)}

@st.cache_data(ttl=60 * 60)
def parse_pdf_bytes(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = "\n".join([page.extract_text() or "" for page in reader.pages])
    return text

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
SIDEBAR_URL = "https://images.unsplash.com/photo-1553729784-e91953dec042?q=80&w=1200&auto=format&fit=crop"
st.sidebar.image(SIDEBAR_URL, caption="Finance • Analysis • Learning", use_column_width=True)
st.sidebar.title("PSP Finance")
st.sidebar.caption("Student-built finance learning platform.")
q = st.sidebar.text_input("Search company (name or ticker)", value="Apple")

# -------------------------------------------------
# Header
# -------------------------------------------------
HERO_URL = "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?q=80&w=1200&auto=format&fit=crop"
col1, col2 = st.columns([3, 2])
with col1:
    st.markdown("<h1 style='margin-bottom:0'>PSP Finance</h1>", unsafe_allow_html=True)
    st.write("Research, learn, and analyze global companies with AI-based insights.")
with col2:
    st.image(HERO_URL, use_column_width=True)

st.divider()

# -------------------------------------------------
# Tabs
# -------------------------------------------------
TAB_HOME, TAB_KNOW, TAB_RESEARCH, TAB_AI = st.tabs([
    "🏠 Home",
    "📚 Knowledge Library",
    "🔎 Research",
    "📅 Portfolios & 🧠 AI Insights",
])

# -------------------------------------------------
# HOME TAB
# -------------------------------------------------
with TAB_HOME:
    st.markdown("""## 📘 About the Project

**PSP Finance** is a student-led initiative developed in a Business & Technology class. Our mission is to make financial education clear, accessible, and practical for everyone. The platform allows users to:

- 🔍 Research public companies  
- 📊 View and download financial statements (income, balance sheet, cash flow)  
- 🧠 Explore simplified explanations of complex financial concepts

---

## 💡 Why It Matters

As finance students, we often need multi-year financial data quickly — but searching across multiple websites is time-consuming and inefficient. **PSP Finance solves this by bringing everything into one intuitive dashboard**, complete with export buttons for instant downloads.

Whether you're studying for exams, building a report, or exploring investment ideas, PSP Finance helps you focus on learning — not searching.
""")

# -------------------------------------------------
# KNOWLEDGE LIBRARY
# -------------------------------------------------
STORIES = {
    "Financial Crises and Lessons": "The 2008 Lehman Brothers collapse showed how leverage, poor risk control, and panic can freeze global credit. The Great Depression revealed how falling prices and policy mistakes amplify downturns. Regulators now use capital buffers, liquidity coverage, and stress tests to avoid repeats.",
    "Basel Standards Explained": "Basel I introduced capital rules; Basel II refined them with risk weights; Basel III enforced liquidity and leverage ratios to strengthen resilience. These frameworks keep banks prepared for global shocks.",
    "Risk Management & Hull Principles": "Risk comes in many forms: market, credit, liquidity, and operational. Hull’s core ideas stress measurement (VaR, expected shortfall), diversification, and disciplined hedging through futures, options, and swaps.",
    "Smart Trading Essentials": "Good trading blends analysis and control. Always size small, hedge major exposures, and review decisions. Focus on consistent learning rather than quick profit.",
}

with TAB_KNOW:
    st.subheader("Knowledge Library — Story-based Finance Education")
    topic = st.selectbox("Choose a topic", list(STORIES.keys()))
    st.write(STORIES[topic])

    uploaded = st.file_uploader("Upload PDF notes (optional)", type=["pdf"])
    if uploaded is not None:
        text = parse_pdf_bytes(uploaded.read())
        st.session_state["kb_text"] = text
        st.success(f"Loaded {uploaded.name} — {len(text):,} characters.")

    query = st.text_input("Search uploaded notes")
    kb_text = st.session_state.get("kb_text", "")
    if query and kb_text:
        lower = kb_text.lower(); ql = query.lower()
        hits = ["…" + kb_text[max(0,i-80):min(len(kb_text),i+80)] + "…" for i in range(len(lower)) if lower.startswith(ql,i)]
        for i, h in enumerate(hits[:5], 1):
            st.write(f"{i}. {h}")

# -------------------------------------------------
# RESEARCH TAB
# -------------------------------------------------
with TAB_RESEARCH:
    st.subheader("Company Research & Financials")
    guess = TICKER_MAP[TICKER_MAP["name"].str.contains(q, case=False, na=False) | TICKER_MAP["ticker"].str.contains(q, case=False, na=False)]
    company_name = guess.iloc[0]["name"] if not guess.empty else q
    ticker = guess.iloc[0]["ticker"] if not guess.empty else "AAPL"

    desc, img = wikipedia_summary(company_name)
    if img:
        st.image(img, width=200)
    st.markdown(f"### {company_name}")
    st.write(desc or "No summary found.")

    fin = yf_load_financials(ticker)
    for label, df in fin.items():
        if df.empty:
            continue
        st.markdown(f"**{label.capitalize()}**")
        st.dataframe(df)
        st.download_button(f"Download {label}", df.to_csv().encode('utf-8'), file_name=f"{ticker}_{label}.csv")

    if not fin["income"].empty:
        try:
            rev = fin["income"].loc[[i for i in fin["income"].index if 'Revenue' in i][0]]
            ni = fin["income"].loc[[i for i in fin["income"].index if 'Net' in i and 'Income' in i][0]]
            df = pd.DataFrame({"Revenue": rev, "Net Income": ni})
            df.index.name = "Year"
            fig = px.line(df.reset_index(), x="Year", y=["Revenue", "Net Income"], markers=True, title=f"{ticker} — Revenue vs Net Income")
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            pass

# -------------------------------------------------
# AI INSIGHTS TAB (Portfolios & Historical Performance)
# -------------------------------------------------
with TAB_AI:
    st.subheader("📅 Historical Performance Charts & 🧠 AI-based Insights")
    st.write("Compare multiple tickers and see AI-style commentary on their trends.")

    tickers = st.text_input("Enter tickers separated by commas", value="AAPL, MSFT, NVDA")
    tickers = [t.strip().upper() for t in tickers.split(",") if t.strip()]

    import yfinance as yf
    data = yf.download(tickers, period="5y")['Adj Close']
    if not data.empty:
        normed = data / data.iloc[0] * 100
        fig = px.line(normed, title="Normalized 5-Year Performance (100 = start)")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🧠 AI-based Insight Summary")
        best = normed.iloc[-1].idxmax()
        worst = normed.iloc[-1].idxmin()
        st.write(f"Over the past 5 years, **{best}** has delivered the strongest cumulative return, while **{worst}** lagged behind.")
        st.write("Volatility across these assets highlights the importance of diversification and disciplined rebalancing — key themes in global risk management.")

st.divider()
st.caption("PSP Finance — Educational project built with Streamlit, Yahoo Finance, and Wikipedia. Not investment advice.")
