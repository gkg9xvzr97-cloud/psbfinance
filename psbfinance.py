# pspfinance.py
# PSP Finance Intelligence Terminal — professional build

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

# --------------------------
# Configuration and constants
# --------------------------
st.set_page_config(page_title="PSP Finance", layout="wide")

# Replace with your real Alpha Vantage key
ALPHA_KEY = "79T4YLBTP8L9E9FK"

# --------------------------
# Homepage copy
# --------------------------
st.title("PSP Finance Intelligence Terminal")
st.subheader("Where analysts turn data into decisions")

st.markdown("""
PSP Finance is a professional-grade dashboard for real-time market intelligence, multi-year fundamentals, valuation analytics, peer comparisons, regulatory filings, and curated news.
It is built for clarity, speed, and practical insight—so you can analyze companies, markets, and trends in one place.
""")

section = st.sidebar.radio(
    "Navigate",
    ["Home", "Company Search", "AI Comparison", "SEC Filings", "News Feed", "Global Markets", "Portfolio"],
    key="nav_radio"
)

# --------------------------
# Utilities and fallbacks
# --------------------------
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
        info = tk.info
        return info if isinstance(info, dict) else {}
    except Exception:
        return {}

@st.cache_data(show_spinner=False)
def load_price_history_yf(ticker: str, period="1y", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, threads=False)
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = df.reset_index()
        return df
    except Exception:
        return pd.DataFrame()

def alpha_overview(symbol: str) -> dict:
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data if data.get("Name") else {}
    except Exception:
        pass
    return {}

def alpha_daily(symbol: str) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            js = r.json()
            ts = js.get("Time Series (Daily)", {})
            if ts:
                df = pd.DataFrame.from_dict(ts, orient="index")
                df.index = pd.to_datetime(df.index)
                df = df.rename(columns={
                    "1. open": "Open", "2. high": "High", "3. low": "Low",
                    "4. close": "Close", "5. volume": "Volume"
                }).sort_index()
                df = df.reset_index().rename(columns={"index": "Date"})
                for col in ["Open","High","Low","Close","Volume"]:
                    df[col] = pd.to_numeric(df[col], errors="coerce")
                return df
    except Exception:
        pass
    return pd.DataFrame()

def get_prices_with_fallback(symbol: str, period="1y", interval="1d"):
    df = load_price_history_yf(symbol, period=period, interval=interval)
    if df.empty or "Close" not in df.columns:
        df = alpha_daily(symbol)
    return df

# --------------------------
# Home section
# --------------------------
if section == "Home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Quick start")
        st.write("- Use Company Search for fundamentals and charts")
        st.write("- Add peers in AI Comparison for side-by-side analysis")
        st.write("- Review filings in SEC Filings; track news via News Feed")
    with col2:
        st.markdown("### Why it helps")
        st.write("- Multi-year statements with export")
        st.write("- Clear valuation and profitability decomposition")
        st.write("- Concise analyst-style summaries")
    with col3:
        st.markdown("### Roadmap")
        st.write("- Options implied volatility and skew")
        st.write("- Corporate bonds and CDS spreads")
        st.write("- Macro rates and alerts")

