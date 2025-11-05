# streamlit_app.py
# PSP Finance: a student-friendly app to research companies, view/download financials, and browse filings
# Run locally with:  
#   pip install streamlit yfinance pandas requests plotly PyPDF2
#   streamlit run streamlit_app.py

import io
import json
import textwrap
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PyPDF2 import PdfReader

# -----------------------------
# Page & global config
# -----------------------------
st.set_page_config(
    page_title="PSP Finance",
    page_icon="💹",
    layout="wide",
    menu_items={
        "Get help": "mailto:support@example.com",
        "Report a bug": "mailto:support@example.com",
        "About": "PSP Finance — a learning project for finance students."
    }
)

# A friendly, consistent User-Agent for the SEC API (they require one)
SEC_HEADERS = {
    "User-Agent": "PSP-Finance/1.0 (student app; contact: student@example.com)",
    "Accept-Encoding": "gzip, deflate",
    "Host": "data.sec.gov"
}

# -----------------------------
# Helpers
# -----------------------------
@st.cache_data(ttl=60 * 60)
def wikipedia_summary(company_name: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (summary, image_url) from Wikipedia REST API if available."""
    try:
        # Search first
        search = requests.get(
            f"https://en.wikipedia.org/w/rest.php/v1/search/title?q={company_name}&limit=1"
        ).json()
        if not search.get("pages"):
            return None, None
        page = search["pages"][0]
        page_id = page.get("id")
        # Get summary
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
    """Load annual financial statements via yfinance. Returns dict of DataFrames.
    Keys: income, balance, cashflow.
    """
    import yfinance as yf

    t = yf.Ticker(ticker)
    # yfinance returns annual statements with columns as periods (DatetimeIndex)
    income = t.income_stmt
    balance = t.balance_sheet
    cash = t.cashflow
    # Normalize column labels to year (int)
    def normalize(df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()
        cols = []
        for c in df.columns:
            try:
                year = pd.to_datetime(c).year
            except Exception:
                # Sometimes yfinance returns plain strings; try slicing
                try:
                    year = int(str(c)[:4])
                except Exception:
                    year = str(c)
            cols.append(year)
        df2 = df.copy()
        df2.columns = cols
        # Sort columns ascending (oldest->newest)
        df2 = df2.reindex(sorted(df2.columns), axis=1)
        return df2

    return {
        "income": normalize(income),
        "balance": normalize(balance),
        "cashflow": normalize(cash),
    }

@st.cache_data(ttl=24 * 60 * 60)
def sec_ticker_map() -> pd.DataFrame:
    """Return SEC ticker<->CIK mapping as DataFrame."""
    url = "https://www.sec.gov/files/company_tickers.json"
    r = requests.get(url, headers=SEC_HEADERS)
    r.raise_for_status()
    raw = r.json()
    rows = []
    for _, v in raw.items():
        rows.append({
            "ticker": v.get("ticker"),
            "cik": str(v.get("cik_str")).zfill(10),
            "title": v.get("title"),
        })
    return pd.DataFrame(rows)

@st.cache_data(ttl=60 * 60)
def sec_company_submissions(cik: str) -> Dict:
    """Fetch SEC submissions.json for a given CIK (zero-padded)."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    r = requests.get(url, headers=SEC_HEADERS)
    r.raise_for_status()
    return r.json()

@st.cache_data(ttl=60 * 60)
def build_filings_table(submissions: Dict, limit: int = 100) -> pd.DataFrame:
    forms = submissions.get("filings", {}).get("recent", {})
    if not forms:
        return pd.DataFrame()
    df = pd.DataFrame({
        "accessionNumber": forms.get("accessionNumber", []),
        "filingDate": forms.get("filingDate", []),
        "reportDate": forms.get("reportDate", []),
        "form": forms.get("form", []),
        "primaryDoc": forms.get("primaryDocument", []),
        "primaryDocDesc": forms.get("primaryDocDescription", []),
    })
    df = df.head(limit)
    # Build doc URL
    def doc_url(row):
        acc = row["accessionNumber"].replace("-", "")
        return f"https://www.sec.gov/Archives/edgar/data/{submissions.get('cik')}/{acc}/{row['primaryDoc']}"

    df["url"] = df.apply(doc_url, axis=1)
    return df

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

# -----------------------------
# Sidebar: App info & inputs
# -----------------------------
st.sidebar.image(
    "https://images.unsplash.com/photo-1553729784-e91953dec042?q=80&w=1200&auto=format&fit=crop",
    caption="Finance • Analysis • Learning",
    use_column_width=True,
)

st.sidebar.title("PSP Finance")
st.sidebar.caption(
    "A student-built hub for researching companies, downloading financials, and learning the language of business."
)

default_ticker = st.sidebar.text_input("Default Ticker (optional)", value="AAPL")

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <style>
        .big-title {font-size: 44px; font-weight: 800; margin-bottom: 0px}
        .tagline {font-size: 16px; color: #5b5b5b;}
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 2])
with col1:
    st.markdown('<div class="big-title">PSP Finance</div>', unsafe_allow_html=True)
    st.markdown(
        "<div class='tagline'>Built for students: simple research, fast downloads, clear learning.</div>",
        unsafe_allow_html=True,
    )
