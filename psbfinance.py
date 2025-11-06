# app.py (main Streamlit app)
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import feedparser
from PyPDF2 import PdfReader
import openai
from sklearn.decomposition import PCA

# Optional: stauth for login (not fully implemented here)
# import streamlit_authenticator as stauth

# Set page config
st.set_page_config(page_title="PSP Finance Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
pages = [
    "Landing Page", "Ticker Research", "Company Comparison", "Portfolio Analysis",
    "Finance News", "FX & Derivatives", "AI Summary & PDF", "Knowledge Library",
    "Decomposition Demo", "Login/Personalization"
]
selection = st.sidebar.radio("Go to", pages)

# Landing Page Content
if selection == "Landing Page":
    st.title("PSP Finance Dashboard")
    st.image("https://via.placeholder.com/150", width=150)  # Placeholder image
    st.markdown("""
    Welcome to PSP Finance! This interactive dashboard provides tools for stock research, portfolio analysis, market news, FX charts, and more. 
    Use the sidebar to navigate between modules. Each section offers data-driven insights powered by Python libraries (e.g. yfinance) and AI.
    """)

    st.write("Use the sidebar on the left to navigate through the app modules.")
# Ticker Research
if selection == "Ticker Research":
    st.header("Ticker Research")
    ticker_symbol = st.text_input("Enter Stock Ticker (e.g. AAPL)", value="AAPL")
    if ticker_symbol:
        ticker_data = yf.Ticker(ticker_symbol)
        # Fetch fundamental data with caching
        @st.cache_data
        def get_financials(sym):
            t = yf.Ticker(sym)
            return {
                "info": t.info,
                "income": t.financials.T,      # transpose for easier display
                "balance": t.balance_sheet.T,
                "cashflow": t.cashflow.T,
                "history": t.history(period="5y")
            }
        data = get_financials(ticker_symbol)
        
        # Display key info
        st.subheader("Key Metrics")
        info = data["info"]
        cols = st.columns(3)
        with cols[0]:
            st.write(f"**Name:** {info.get('shortName', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        with cols[1]:
            st.write(f"**Market Cap:** ${info.get('marketCap', 0):,.0f}")
            st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
        with cols[2]:
            st.write(f"**Forward EPS:** {info.get('forwardEps', 'N/A')}")
            st.write(f"**52-Week High/Low:** {info.get('fiftyTwoWeekHigh', 0):.2f} / {info.get('fiftyTwoWeekLow', 0):.2f}")
        
        # Display financial statements
        st.subheader("Income Statement (Recent Years)")
        st.dataframe(data["income"])
        st.subheader("Balance Sheet (Recent Years)")
        st.dataframe(data["balance"])
        st.subheader("Cash Flow Statement (Recent Years)")
        st.dataframe(data["cashflow"])
        
        # Price history chart
        st.subheader("Historical Price (5 Years)")
        price_df = data["history"]["Close"]
        price_df.index = price_df.index.date
        st.line_chart(price_df)
# Company Comparison
if selection == "Company Comparison":
    st.header("Company Comparison")
    col1, col2 = st.columns(2)
    with col1:
        sym1 = st.text_input("Ticker 1", value="AAPL")
    with col2:
        sym2 = st.text_input("Ticker 2", value="MSFT")
    if sym1 and sym2:
        tick1 = yf.Ticker(sym1)
        tick2 = yf.Ticker(sym2)
        info1 = tick1.info
        info2 = tick2.info
        # Compute ROE (netIncome/shareholderEquity) if available
        def calc_roe(t):
            ni = t.info.get('netIncomeToCommon', None)
            eq = t.info.get('totalStockholderEquity', None)
            if ni and eq:
                return ni / eq
            else:
                return None
        roe1 = calc_roe(tick1)
        roe2 = calc_roe(tick2)
        # EPS growth (trailing vs forward EPS)
        eps1 = info1.get('trailingEps', 0)
        fwd_eps1 = info1.get('forwardEps', 0)
        growth1 = (fwd_eps1 - eps1) / eps1 * 100 if eps1 and fwd_eps1 else None
        eps2 = info2.get('trailingEps', 0)
        fwd_eps2 = info2.get('forwardEps', 0)
        growth2 = (fwd_eps2 - eps2) / eps2 * 100 if eps2 and fwd_eps2 else None
        
        # Prepare comparison table
        comp_df = pd.DataFrame({
            "Metric": ["Market Cap (USD)", "P/E Ratio", "ROE", "EPS Growth (%)"],
            sym1: [
                f"${info1.get('marketCap',0):,.0f}", 
                round(info1.get('trailingPE', 0), 2), 
                f"{roe1:.2%}" if roe1 else "N/A", 
                f"{growth1:.1f}%" if growth1 else "N/A"
            ],
            sym2: [
                f"${info2.get('marketCap',0):,.0f}", 
                round(info2.get('trailingPE', 0), 2), 
                f"{roe2:.2%}" if roe2 else "N/A", 
                f"{growth2:.1f}%" if growth2 else "N/A"
            ]
        })
        st.dataframe(comp_df.set_index("Metric"))
        
        # Scoring (simple example: higher ROE and EPS growth = higher score)
        score1 = (roe1 or 0) + (growth1 or 0)/100
        score2 = (roe2 or 0) + (growth2 or 0)/100
        st.write(f"Score for {sym1}: {score1:.2f}")
        st.write(f"Score for {sym2}: {score2:.2f}")
# Portfolio Analysis
if selection == "Portfolio Analysis":
    st.header("Portfolio Upload & Analysis")
    uploaded = st.file_uploader("Upload Portfolio CSV", type="csv")
    if uploaded:
        port_df = pd.read_csv(uploaded)
        if 'Ticker' in port_df.columns and 'Shares' in port_df.columns:
            # Aggregate shares by ticker
            holdings = port_df.groupby("Ticker")["Shares"].sum().reset_index()
            st.write("Portfolio Holdings:", holdings)
            # Fetch latest price for each ticker
            prices = {}
            total_value = 0.0
            for ticker in holdings["Ticker"]:
                price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
                prices[ticker] = price
                shares = holdings.loc[holdings["Ticker"] == ticker, "Shares"].iloc[0]
                total_value += price * shares
            st.write(f"Total Portfolio Value: ${total_value:,.2f}")
            # Example PnL: (assuming each row had a cost; else skip)
            if 'Buy Price' in port_df.columns:
                port_df['Value'] = port_df['Shares'] * port_df['Buy Price']
                invested = port_df['Value'].sum()
                pnl = total_value - invested
                st.write(f"Total Invested: ${invested:,.2f}")
                st.write(f"Unrealized P/L: ${pnl:,.2f}")
            # Plot portfolio weights
            fig = px.pie(holdings, names='Ticker', values='Shares', title="Portfolio Allocation")
            st.plotly_chart(fig)
        else:
            st.error("CSV must have 'Ticker' and 'Shares' columns.")
# Finance News via RSS
if selection == "Finance News":
    st.header("Latest Finance News")
    feeds = {
        "Bloomberg Technology": "https://www.bloomberg.com/feeds/site/technology.xml",
        "WSJ Markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
        "Reuters Business": "http://feeds.reuters.com/reuters/businessNews"
    }
    for name, url in feeds.items():
        st.subheader(name)
        feed = feedparser.parse(url)
        entries = feed.get('entries', [])[:5]  # top 5 articles
        for entry in entries:
            st.markdown(f"- [{entry.get('title')}]({entry.get('link')})")
# FX & Derivatives Dashboard
if selection == "FX & Derivatives":
    st.header("FX Rates")
    fx_pairs = ["EURUSD=X", "GBPUSD=X", "JPY=X"]
    for pair in fx_pairs:
        rate = yf.Ticker(pair).history(period="1y")["Close"]
        st.subheader(pair.replace("=X", ""))
        st.line_chart(rate)
    st.header("Derivatives Basics")
    st.markdown("""
    **Options (Calls and Puts)** – contracts giving the right (not obligation) to buy (call) or sell (put) an asset at a specified strike price.  
    **Example:** A call option on a stock allows a trader to lock in a maximum buy price.  
    **Futures Contracts** – agreements to buy/sell an asset at a future date and price.  
    *(This section can be expanded with formulas or payoff diagrams as needed.)*
    """)
# AI Summary & PDF Upload
if selection == "AI Summary & PDF":
    st.header("AI Summary of PDF Document")
    pdf_file = st.file_uploader("Upload PDF for Summarization", type="pdf")
    api_key = st.text_input("OpenAI API Key", type="password")
    if pdf_file and api_key:
        pdf_reader = PdfReader(pdf_file)
        text_data = ""
        for page in pdf_reader.pages:
            text_data += page.extract_text() + "\n"
        st.write("Extracted text (truncated):", text_data[:500] + "...")
        
        openai.api_key = api_key
        if st.button("Generate Summary"):
            # Call OpenAI API to summarize (example using ChatCompletion)
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Summarize the following financial document."},
                    {"role": "user", "content": text_data[:4000]}  # truncate if too long
                ],
                max_tokens=300
            )
            summary = response.choices[0].message.content.strip()
            st.subheader("AI Summary")
            st.write(summary)