# --------------------------
# Company Search section
# --------------------------
if section == "Company Search":
    st.header("Company search and detailed analysis")

    query = st.text_input(
        "Enter a ticker or name (e.g., AAPL, MSFT, AIR.PA):",
        key="company_search_input"
    ).strip().upper()

    tabs = st.tabs(["Overview", "Financials", "Valuation and profitability", "Peers", "Summary"])

    if query:
        # Primary: Yahoo Finance
        stock = yf.Ticker(query)
        info = safe_info(stock)

        # Fallback: Alpha Vantage Overview
        if not info or "longName" not in info:
            ov = alpha_overview(query)
            if ov:
                info = {
                    "longName": ov.get("Name", query),
                    "sector": ov.get("Sector"),
                    "industry": ov.get("Industry"),
                    "marketCap": float(ov.get("MarketCapitalization")) if ov.get("MarketCapitalization") else None,
                    "beta": ov.get("Beta"),
                    "trailingPE": float(ov.get("PERatio")) if ov.get("PERatio") else None,
                    "priceToSalesTrailing12Months": float(ov.get("PriceToSalesRatioTTM")) if ov.get("PriceToSalesRatioTTM") else None,
                    "enterpriseToEbitda": float(ov.get("EVToEBITDA")) if ov.get("EVToEBITDA") else None,
                    "returnOnEquity": float(ov.get("ReturnOnEquityTTM")) if ov.get("ReturnOnEquityTTM") else None,
                    "dividendYield": float(ov.get("DividendYield")) if ov.get("DividendYield") else None,
                    "description": ov.get("Description")
                }
            else:
                info = info  # keep whatever exists (even empty)

        # --------------------------
        # Overview tab
        # --------------------------
        with tabs[0]:
            st.subheader(f"Overview — {info.get('longName', query)} ({query})")

            overview_cols = st.columns(4)
            with overview_cols[0]:
                st.write(f"Sector: {info.get('sector', '–')}")
                st.write(f"Industry: {info.get('industry', '–')}")
                st.write(f"Description: {info.get('description', '–')}")
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
            period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3, key="price_period")
            interval = st.selectbox("Interval", ["1d", "1wk"], index=0, key="price_interval")
            prices = get_prices_with_fallback(query, period=period, interval=interval)
            if prices.empty or "Close" not in prices.columns:
                st.warning("Price data unavailable from both sources.")
            else:
                fig_price = px.line(prices, x="Date", y="Close", title=f"{query} closing price ({period})")
                st.plotly_chart(fig_price, use_container_width=True)

        # --------------------------
        # Financials tab
        # --------------------------
        with tabs[1]:
            st.subheader("Financial statements (annual)")
            fin_cols = st.columns(3)

            # Income statement
            with fin_cols[0]:
                st.markdown("Income statement")
                inc = stock.financials if isinstance(stock.financials, pd.DataFrame) else pd.DataFrame()
                if inc.empty:
                    st.info("Income statement unavailable via Yahoo Finance.")
                else:
                    st.dataframe(inc)
                    st.download_button("Download income (CSV)", inc.to_csv().encode(), "income_statement.csv", key="dl_income")

            # Balance sheet
            with fin_cols[1]:
                st.markdown("Balance sheet")
                bal = stock.balance_sheet if isinstance(stock.balance_sheet, pd.DataFrame) else pd.DataFrame()
                if bal.empty:
                    st.info("Balance sheet unavailable via Yahoo Finance.")
                else:
                    st.dataframe(bal)
                    st.download_button("Download balance (CSV)", bal.to_csv().encode(), "balance_sheet.csv", key="dl_balance")

            # Cash flow
            with fin_cols[2]:
                st.markdown("Cash flow statement")
                cf = stock.cashflow if isinstance(stock.cashflow, pd.DataFrame) else pd.DataFrame()
                if cf.empty:
                    st.info("Cash flow statement unavailable via Yahoo Finance.")
                else:
                    st.dataframe(cf)
                    st.download_button("Download cash flow (CSV)", cf.to_csv().encode(), "cash_flow.csv", key="dl_cashflow")

            st.markdown("#### Growth trends (revenue and earnings)")
            earn = stock.earnings if isinstance(stock.earnings, pd.DataFrame) else pd.DataFrame()
            if not earn.empty and set(["Revenue", "Earnings"]).issubset(earn.columns):
                fig_growth = go.Figure()
                fig_growth.add_trace(go.Bar(x=earn.index.astype(str), y=earn["Revenue"], name="Revenue"))
                fig_growth.add_trace(go.Bar(x=earn.index.astype(str), y=earn["Earnings"], name="Earnings"))
                fig_growth.update_layout(barmode="group", title="Revenue and earnings (annual)")
                st.plotly_chart(fig_growth, use_container_width=True)
            else:
                st.info("Revenue/Earnings series unavailable from Yahoo Finance.")

        # --------------------------
        # Valuation and profitability tab
        # --------------------------
        with tabs[2]:
            st.subheader("Valuation and profitability decomposition")

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
                    st.info("Valuation metrics unavailable from current sources.")
                else:
                    fig_val = px.bar(val_df, x="Metric", y="Value", title="Valuation metrics")
                    st.plotly_chart(fig_val, use_container_width=True)

                prof_df = pd.DataFrame({
                    "Metric": ["Profit margin", "Operating margin", "Return on equity", "Return on assets"],
                    "Value": [profit_margin, op_margin, roe, roa]
                }).dropna()
                if prof_df.empty:
                    st.info("Profitability metrics unavailable from current sources.")
                else:
                    prof_df["Value_pct"] = prof_df["Value"] * 100
                    fig_prof = px.bar(prof_df, x="Metric", y="Value_pct", title="Profitability (%)")
                    fig_prof.update_yaxes(title="Percent")
                    st.plotly_chart(fig_prof, use_container_width=True)

            with colB:
                st.markdown("Key facts")
                st.write(f"Market capitalization: {fmt_big(info.get('marketCap'))}")
                st.write(f"Free cash flow: {fmt_big(fcf)}")
                st.write(f"Dividend yield: {pct(info.get('dividendYield'))}")
                st.write(f"Beta: {info.get('beta', '–')}")

            # Simple risk label
            risk_label = "Low"
            if pe is None or info.get("marketCap", 0) == 0:
                risk_label = "Unknown"
            elif isinstance(pe, (int, float)) and pe > 30:
                risk_label = "High"
            elif isinstance(pe, (int, float)) and pe > 15:
                risk_label = "Moderate"
            st.write(f"Risk score: {risk_label}")

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
                    p = yf.Ticker(tk)
                    pi = safe_info(p)
                    # Fallback to Alpha if empty
                    if not pi or "longName" not in pi:
                        pov = alpha_overview(tk)
                        pi = {
                            "longName": pov.get("Name", tk),
                            "sector": pov.get("Sector"),
                            "industry": pov.get("Industry"),
                            "marketCap": float(pov.get("MarketCapitalization")) if pov.get("MarketCapitalization") else None,
                            "trailingPE": float(pov.get("PERatio")) if pov.get("PERatio") else None,
                            "priceToSalesTrailing12Months": float(pov.get("PriceToSalesRatioTTM")) if pov.get("PriceToSalesRatioTTM") else None,
                            "enterpriseToEbitda": float(pov.get("EVToEBITDA")) if pov.get("EVToEBITDA") else None,
                            "profitMargins": None,
                            "operatingMargins": None,
                            "returnOnEquity": float(pov.get("ReturnOnEquityTTM")) if pov.get("ReturnOnEquityTTM") else None,
                            "returnOnAssets": None
                        }
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
                    pass
            peer_df = pd.DataFrame(rows)
            if peer_df.empty:
                st.info("Add peer tickers to see comparisons.")
            else:
                st.dataframe(peer_df)

                cap_df = peer_df[["Ticker", "MarketCap"]].dropna()
                if not cap_df.empty:
                    fig_cap = px.bar(cap_df, x="Ticker", y="MarketCap", title="Market capitalization comparison")
                    st.plotly_chart(fig_cap, use_container_width=True)

                pe_df = peer_df[["Ticker", "P/E"]].dropna()
                if not pe_df.empty:
                    fig_pe = px.bar(pe_df, x="Ticker", y="P/E", title="P/E comparison")
                    st.plotly_chart(fig_pe, use_container_width=True)

                pm_df = peer_df[["Ticker", "ProfitMargin"]].dropna()
                if not pm_df.empty:
                    pm_df["ProfitMargin_pct"] = pm_df["ProfitMargin"] * 100
                    fig_pm = px.bar(pm_df, x="Ticker", y="ProfitMargin_pct", title="Profit margin (%)")
                    fig_pm.update_yaxes(title="Percent")
                    st.plotly_chart(fig_pm, use_container_width=True)

        # --------------------------
        # Summary tab (7 sentences)
        # --------------------------
        with tabs[4]:
            st.subheader("Analyst-style summary")
            lines = []
            lines.append(f"{info.get('longName', query)} operates in {info.get('sector', '–')} with a focus on {info.get('industry', '–')}.")
            lines.append(f"Market capitalization is {fmt_big(info.get('marketCap'))}; core valuation metrics include P/E={info.get('trailingPE', '–')}, Price/Sales={info.get('priceToSalesTrailing12Months', '–')}, and EV/EBITDA={info.get('enterpriseToEbitda', '–')}.")
            lines.append(f"Profitability indicates profit margin {pct(info.get('profitMargins'))} and operating margin {pct(info.get('operatingMargins'))}.")
            lines.append(f"Returns on capital include return on equity {pct(info.get('returnOnEquity'))} and return on assets {pct(info.get('returnOnAssets'))}.")
            lines.append(f"Dividend yield stands at {pct(info.get('dividendYield'))}, while free cash flow is {fmt_big(info.get('freeCashflow'))}.")
            lines.append("Revenue and earnings trends, where available, show the direction of growth across recent periods.")
            lines.append("Overall positioning reflects valuation, margin durability, cash generation, and sector dynamics relative to peers.")
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
                ti = yf.Ticker(tk)
                ii = safe_info(ti)
                if not ii or "longName" not in ii:
                    ov = alpha_overview(tk)
                    ii = {
                        "longName": ov.get("Name", tk),
                        "sector": ov.get("Sector"),
                        "marketCap": float(ov.get("MarketCapitalization")) if ov.get("MarketCapitalization") else None,
                        "trailingPE": float(ov.get("PERatio")) if ov.get("PERatio") else None,
                        "priceToSalesTrailing12Months": float(ov.get("PriceToSalesRatioTTM")) if ov.get("PriceToSalesRatioTTM") else None,
                        "enterpriseToEbitda": float(ov.get("EVToEBITDA")) if ov.get("EVToEBITDA") else None,
                        "profitMargins": None,
                        "operatingMargins": None,
                        "returnOnEquity": float(ov.get("ReturnOnEquityTTM")) if ov.get("ReturnOnEquityTTM") else None,
                        "returnOnAssets": None
                    }
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
            st.info("No data for the given tickers.")
        else:
            st.dataframe(df)

            for col in ["MarketCap", "P/E", "Price/Sales", "EV/EBITDA"]:
                sub = df[["Ticker", col]].dropna()
                if not sub.empty:
                    st.plotly_chart(px.bar(sub, x="Ticker", y=col, title=f"{col} comparison"), use_container_width=True)

            st.markdown("#### Comparison summary")
            # Safe idx operations
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
    sec_ticker = st.text_input("Enter a US ticker (e.g., AAPL, MSFT, TSLA)", key="sec_input").strip().upper()
    if sec_ticker:
        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={sec_ticker}&type=&owner=exclude&count=20&action=getcompany"
        try:
            resp = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"})
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
                st.warning("No recent 10-K, 10-Q or 8-K found.")
        except requests.exceptions.RequestException:
            st.error("Network error while retrieving SEC filings.")
        except Exception:
            st.error("Unexpected error. Please try again.")