with col2:
    st.image(
        "https://images.unsplash.com/photo-1520607162513-77705c0f0d4a?q=80&w=1200&auto=format&fit=crop",
        use_column_width=True,
    )

st.divider()

# -----------------------------
# Horizontal Navigation (Tabs)
# -----------------------------
TAB_HOME, TAB_KNOW, TAB_RESEARCH, TAB_FILINGS = st.tabs([
    "🏠 Home",
    "📚 Knowledge Base",
    "🔎 Research",
    "📄 Filings",
])

# -----------------------------
# HOME
# -----------------------------
with TAB_HOME:
    st.subheader("About the Project")
    st.write(
        """
        **PSP Finance** is a student project created in a Business & Tech class. The goal: make it **easy** for finance
        students to research a company, **download clean financial statements**, and learn the key ideas from class – all in one place.
        """
    )

    st.markdown(
        """
        **Why this matters to us**  
        As students, we often need quick access to income statements, balance sheets, and cash flows for multiple years. Downloading from different
        websites is slow and messy. PSP Finance brings it together with one clean interface and export buttons.
        """
    )

    st.info(
        "Tip: Use the **Research** tab for company overviews & financials, and the **Filings** tab for official SEC documents (US-listed companies)."
    )

# -----------------------------
# KNOWLEDGE BASE
# -----------------------------
with TAB_KNOW:
    st.subheader("Course Knowledge (Chapters 1–37)")
    st.caption("Upload notes or textbooks (PDF) and search inside. Great for revision: options, derivatives, and more.")

    uploaded = st.file_uploader("Upload PDF notes (optional)", type=["pdf"])
    if uploaded is not None:
        text = parse_pdf_bytes(uploaded.read())
        st.session_state["kb_text"] = text
        st.success(f"Loaded {uploaded.name} — {len(text):,} characters of text.")

    query = st.text_input("Search your notes (keyword)")
    kb_text = st.session_state.get("kb_text", "")

    if query and kb_text:
        # Simple keyword hits (top 5 snippets)
        snippets = []
        lower = kb_text.lower()
        q = query.lower()
        start = 0
        while True:
            idx = lower.find(q, start)
            if idx == -1 or len(snippets) >= 5:
                break
            s = max(0, idx - 120)
            e = min(len(kb_text), idx + 120)
            snippets.append("…" + kb_text[s:e].replace("\n", " ") + "…")
            start = idx + len(q)
        st.write("**Matches:**")
        for i, sn in enumerate(snippets, 1):
            st.write(f"{i}. {sn}")
        if not snippets:
            st.warning("No matches found.")

    with st.expander("Chapter Outline (placeholders you can edit)"):
        cols = st.columns(3)
        total = 37
        for i in range(total):
            with cols[i % 3]:
                st.text_input(f"Chapter {i+1}", value=f"Topic {i+1}")

