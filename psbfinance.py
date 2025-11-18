# pspfinance.py
# PSP Finance Intelligence Terminal — fast, professional, complete

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="PSP Finance", layout="wide")

ALPHA_KEY = "79T4YLBTP8L9E9FK"

# --------------------------
# Utilities and performance
# --------------------------
def fmt_big(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "–"
    try:
        x = float(x)
    except Exception:
        return "–"
    if abs(x) >= 1e12: return f"{x/1e12:.2f}T"
    if abs(x) >= 1e9:  return f"{x/1e9:.2f}B"
    if abs(x) >= 1e6:  return f"{x/1e6:.2f}M"
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
def yf_prices(symbol: str, period="1y", interval="1d"):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, threads=False)
        if isinstance(df, pd.DataFrame) and not df.empty:
            df = df.reset_index()
        return df
    except Exception:
        return pd.DataFrame()

def alpha_json(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

@st.cache_data(show_spinner=False)
def alpha_overview(symbol: str) -> dict:
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_KEY}"
    data = alpha_json(url)
    return data if data.get("Name") else {}

@st.cache_data(show_spinner=False)
def alpha_timeseries_daily(symbol: str) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_KEY}"
    js = alpha_json(url)
    ts = js.get("Time Series (Daily)", {})
    if not ts: return pd.DataFrame()
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

@st.cache_data(show_spinner=False)
def alpha_income(symbol: str) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={symbol}&apikey={ALPHA_KEY}"
    js = alpha_json(url)
    df = pd.DataFrame(js.get("annualReports", []))
    return df

@st.cache_data(show_spinner=False)
def alpha_balance(symbol: str) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={symbol}&apikey={ALPHA_KEY}"
    js = alpha_json(url)
    df = pd.DataFrame(js.get("annualReports", []))
    return df

@st.cache_data(show_spinner=False)
def alpha_cashflow(symbol: str) -> pd.DataFrame:
    url = f"https://www.alphavantage.co/query?function=CASH_FLOW&symbol={symbol}&apikey={ALPHA_KEY}"
    js = alpha_json(url)
    df = pd.DataFrame(js.get("annualReports", []))
    return df

def get_prices(symbol: str, period="1y", interval="1d"):
    df = yf_prices(symbol, period=period, interval=interval)
    if df.empty or "Close" not in df.columns:
        df = alpha_timeseries_daily(symbol)
    return df

# --------------------------
# Homepage
# --------------------------
st.title("PSP Finance Intelligence Terminal")
st.subheader("Where analysts turn data into decisions")
st.markdown("""
A professional-grade dashboard for market intelligence, multi-year fundamentals, valuation analytics, peer comparisons, regulatory filings, and curated news.
Built for clarity, speed, and practical insight—analyze companies, markets, and trends in one place.
""")

section = st.sidebar.radio("Navigate", [
    "Home", "Company Search", "AI Comparison", "SEC Filings", "News Feed", "Global Markets", "Portfolio"
], key="nav")

if section == "Home":
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Quick start")
        st.write("- Company Search for fundamentals and charts")
        st.write("- AI Comparison for side-by-side metrics")
        st.write("- SEC Filings viewer for core documents")
    with col2:
        st.markdown("### Capabilities")
        st.write("- Up to 10–15 years of statements via Alpha Vantage")
        st.write("- Valuation, profitability, liquidity, growth ratios")
        st.write("- Embedded SEC document pages")
    with col3:
        st.markdown("### Stability")
        st.write("- Caching to avoid re-fetching")
        st.write("- Timeouts to prevent long blocking")
        st.write("- Fallbacks across sources")