# Knowledge Library
if selection == "Knowledge Library":
    st.header("Knowledge Library")
    st.subheader("Major Financial Crises")
    st.markdown("""
    - **Black Monday (1987)**: A sudden global stock market crash on Oct 19, 1987. Major indices fell ~20-45%, triggering concerns of a depression:contentReference[oaicite:14]{index=14}.  
    - **Asian Financial Crisis (1997)**: Began with the Thai baht collapse; spread to East Asia and beyond. It highlighted risks of fixed exchange regimes and over-leveraged economies.  
    - **Global Financial Crisis (2007-2009)**: Triggered by subprime mortgages in the US, this became the worst crisis since the Great Depression:contentReference[oaicite:15]{index=15}. Banks globally experienced massive losses; economic activity contracted worldwide.  
    - **Other Crises**: (e.g., 1929 Great Depression, 2000 Dot-com crash, 2020 COVID-19 market crash, etc.)
    """)

    st.subheader("Basel Accords I, II, III")
    st.markdown("""
    - **Basel I (1988)**: Required internationally active banks to hold capital equal to at least 8% of risk-weighted assets:contentReference[oaicite:16]{index=16}. This standardized credit-risk capital across banks.  
    - **Basel II (2004)**: Introduced more sophisticated risk measures (including operational risk) and internal ratings.  
    - **Basel III (2010)**: Enacted post-2008 crisis; increased capital quality/quantity and added liquidity standards. It further refined the capital rules after lessons from the 2007-09 crisis:contentReference[oaicite:17]{index=17}.  
    - These accords aim to enhance financial system resilience by ensuring banks can absorb losses.
    """)

    st.subheader("Core Finance Formulas")
    st.markdown(r"""
    - **CAPM (Capital Asset Pricing Model)**: \( E(R_i) = R_f + \beta_i (E(R_m) - R_f) \):contentReference[oaicite:18]{index=18}. This gives the expected return of an asset based on its beta and the market risk premium.  
    - **Return on Equity (ROE)**: \( \text{ROE} = \frac{\text{Net Income}}{\text{Shareholders' Equity}} \). It measures how efficiently equity is used to generate profit:contentReference[oaicite:19]{index=19}.  
    - **Earnings Per Share (EPS) Growth**: The percentage increase in EPS year-over-year:contentReference[oaicite:20]{index=20}. It indicates how rapidly a company's "bottom line" per share is growing.  
    - **Other Ratios**: P/E = Price / EPS; Debt-to-Equity, Current Ratio, etc. These provide snapshots of valuation, leverage, and liquidity.
    """)