# --------------------------
# News Feed
# --------------------------
if section == "News Feed":
    st.header("News feed")
    st.write("Enter a ticker to fetch recent headlines via Yahoo Finance.")
    news_ticker = st.text_input("Ticker for news (e.g., AAPL, MSFT)", key="news_input").strip().upper()
    if news_ticker:
        try:
            tk = yf.Ticker(news_ticker)
            news_items = getattr(tk, "news", [])
            if not news_items:
                st.info("No recent headlines available.")
            else:
                for n in news_items[:15]:
                    title = n.get("title", "")
                    link = n.get("link", "")
                    provider = n.get("publisher", "")
                    st.markdown(f"- {title} — {provider} — [Read]({link})")
        except Exception:
            st.error("Could not load news for this ticker.")

# --------------------------
# Global Markets
# --------------------------
if section == "Global Markets":
    st.header("Global markets")
    st.write("Add indices, FX, commodities, and crypto symbols. Examples: ^GSPC, ^NDX, ^DJI, EURUSD=X, CL=F, GC=F.")
    gm_tickers = st.text_input("Enter symbols (comma-separated)", key="global_input")
    syms = [s.strip() for s in gm_tickers.split(",") if s.strip()]
    for sym in syms:
        st.markdown(f"#### {sym}")
        df = get_prices_with_fallback(sym, period="1y", interval="1d")
        if df.empty:
            st.info("No data.")
        else:
            fig = px.line(df, x="Date", y="Close", title=f"{sym} closing price (1y)")
            st.plotly_chart(fig, use_container_width=True)

# --------------------------
# Portfolio
# --------------------------
if section == "Portfolio":
    st.header("Portfolio tracker")
    pt = st.text_input("Enter holdings (comma-separated), e.g., AAPL, MSFT, NVDA", key="portfolio_input")
    holdings = [h.strip().upper() for h in pt.split(",") if h.strip()]
    if holdings:
        rows = []
        for tk in holdings:
            df = get_prices_with_fallback(tk, period="1y", interval="1d")
            if df.empty or "Close" not in df.columns:
                continue
            last = df["Close"].iloc[-1]
            rows.append({"Ticker": tk, "Last close": last})
        if rows:
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("No price data for the given tickers.")
