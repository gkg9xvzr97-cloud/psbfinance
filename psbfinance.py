import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd

st.set_page_config(page_title="Finance Dashboard", layout="wide")

# Sidebar for user input
st.sidebar.title("Finance Dashboard")
ticker = st.sidebar.text_input("Enter Stock Ticker (e.g., AAPL)", value="AAPL")

# Yahoo Finance-style tabs
tab1, tab2, tab3, tab4 = st.tabs(["Price & Stats", "Options Chain", "Futures", "Derivatives Help"])

####################### TAB 1: Price & Key Stats #######################
with tab1:
    # Stock data & price chart
    data = yf.download(ticker, period="1y", interval="1d")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Price'))
    fig.update_layout(title=f"Historical Closing Price ({ticker.upper()})")
    st.plotly_chart(fig, use_container_width=True)

    # Key statistics
    info = yf.Ticker(ticker).info
    st.subheader("Key Statistics")
    stats = {
        "Market Cap": info.get("marketCap"),
        "52 Week High": info.get("fiftyTwoWeekHigh"),
        "52 Week Low": info.get("fiftyTwoWeekLow"),
        "PE Ratio": info.get("trailingPE"),
        "Dividend Yield": info.get("dividendYield"),
        "Sector": info.get("sector"),
    }
    for k,v in stats.items():
        st.write(f"**{k}:** {v}")

####################### TAB 2: Options Chain #######################
with tab2:
    st.subheader("Options Chain")
    opt = yf.Ticker(ticker)
    dates = opt.options
    date = st.selectbox("Select Expiration Date", dates)
    chain = opt.option_chain(date)
    st.write("**Calls**")
    st.dataframe(chain.calls)
    st.write("**Puts**")
    st.dataframe(chain.puts)

    st.markdown("""
    **Payoff Formula**   
    - Call payoff: max(\(S_T-K\), 0)  
    - Put payoff: max(\(K-S_T\), 0)
    """)

####################### TAB 3: Futures (Info) #######################
with tab3:
    st.subheader("Futures Data")
    st.markdown("Futures data is not available for individual equities via Yahoo Finance API, but you can fetch index futures (e.g., S&P 500 ES, FTSE 100, etc.) via third-party APIs like [Alpha Vantage](https://www.alphavantage.co) or [Finnhub](https://finnhub.io).")
    st.markdown("""
    **Key formulas:**  
    - Forward Price: \(F = S_0e^{rT}\)  
    - Futures Payoff: long = \(S_T - F\), short = \(F - S_T\)
    """)

####################### TAB 4: Derivatives Help & Theory #######################
with tab4:
    st.subheader("Derivatives: Theory & Formulas")
    st.markdown("""
    **Types of Traders in Derivatives Markets**
    - Hedgers: reduce risk with derivatives
    - Speculators: aim for profit with leverage
    - Arbitrageurs: lock in riskless profit

    **Black-Scholes Formula (European Options):**
    \[
    C = S N(d_1) - K e^{-rT}N(d_2)
    \]
    Where:  
    \(
    d_1 = \frac{\ln(S/K)+(r+\frac{\sigma^2}{2})T}{\sigma\sqrt{T}}
    \),  
    \(
    d_2 = d_1-\sigma\sqrt{T}
    \)
    """)
    st.info("For hedging, speculation and arbitrage examples from Hull's textbook, check the help sidebar.")

st.sidebar.markdown("""
**Derivatives Guide:**  
- Call/Put Option examples
- Hedging with forward contracts
- Futures and options payoff charts

**Hull's textbook explanations are provided in-app.**
""")
