# PSPFinance — Bubble-style replica in Streamlit (Corrected)
# ------------------------------------------------------------------
# Features:
# - Dashboard (hero + market overview cards)
# - Market Data (multi-ticker, snapshot table)
# - Portfolio (add holdings, CSV upload, KPIs, P/L, top holdings)
# - Analysis (AI summaries + simple decomposition & MA signals)
# - News (finance-only RSS with search and filters)
# - Alerts (price threshold alerts)
# - Community (lightweight forum in session)
# - About
# ------------------------------------------------------------------

import os
import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf
import feedparser

# Optional AI + PDF
try:
    import openai
    HAVE_OPENAI = True
except Exception:
    HAVE_OPENAI = False

from PyPDF2 import PdfReader

# ---------- Page / Theme ----------
st.set_page_config(page_title="PSPFinance", layout="wide")

DARK_CSS = """
<style>
:root { --bg:#0e1824; --panel:#131f2c; --text:#e6eef6; --muted:#a8b3bf; --accent:#f3c13a; --green:#37c36b; }
html, body, [class^="css"]  { background:var(--bg) !important; color:var(--text); }
section.main > div { padding-top: 0rem !important; }
h1,h2,h3,h4 { color: var(--text); letter-spacing: .2px; }
small, .stCaption, .stMarkdown p { color: var(--muted) !important; }
.block-container { padding-top: 1rem; }
.card { background: var(--panel); border-radius: 14px; padding: 18px 18px; border: 1px solid #1b2a3a; }
.kpi { font-size: 30px; font-weight: 700; }
.kpi-sub { font-size: 13px; color: var(--muted); margin-top: -6px; }
.badge { display:inline-block; padding:3px 10px; border-radius:10px; background:#1e2b3b; color:#dcdcdc; font-size:12px; margin-right:8px;}
.badge--accent{ background: var(--accent); color:#121212; font-weight:700;}
.change-up{ color: var(--green); font-weight:700;}
.change-down{ color:#ff6b6b; font-weight:700;}
.stButton>button { background: var(--accent); color:#141414; border:0; border-radius:10px; padding:8px 14px; font-weight:700;}
.stTextInput>div>div>input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div { background:#0c1520; color:var(--text); border:1px solid #1b2a3a; }
hr{ border-color:#1b2a3a;}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# ---------- Sidebar ----------
st.sidebar.title("PSPFinance")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Market Data", "Portfolio", "Analysis", "News", "Alerts", "Community", "About"],
)

# ---------- Helpers / Cache ----------
@st.cache_data(ttl=300)
def yf_history(tickers, period="1y", interval="1d"):
    if isinstance(tickers, str):
        tickers = [tickers]
    df = yf.download(tickers, period=period, interval=interval, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    return df

@st.cache_data(ttl=600)
def yf_info(ticker):
    return yf.Ticker(ticker).info

def pct_change_str(x):
    try:
        return f"{x:+.2f}%"
    except Exception:
        return "N/A"

def last_price_change(ticker):
    df = yf_history(ticker, period="5d")
    if df.empty:
        return None, None, None
    s = df.iloc[-2:]
    price = float(s.iloc[-1])
    prev = float(s.iloc[0])
    chg = (price/prev - 1.0)*100.0 if prev else None
    return price, chg, len(df)

def kpi_card(title, price, change_pct, right_note=""):
    change_class = "change-up" if (change_pct is not None and change_pct >= 0) else "change-down"
    price_txt = f"${price:,.2f}" if price is not None else "N/A"
    chg_txt = pct_change_str(change_pct) if change_pct is not None else "N/A"
    st.markdown(
        f"""
        <div class="card">
            <div class="badge">Stock Index</div>
            <h3 style="margin:.2rem 0 .6rem 0;">{title}</h3>
            <div class="kpi">{price_txt}</div>
            <div class="{change_class}">{chg_txt}</div>
            <div class="kpi-sub">{right_note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def ensure_state():
    for key, default in {
        "holdings": [],
        "posts": [],
        "alerts": [],
    }.items():
        if key not in st.session_state:
            st.session_state[key] = default

ensure_state()

# ---------- Dashboard ----------
if page == "Dashboard":
    # Hero
    st.markdown(
        """
        <div class="card" style="padding:24px 24px; background:linear-gradient(180deg,#0f1d2c,#0e1824);">
            <div class="badge badge--accent">AI-Driven</div>
            <div class="badge">24/7 Monitoring</div>
            <div class="badge">Real-Time</div>
            <h1 style="margin-top:.6rem; font-size:42px;">Your Financial Intelligence Hub</h1>
            <p style="max-width:900px; color:#c9d4df;">
                Real-time market data, AI-powered insights, and personalized analysis to help you make informed decisions with confidence.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Market Overview")
    c1, c2, c3 = st.columns(3)
    with c1:
        p, chg, _ = last_price_change("^GSPC")
        kpi_card("S&P 500", p, chg, "SPX")
    with c2:
        p, chg, _ = last_price_change("^IXIC")
        kpi_card("NASDAQ", p, chg, "IXIC")
    with c3:
        p, chg, _ = last_price_change("BTC-USD")
        kpi_card("Bitcoin", p, chg, "BTCUSD")

    st.markdown("### Portfolio Performance")
    if st.session_state.holdings:
        tickers = list({h["ticker"].upper() for h in st.session_state.holdings})
        prices = yf_history(tickers, period="6mo")
        latest = prices.iloc[-1]

        total_value = 0.0
        invested = 0.0
        for h in st.session_state.holdings:
            t = h["ticker"].upper()
            qty = float(h["qty"])
            bp = float(h.get("buy_price", 0))
            if t in latest:
                total_value += float(latest[t]) * qty
            invested += bp * qty
        gain = total_value - invested
        ret_pct = (gain / invested * 100.0) if invested else 0.0

        k1, k2, k3, k4 = st.columns(4)
        # k1
        with k1:
            st.markdown(
                f'<div class="card"><div>Total Value</div><div class="kpi">${total_value:,.2f}</div></div>',
                unsafe_allow_html=True
            )
        # k2 (fixed interpolation)
        with k2:
            color_class = "change-up" if gain >= 0 else "change-down"
            st.markdown(
                f'<div class="card"><div>Total Gain/Loss</div>'
                f'<div class="kpi {color_class}">{gain:,+.2f}</div></div>',
                unsafe_allow_html=True
            )
        # k3 (fixed interpolation)
        with k3:
            color_class_ret = "change-up" if ret_pct >= 0 else "change-down"
            st.markdown(
                f'<div class="card"><div>Total Return</div>'
                f'<div class="kpi {color_class_ret}">{ret_pct:+.2f}%</div></div>',
                unsafe_allow_html=True
            )
        # k4
        with k4:
            st.markdown(
                f'<div class="card"><div>Holdings</div><div class="kpi">{len(tickers)}</div></div>',
                unsafe_allow_html=True
            )

        st.markdown("#### Portfolio Value (last 6 months)")
        st.line_chart(prices.fillna(method="ffill"))
    else:
        st.info("No holdings yet. Go to the Portfolio page to add investments.")

# ---------- Market Data ----------
elif page == "Market Data":
    st.header("Market Data")
    default = "AAPL, MSFT, NVDA"
    raw = st.text_input("Tickers (comma-separated)", value=default)
    tickers = [t.strip().upper() for t in raw.split(",") if t.strip()]
    period = st.selectbox("Period", ["6mo", "1y", "2y", "5y"], index=1)
    if tickers:
        hist = yf_history(tickers, period=period)
        st.markdown("#### Normalized Performance")
        norm = hist / hist.iloc[0] * 100.0
        st.line_chart(norm)

        st.markdown("#### Latest Snapshot")
        info_rows = []
        for t in tickers:
            try:
                ii = yf_info(t)
                info_rows.append({
                    "Ticker": t,
                    "Name": ii.get("shortName", t),
                    "Price": ii.get("currentPrice", None),
                    "MarketCap(USD)": ii.get("marketCap", None),
                    "PE": ii.get("trailingPE", None),
                    "ROE": ii.get("returnOnEquity", None),
                    "RevGrowth": ii.get("revenueGrowth", None),
                })
            except Exception:
                pass
        st.dataframe(pd.DataFrame(info_rows))

# ---------- Portfolio ----------
elif page == "Portfolio":
    st.header("My Portfolio")
    left, right = st.columns([1.2, 1])
    with left:
        st.subheader("Add Investment")
        with st.form("add_hold"):
            t = st.text_input("Ticker", value="AAPL")
            qty = st.number_input("Quantity", value=10.0, step=1.0)
            bp = st.number_input("Purchase Price (optional)", value=0.0, step=0.01)
            submitted = st.form_submit_button("Add")
        if submitted and t:
            st.session_state.holdings.append({"ticker": t.upper(), "qty": qty, "buy_price": bp})
            st.success(f"Added {qty} of {t.upper()}")
    with right:
        up = st.file_uploader("Upload CSV (Ticker,Qty,BuyPrice optional)", type="csv")
        if up is not None:
            dfu = pd.read_csv(up)
            for _, r in dfu.iterrows():
                st.session_state.holdings.append({
                    "ticker": str(r["Ticker"]).upper(),
                    "qty": float(r["Qty"]),
                    "buy_price": float(r.get("BuyPrice", 0))
                })
            st.success("Holdings imported.")

    st.subheader("Your Holdings")
    if not st.session_state.holdings:
        st.info("No holdings yet.")
    else:
        hd = pd.DataFrame(st.session_state.holdings)
        tickers = list({x["ticker"] for x in st.session_state.holdings})
        prices = yf_history(tickers, period="5d").iloc[-1]
        rows = []
        total_val = 0.0
        invested = 0.0
        for h in st.session_state.holdings:
            t = h["ticker"]
            qty = float(h["qty"])
            bp = float(h["buy_price"])
            px = float(prices.get(t, np.nan))
            val = qty * px if not np.isnan(px) else np.nan
            rows.append({
                "Ticker": t, "Qty": qty, "Price": px, "Value": val,
                "BuyPrice": bp,
                "UnrealizedPnL": (val - qty*bp) if (bp > 0 and not np.isnan(val)) else np.nan
            })
            if not np.isnan(val):
                total_val += val
            invested += (bp*qty if bp>0 else 0)
        out = pd.DataFrame(rows)
        st.dataframe(out)
        st.markdown("---")
        st.markdown(f"**Total Value:** ${total_val:,.2f}")
        if invested > 0:
            st.markdown(f"**Invested:** ${invested:,.2f}  |  **Unrealized P/L:** {total_val - invested:,+.2f}")

        st.markdown("#### Top Holdings by Value")
        pie = out.dropna(subset=["Value"]).groupby("Ticker")["Value"].sum().reset_index()
        if not pie.empty:
            fig = px.pie(pie, names="Ticker", values="Value")
            st.plotly_chart(fig, use_container_width=True)

# ---------- Analysis (AI + decomposition) ----------
elif page == "Analysis":
    st.header("AI Insights & Decomposition")
    colA, colB = st.columns([1,1])

    with colA:
        st.subheader("AI Summary")
        text_src = st.text_area("Paste text (e.g., market summary or report excerpt) or upload a PDF below", height=150)
        up_pdf = st.file_uploader("Upload PDF (optional)", type="pdf", key="pdf_ai")
        if up_pdf is not None and not text_src:
            try:
                reader = PdfReader(up_pdf)
                text_src = "\n".join([p.extract_text() or "" for p in reader.pages])[:6000]
                st.caption(f"Loaded {len(text_src)} characters from PDF.")
            except Exception as e:
                st.error(f"PDF error: {e}")

        if HAVE_OPENAI:
            try:
                openai.api_key = st.secrets["openai"]["api_key"]
            except Exception:
                openai.api_key = None

        if st.button("Generate Insight"):
            if not text_src:
                st.warning("Provide text or PDF content first.")
            else:
                with st.spinner("Generating insight..."):
                    if HAVE_OPENAI and openai.api_key:
                        try:
                            resp = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[
                                    {"role":"system","content":"You are a concise financial analyst."},
                                    {"role":"user","content":f"Summarize and give 3 risks + 3 opportunities:\n{text_src[:5000]}"},
                                ],
                                max_tokens=300, temperature=0.4
                            )
                            st.success("AI summary")
                            st.write(resp.choices[0].message.content)
                        except Exception as e:
                            st.error(f"OpenAI error: {e}")
                    else:
                        st.info("OpenAI key not configured. Showing template summary.")
                        st.write(textwrap.dedent("""
                            - Trend: risk-on; breadth improving in large-cap tech.
                            - Risks: policy path uncertainty, margin compression, funding stress.
                            - Opportunities: quality compounders, cash generative firms, low leverage.
                        """))

    with colB:
        st.subheader("Simple Decomposition")
        t = st.text_input("Ticker for decomposition", value="AAPL")
        hist = yf_history(t, period="2y").dropna()
        if not hist.empty:
            s = hist.squeeze()
            trend = s.rolling(30, min_periods=5).mean()
            resid = s - trend
            chart = pd.DataFrame({"Price": s, "Trend(30d MA)": trend, "Residual": resid})
            st.line_chart(chart[["Price","Trend(30d MA)"]])
            st.markdown("Residual (Price - Trend)")
            st.line_chart(chart[["Residual"]])

        st.subheader("Signal Snapshot")
        if not hist.empty:
            last = float(s.iloc[-1])
            ma50 = float(s.rolling(50).mean().iloc[-1])
            ma200 = float(s.rolling(200).mean().iloc[-1])
            st.write(f"Price: {last:.2f} | MA50: {ma50:.2f} | MA200: {ma200:.2f}")
            signal = "Bullish (MA50>MA200)" if ma50 > ma200 else "Cautious/Neutral"
            st.write("Signal:", signal)

# ---------- News ----------
elif page == "News":
    st.header("Financial News")
    sources = {
        "Reuters Business": "http://feeds.reuters.com/reuters/businessNews",
        "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "Bloomberg ETF Report": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    }
    colf1, colf2, colf3 = st.columns([1,1,1])
    with colf1:
        src = st.selectbox("Source", list(sources.keys()))
    with colf2:
        index_filter = st.selectbox("Filter by Index", ["All", "S&P 500", "NASDAQ", "Dow Jones"])
    with colf3:
        crypto_filter = st.selectbox("Filter by Crypto", ["All", "Bitcoin", "Ethereum"])

    q = st.text_input("Search keyword", value="")
    parsed = feedparser.parse(sources[src])
    if not parsed.entries:
        st.info("No articles available.")
    else:
        count = 0
        for e in parsed.entries:
            title = e.get("title","")
            summ = e.get("summary","")
            link = e.get("link","#")
            txt = (title + " " + summ).lower()
            if q and q.lower() not in txt:
                continue
            if index_filter != "All" and index_filter.lower().split()[0] not in txt:
                pass
            if crypto_filter == "Bitcoin" and "bitcoin" not in txt:
                continue
            if crypto_filter == "Ethereum" and "ethereum" not in txt:
                continue
            st.markdown(f'**[{title}]({link})**')
            st.caption(e.get("published",""))
            st.write(summ[:400] + ("…" if len(summ)>400 else ""))
            st.markdown("---")
            count += 1
        if count == 0:
            st.info("No matches for your filters.")

# ---------- Alerts ----------
elif page == "Alerts":
    st.header("Custom Alerts")
    with st.form("new_alert"):
        t = st.text_input("Ticker", value="AAPL")
        op = st.selectbox("Condition", [">=", "<="], index=0)
        thr = st.number_input("Price threshold", value=200.0, step=1.0)
        ok = st.form_submit_button("Create Alert")
    if ok and t:
        st.session_state.alerts.append({"ticker": t.upper(), "operator": op, "threshold": float(thr)})
        st.success("Alert created.")

    st.subheader("Your Alerts")
    if not st.session_state.alerts:
        st.info("No alerts yet.")
    else:
        st.table(pd.DataFrame(st.session_state.alerts))

        st.subheader("Triggered (now)")
        trig = []
        for a in st.session_state.alerts:
            px, _, _ = last_price_change(a["ticker"])
            if px is None:
                continue
            if a["operator"] == ">=" and px >= a["threshold"]:
                trig.append({**a, "price": px})
            if a["operator"] == "<=" and px <= a["threshold"]:
                trig.append({**a, "price": px})
        if trig:
            st.success("Some alerts are currently triggered:")
            st.dataframe(pd.DataFrame(trig))
        else:
            st.write("No triggers at this moment.")

# ---------- Community ----------
elif page == "Community":
    st.header("PSPFinance Community")
    c1, c2 = st.columns([1.2, 1])
    with c1:
        with st.form("new_post"):
            author = st.text_input("Your name or email", value="testuser@example.com")
            title = st.text_input("Post title", value="")
            category = st.selectbox("Category", ["Global Trends", "Technology", "Predictions", "Portfolio"])
            body = st.text_area("Write your post", height=150)
            post = st.form_submit_button("Create Post")
        if post and title and body:
            st.session_state.posts.insert(0, {
                "author": author,
                "title": title,
                "category": category,
                "body": body,
                "ts": pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            })
            st.success("Post published.")

    with c2:
        st.markdown("Filter")
        cat = st.selectbox("Category", ["All", "Global Trends", "Technology", "Predictions", "Portfolio"])
        key = st.text_input("Search keyword", value="")

    st.markdown("---")
    if not st.session_state.posts:
        st.info("No posts yet.")
    else:
        for p in st.session_state.posts:
            if cat != "All" and p["category"] != cat:
                continue
            txt = (p["title"] + " " + p["body"]).lower()
            if key and key.lower() not in txt:
                continue
            st.markdown(f"**{p['title']}**  —  {p['category']}")
            st.caption(f"{p['author']} • {p['ts']}")
            st.write(p["body"])
            st.markdown("---")