# Decomposition and PCA Demo
if selection == "Decomposition Demo":
    st.header("Financial Data Decomposition (PCA Demo)")
    st.write("This example generates synthetic financial ratios for 100 companies and performs PCA.")
    # Generate synthetic data (e.g., 4 ratios: profit margin, debt/equity, ROE, current ratio)
    np.random.seed(42)
    ratios = np.random.rand(100, 4)  # random for demo purposes
    pca = PCA(n_components=2)
    components = pca.fit_transform(ratios)
    df_comp = pd.DataFrame(components, columns=["PC1", "PC2"])
    df_comp["Ticker"] = [f"T{str(i).zfill(3)}" for i in range(1, 101)]
    fig = px.scatter(df_comp, x="PC1", y="PC2", hover_data=["Ticker"], title="PCA of Financial Ratios")
    st.plotly_chart(fig)
    st.write("Here, PC1 and PC2 are the principal components capturing the most variance in the synthetic ratio data.")
# Login / Personalization (Optional)
if selection == "Login/Personalization":
    st.header("User Login / Personalization")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Dummy check (replace with real auth)
            if username == "user" and password == "pass":
                st.session_state.logged_in = True
                st.session_state.user = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")
    else:
        st.write(f"Welcome back, **{st.session_state.user}**!")
        # Personalized settings could go here
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()