# -----------------------------
# RESEARCH
# -----------------------------
with TAB_RESEARCH:
    st.subheader("Company Research & Financials")
    st.caption("Enter a company name for a quick overview (Wikipedia), and a ticker for financial statements (Yahoo Finance).")

    colA, colB = st.columns([2, 1])
    with colA:
        company_name = st.text_input("Company name (e.g., 'Nestlé', 'KPMG', 'Tesla')", value="Nestlé")
    with colB:
        ticker = st.text_input("Ticker (optional, for financials)", value=default_ticker)

    # Overview from Wikipedia
    if company_name:
        desc, img = wikipedia_summary(company_name)
        if img:
            st.image(img, width=240)
        if desc:
            st.write(desc)
        else:
            st.info("No Wikipedia summary found. Try a different spelling or a more specific name.")

    # Financials via yfinance
    if ticker:
        st.divider()
        st.markdown(f"### Financial Statements — `{ticker}`")
        fin = yf_load_financials(ticker)

        def tidy(df: pd.DataFrame, label: str) -> pd.DataFrame:
            if df.empty:
                return df
            dft = df.copy()
            dft.index.name = "Line Item"
            # Keep up to the last 10 columns (years)
            if len(dft.columns) > 10:
                dft = dft.iloc[:, -10:]
            dft.attrs["label"] = label
            return dft

        income = tidy(fin["income"], "Income Statement")
        balance = tidy(fin["balance"], "Balance Sheet")
        cash = tidy(fin["cashflow"], "Cash Flow")

        def show_and_download(df: pd.DataFrame):
            if df.empty:
                st.warning("Not available for this ticker.")
                return
            st.dataframe(df)
            csv = df.to_csv().encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"{ticker}_{df.attrs.get('label','table').replace(' ','_').lower()}.csv",
                mime="text/csv",
            )

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Income Statement (annual)**")
            show_and_download(income)
        with col2:
            st.markdown("**Balance Sheet (annual)**")
            show_and_download(balance)
        st.markdown("**Cash Flow (annual)**")
        show_and_download(cash)

        # Simple chart: Revenue & Net Income if present
        try:
            rev_candidates = [
                "Total Revenue",
                "Operating Revenue",
                "Revenue",
            ]
            ni_candidates = [
                "Net Income",
                "Net Income Common Stockholders",
                "NetIncome",
            ]
            def pick_line(df: pd.DataFrame, names: List[str]) -> Optional[pd.Series]:
                for n in names:
                    if n in df.index:
                        return df.loc[n]
                return None
            rev = pick_line(income, rev_candidates) if not income.empty else None
            ni = pick_line(income, ni_candidates) if not income.empty else None
            chart_df = pd.DataFrame()
            if rev is not None:
                chart_df["Revenue"] = rev
            if ni is not None:
                chart_df["Net Income"] = ni
            if not chart_df.empty:
                chart_df.index.name = "Year"
                chart_df = chart_df.reset_index()
                fig = px.line(chart_df, x="Year", y=list(chart_df.columns[1:]), markers=True)
                fig.update_layout(height=380, title=f"{ticker} — Revenue & Net Income")
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.caption(f"(Chart unavailable: {e})")

    st.info(
        "Note: Private firms (e.g., KPMG) may lack public financial statements in Yahoo Finance. Use the **Overview** text for context or upload PDFs in the Knowledge tab."
    )

# -----------------------------
# FILINGS (SEC for US-listed)
# -----------------------------
with TAB_FILINGS:
    st.subheader("SEC Filings (US-listed companies)")
    st.caption("Search a US ticker to list recent 10-K, 10-Q, 8-K, S-1, etc., with links to the primary documents.")

    sec_tk = st.text_input("US Ticker for SEC search", value=default_ticker)

    if sec_tk:
        try:
            mapping = sec_ticker_map()
            row = mapping[mapping["ticker"].str.upper() == sec_tk.upper()]
            if row.empty:
                st.warning("Ticker not found in SEC database. Try another (only US-listed).")
            else:
                cik = row.iloc[0]["cik"]
                subs = sec_company_submissions(cik)
                table = build_filings_table(subs, limit=100)
                if table.empty:
                    st.info("No recent filings found.")
                else:
                    # Filter common forms and show download
                    forms_pick = st.multiselect(
                        "Filter forms", ["10-K", "10-Q", "8-K", "S-1", "S-3", "424B2", "SD", "13D", "13G"],
                        default=["10-K", "10-Q", "8-K"],
                    )
                    view = table[table["form"].isin(forms_pick)] if forms_pick else table
                    # Pretty display with click-through links
                    show = view[["filingDate", "reportDate", "form", "primaryDocDesc", "url"]].rename(
                        columns={
                            "filingDate": "Filed",
                            "reportDate": "Report Date",
                            "form": "Form",
                            "primaryDocDesc": "Description",
                            "url": "Document URL",
                        }
                    )
                    st.dataframe(show, use_container_width=True)

                    csv = show.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="Download Filings List (CSV)",
                        data=csv,
                        file_name=f"{sec_tk}_sec_filings.csv",
                        mime="text/csv",
                    )
        except Exception as e:
            st.error(f"SEC lookup failed: {e}")

# -----------------------------
# Footer
# -----------------------------
st.divider()
st.caption(
    "PSP Finance — built with Streamlit, Yahoo Finance, Wikipedia, and SEC data. Educational use only; not investment advice."
)