# --------------------------
# Company Search
# --------------------------
if section == "Company Search":
    st.header("Company search and detailed analysis")
    ticker = st.text_input("Enter ticker (e.g., AAPL, MSFT, AIR.PA)", key="tkr").strip().upper()
    years_requested = st.slider("Years of history", min_value=5, max_value=15, value=10, step=1, key="yrs")

    tabs = st.tabs(["Overview", "Financials", "Ratios", "Peers", "Summary"])
    if ticker:
        # Overview: try yfinance, fallback to Alpha overview
        yft = yf.Ticker(ticker)
        info = safe_info(yft)
        if not info or "longName" not in info:
            ov = alpha_overview(ticker)
            info = {
                "longName": ov.get("Name", ticker),
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

        # Overview tab
        with tabs[0]:
            st.subheader(f"Overview — {info.get('longName', ticker)} ({ticker})")
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.write(f"Sector: {info.get('sector', '–')}")
                st.write(f"Industry: {info.get('industry', '–')}")
                st.write(f"Description: {info.get('description', '–')}")
            with c2:
                st.write(f"Market capitalization: {fmt_big(info.get('marketCap'))}")
                st.write(f"Beta: {info.get('beta', '–')}")
            with c3:
                st.write(f"Trailing P/E: {info.get('trailingPE', '–')}")
                st.write(f"Price/Sales (TTM): {info.get('priceToSalesTrailing12Months', '–')}")
                st.write(f"EV/EBITDA: {info.get('enterpriseToEbitda', '–')}")
            with c4:
                st.write(f"Dividend yield: {pct(info.get('dividendYield'))}")

            st.markdown("#### Price performance")
            period = st.selectbox("Period", ["1mo","3mo","6mo","1y","2y","5y"], index=3, key="pp")
            interval = st.selectbox("Interval", ["1d","1wk"], index=0, key="pi")
            prices = get_prices(ticker, period=period, interval=interval)
            if prices.empty or "Close" not in prices.columns:
                st.warning("Price data unavailable.")
            else:
                fig = px.line(prices, x="Date", y="Close", title=f"{ticker} closing price ({period})")
                st.plotly_chart(fig, use_container_width=True)

        # Financials tab (10–15 years via Alpha Vantage; Yahoo limited)
        with tabs[1]:
            st.subheader("Financial statements (annual)")
            st.caption("Select years above to limit history and improve performance.")
            inc_av = alpha_income(ticker)
            bal_av = alpha_balance(ticker)
            cf_av  = alpha_cashflow(ticker)

            def limit_years(df, date_col="fiscalDateEnding", n=10):
                if df.empty: return df
                df = df.copy()
                if date_col in df.columns:
                    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                    df = df.sort_values(date_col, ascending=False).head(n)
                return df

            inc = limit_years(inc_av, n=years_requested)
            bal = limit_years(bal_av, n=years_requested)
            cf  = limit_years(cf_av,  n=years_requested)

            colA, colB, colC = st.columns(3)
            with colA:
                st.markdown("Income statement")
                if inc.empty:
                    st.info("Unavailable from Alpha Vantage.")
                else:
                    st.dataframe(inc)
                    st.download_button("Download income (CSV)", inc.to_csv(index=False).encode(), "income_statement.csv", key="dl_inc")
            with colB:
                st.markdown("Balance sheet")
                if bal.empty:
                    st.info("Unavailable from Alpha Vantage.")
                else:
                    st.dataframe(bal)
                    st.download_button("Download balance (CSV)", bal.to_csv(index=False).encode(), "balance_sheet.csv", key="dl_bal")
            with colC:
                st.markdown("Cash flow statement")
                if cf.empty:
                    st.info("Unavailable from Alpha Vantage.")
                else:
                    st.dataframe(cf)
                    st.download_button("Download cash flow (CSV)", cf.to_csv(index=False).encode(), "cash_flow.csv", key="dl_cf")

            st.markdown("#### Growth trends")
            if not inc.empty and "totalRevenue" in inc.columns and "fiscalDateEnding" in inc.columns:
                gdf = inc[["fiscalDateEnding", "totalRevenue"]].dropna()
                gdf = gdf.sort_values("fiscalDateEnding")
                fig_g = px.bar(gdf, x="fiscalDateEnding", y="totalRevenue", title="Total revenue (annual)")
                st.plotly_chart(fig_g, use_container_width=True)
            if not inc.empty and "netIncome" in inc.columns and "fiscalDateEnding" in inc.columns:
                ndf = inc[["fiscalDateEnding", "netIncome"]].dropna()
                ndf = ndf.sort_values("fiscalDateEnding")
                fig_n = px.bar(ndf, x="fiscalDateEnding", y="netIncome", title="Net income (annual)")
                st.plotly_chart(fig_n, use_container_width=True)

        # Ratios tab: valuation, profitability, liquidity, growth
        with tabs[2]:
            st.subheader("Ratios and decomposition")
            # Build ratios from Alpha statements when possible
            def safe_num(x):
                try: return float(x)
                except: return None

            # Pick latest row for single-period ratios
            latest_inc = inc.head(1).iloc[0] if not inc.empty else pd.Series()
            latest_bal = bal.head(1).iloc[0] if not bal.empty else pd.Series()
            latest_cf  = cf.head(1).iloc[0]  if not cf.empty  else pd.Series()

            revenue = safe_num(latest_inc.get("totalRevenue"))
            net_income = safe_num(latest_inc.get("netIncome"))
            ebitda = safe_num(latest_inc.get("ebitda"))
            shares = safe_num(latest_bal.get("commonStockSharesOutstanding"))
            total_assets = safe_num(latest_bal.get("totalAssets"))
            total_equity = safe_num(latest_bal.get("totalShareholderEquity"))
            current_assets = safe_num(latest_bal.get("totalCurrentAssets"))
            current_liabilities = safe_num(latest_bal.get("totalCurrentLiabilities"))
            cash = safe_num(latest_bal.get("cashAndCashEquivalentsAtCarryingValue"))
            op_cashflow = safe_num(latest_cf.get("operatingCashflow"))
            capex = safe_num(latest_cf.get("capitalExpenditures"))

            market_cap = info.get("marketCap")
            pe = info.get("trailingPE")
            ps = info.get("priceToSalesTrailing12Months")
            ev_ebitda = info.get("enterpriseToEbitda")

            # Profitability
            profit_margin = (net_income / revenue) if (net_income and revenue) else None
            roe = (net_income / total_equity) if (net_income and total_equity) else None
            roa = (net_income / total_assets) if (net_income and total_assets) else None
            op_margin = None  # if Alpha inc_op_income present: operatingIncome / totalRevenue

            # Liquidity
            current_ratio = (current_assets / current_liabilities) if (current_assets and current_liabilities) else None
            quick_ratio = None  # would require inventory field; Alpha has inventory in balance sheet sometimes
            cash_ratio = (cash / current_liabilities) if (cash and current_liabilities) else None

            # Growth (YoY using last two rows if available)
            def yoy(series_name, df):
                if df.empty or series_name not in df.columns: return None
                s = df[[series_name, "fiscalDateEnding"]].dropna().sort_values("fiscalDateEnding")
                if len(s) < 2: return None
                a, b = safe_num(s.iloc[-2][series_name]), safe_num(s.iloc[-1][series_name])
                if a is None or a == 0 or b is None: return None
                return (b - a) / abs(a)

            revenue_yoy = yoy("totalRevenue", inc)
            net_income_yoy = yoy("netIncome", inc)
            op_cf_yoy = yoy("operatingCashflow", cf)

            # Valuation plot
            val_df = pd.DataFrame({
                "Metric": ["P/E", "Price/Sales (TTM)", "EV/EBITDA"],
                "Value": [pe, ps, ev_ebitda]
            }).dropna()
            if val_df.empty:
                st.info("Valuation metrics unavailable from current sources.")
            else:
                st.plotly_chart(px.bar(val_df, x="Metric", y="Value", title="Valuation metrics"), use_container_width=True)

            # Profitability plot
            prof_df = pd.DataFrame({
                "Metric": ["Profit margin", "Return on equity", "Return on assets"],
                "Value": [profit_margin, roe, roa]
            }).dropna()
            if not prof_df.empty:
                prof_df["Value_pct"] = prof_df["Value"] * 100
                fig_prof = px.bar(prof_df, x="Metric", y="Value_pct", title="Profitability (%)")
                fig_prof.update_yaxes(title="Percent")
                st.plotly_chart(fig_prof, use_container_width=True)

            # Liquidity plot
            liq_df = pd.DataFrame({
                "Metric": ["Current ratio", "Cash ratio"],
                "Value": [current_ratio, cash_ratio]
            }).dropna()
            if not liq_df.empty:
                st.plotly_chart(px.bar(liq_df, x="Metric", y="Value", title="Liquidity"), use_container_width=True)

            # Growth plot
            growth_df = pd.DataFrame({
                "Metric": ["Revenue YoY", "Net income YoY", "Operating cash flow YoY"],
                "Value": [revenue_yoy, net_income_yoy, op_cf_yoy]
            }).dropna()
            if not growth_df.empty:
                growth_df["Value_pct"] = growth_df["Value"] * 100
                fig_g = px.bar(growth_df, x="Metric", y="Value_pct", title="Growth (%)")
                fig_g.update_yaxes(title="Percent")
                st.plotly_chart(fig_g, use_container_width=True)

            st.markdown("Key facts")
            st.write(f"Market capitalization: {fmt_big(market_cap)}")
            st.write(f"P/E: {pe if pe is not None else '–'}")
            st.write(f"Price/Sales (TTM): {ps if ps is not None else '–'}")
            st.write(f"EV/EBITDA: {ev_ebitda if ev_ebitda is not None else '–'}")
            if op_cashflow is not None and capex is not None:
                fcf = op_cashflow - abs(capex)
                st.write(f"Free cash flow: {fmt_big(fcf)}")

        # Peers tab
        with tabs[3]:
            st.subheader("Peer comparison")
            peer_input = st.text_input("Enter peer tickers (comma-separated)", key="peers")
            peers = [p.strip().upper() for p in peer_input.split(",") if p.strip()]
            rows = []
            for tk in peers:
                try:
                    p = yf.Ticker(tk)
                    pi = safe_info(p)
                    if not pi or "longName" not in pi:
                        pov = alpha_overview(tk)
                        pi = {
                            "longName": pov.get("Name", tk),
                            "sector": pov.get("Sector"),
                            "industry": pov.get("Industry"),
                            "marketCap": float(pov.get("MarketCapitalization")) if pov.get("MarketCapitalization") else None,
                            "trailingPE": float(pov.get("PERatio")) if pov.get("PERatio") else None,
                            "priceToSalesTrailing12Months": float(pov.get("PriceToSalesRatioTTM")) if pov.get("PriceToSalesRatioTTM") else None,
                            "enterpriseToEbitda": float(pov.get("EVToEBITDA")) if pov.get("EVToEBITDA") else None
                        }
                    rows.append({
                        "Ticker": tk,
                        "Name": pi.get("longName", tk),
                        "Sector": pi.get("sector", "–"),
                        "Industry": pi.get("industry", "–"),
                        "MarketCap": pi.get("marketCap", None),
                        "P/E": pi.get("trailingPE", None),
                        "Price/Sales": pi.get("priceToSalesTrailing12Months", None),
                        "EV/EBITDA": pi.get("enterpriseToEbitda", None)
                    })
                except Exception:
                    pass
            peer_df = pd.DataFrame(rows)
            if peer_df.empty:
                st.info("Add peer tickers to see comparisons.")
            else:
                st.dataframe(peer_df)
                for col in ["MarketCap", "P/E", "Price/Sales", "EV/EBITDA"]:
                    sub = peer_df[["Ticker", col]].dropna()
                    if not sub.empty:
                        st.plotly_chart(px.bar(sub, x="Ticker", y=col, title=f"{col} comparison"), use_container_width=True)

        # Summary tab
        with tabs[4]:
            st.subheader("Analyst-style summary")
            lines = []
            lines.append(f"{info.get('longName', ticker)} operates in {info.get('sector', '–')} with a focus on {info.get('industry', '–')}.")
            lines.append(f"Market capitalization: {fmt_big(info.get('marketCap'))}. Valuation: P/E={info.get('trailingPE','–')}, Price/Sales={info.get('priceToSalesTrailing12Months','–')}, EV/EBITDA={info.get('enterpriseToEbitda','–')}.")
            lines.append(f"Profitability: margin {pct(profit_margin) if 'profit_margin' in locals() and profit_margin is not None else '–'}, ROE {pct(roe) if 'roe' in locals() and roe is not None else '–'}, ROA {pct(roa) if 'roa' in locals() and roa is not None else '–'}.")
            lines.append(f"Liquidity: current ratio {current_ratio if 'current_ratio' in locals() and current_ratio is not None else '–'}, cash ratio {cash_ratio if 'cash_ratio' in locals() and cash_ratio is not None else '–'}.")
            lines.append(f"Growth: revenue YoY {pct(revenue_yoy) if revenue_yoy is not None else '–'}, net income YoY {pct(net_income_yoy) if net_income_yoy is not None else '–'}.")
            lines.append(f"Free cash flow and dividend yield contribute to capital returns where available.")
            lines.append("Overall positioning reflects valuation, margin durability, cash generation, liquidity, and growth dynamics.")
            st.info(" ".join(lines))

# --------------------------
# AI Comparison (multi-ticker)
# --------------------------
if section == "AI Comparison":
    st.header("Multi-ticker comparison")
    tickers = st.text_input("Enter tickers (comma-separated)", key="cmp").strip()
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
                        "enterpriseToEbitda": float(ov.get("EVToEBITDA")) if ov.get("EVToEBITDA") else None
                    }
                data.append({
                    "Ticker": tk,
                    "Name": ii.get("longName", tk),
                    "Sector": ii.get("sector", "–"),
                    "MarketCap": ii.get("marketCap", None),
                    "P/E": ii.get("trailingPE", None),
                    "Price/Sales": ii.get("priceToSalesTrailing12Months", None),
                    "EV/EBITDA": ii.get("enterpriseToEbitda", None)
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

# --------------------------
# SEC Filings with embedded documents
# --------------------------
if section == "SEC Filings":
    st.header("SEC filings viewer")
    sec_ticker = st.text_input("Enter a US ticker (e.g., AAPL, MSFT, TSLA)", key="sec").strip().upper()
    load_filings = st.button("Load recent filings", key="load_sec")
    if sec_ticker and load_filings:
        base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={sec_ticker}&type=&owner=exclude&count=40&action=getcompany"
        try:
            resp = requests.get(base_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            rows = soup.find_all("tr")
            docs = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    form_type = cols[0].text.strip()
                    filing_date = cols[3].text.strip()
                    link_tag = cols[1].find("a")
                    if link_tag and form_type in ["10-K", "10-Q", "8-K", "S-1", "DEF 14A"]:
                        filing_url = "https://www.sec.gov" + link_tag["href"]
                        docs.append({"type": form_type, "date": filing_date, "url": filing_url})
            if not docs:
                st.warning("No recent core filings found.")
            else:
                for i, d in enumerate(docs[:10]):
                    st.markdown(f"- {d['type']} filed on {d['date']} — [Open filing]({d['url']})")
                st.markdown("#### View a filing document inline")
                choice = st.selectbox("Select filing to view", [f"{d['type']} ({d['date']})" for d in docs[:10]], key="sec_choice")
                if choice:
                    sel = docs[[f"{d['type']} ({d['date']})" for d in docs[:10]].index(choice)]
                    # Many filing pages have a 'Documents' link that contains the HTML filing; embed that page
                    st.components.v1.iframe(sel["url"], height=600, scrolling=True)
        except requests.exceptions.RequestException:
            st.error("Network error while retrieving SEC filings.")
        except Exception:
            st.error("Unexpected error. Try again.")

# --------------------------
# News Feed
# --------------------------
if section == "News Feed":
    st.header("News feed")
    news_ticker = st.text_input("Ticker for news (e.g., AAPL, MSFT)", key="news").strip().upper()
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
    gm_tickers = st.text_input("Symbols (comma-separated): e.g., ^GSPC, ^NDX, EURUSD=X, CL=F", key="gm").strip()
    syms = [s.strip() for s in gm_tickers.split(",") if s.strip()]
    for sym in syms:
        df = get_prices(sym, period="1y", interval="1d")
        if df.empty:
            st.info(f"No data for {sym}.")
        else:
            st.plotly_chart(px.line(df, x="Date", y="Close", title=f"{sym} closing price (1y)"), use_container_width=True)

# --------------------------
# Portfolio
# --------------------------
if section == "Portfolio":
    st.header("Portfolio tracker")
    pt = st.text_input("Holdings (comma-separated tickers)", key="pf").strip()
    holdings = [h.strip().upper() for h in pt.split(",") if h.strip()]
    if holdings:
        rows = []
        for tk in holdings:
            df = get_prices(tk, period="1y", interval="1d")
            if df.empty or "Close" not in df.columns: continue
            last = df["Close"].iloc[-1]
            rows.append({"Ticker": tk, "Last close": last})
        if rows:
            st.dataframe(pd.DataFrame(rows))
        else:
            st.info("No price data for given tickers.")
