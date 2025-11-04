import streamlit as st

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])
if section == "About Us":
    st.image("psbfinance_dark.png", use_column_width=True)  # Replace with darker image
    st.markdown("""
    # 🧠 About PSBFinance  
    ### Built by students for students.

    PSBFinance was born out of a challenge: our professor asked us to create a finance project, and we realized how hard it is to find clean, downloadable financial data. So we built this browser — not just for ourselves, but for every student and curious mind who wants to understand finance.

    Our goal is to make financial knowledge accessible, visual, and practical.

    **Team Members:**  
    - Amelie-Nour  
    - Sai Vinay  
    - N. Pooja  
    - Ira.Divine (Founder & Architect — mentioned here only)

    """)
    if section == "General Knowledge":
    st.header("📚 General Finance Knowledge")
    uploaded_file = st.file_uploader("Upload notes or books (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])

    if uploaded_file:
        # Placeholder for summarization logic
        st.success("File uploaded successfully. Generating summary...")
        st.markdown("### 🔍 Summary of Uploaded Content")
        st.write("This section will summarize the key concepts, definitions, and insights from your uploaded document.")
import feedparser

if section == "Finance News":
    st.header("📰 Global Finance News")
    sources = {
        "Bloomberg": "https://www.bloomberg.com/feed/podcast",
        "France 24": "https://www.france24.com/en/rss",
        "Reuters": "https://www.reuters.com/rssFeed/businessNews"
    }

    for name, url in sources.items():
        st.subheader(f"🗞️ {name}")
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            st.markdown(f"**{entry.title}** — {entry.published}")
            st.write(entry.link)
import yfinance as yf
import pandas as pd
from datetime import datetime

if section == "Global Financials":
    st.header("💼 Global Company Financials")

    start_date = st.date_input("Start Date", value=pd.to_datetime("2000-01-01"))
    end_date = st.date_input("End Date", value=datetime.today())
    ticker = st.text_input("Enter a public company ticker (e.g., AAPL, TSLA, MSFT)").upper()

    if ticker:
        df = yf.download(ticker, start=start_date, end=end_date)
        if not df.empty:
            st.subheader(f"📈 {ticker} Stock Price")
            st.line_chart(df['Adj Close'])

            st.subheader("📥 Download Financial Statements")
            stock = yf.Ticker(ticker)
            st.download_button("Balance Sheet", stock.balance_sheet.to_csv().encode(), f"{ticker}_balance_sheet.csv")
            st.download_button("Income Statement", stock.income_stmt.to_csv().encode(), f"{ticker}_income_statement.csv")
            st.download_button("Cash Flow", stock.cashflow.to_csv().encode(), f"{ticker}_cash_flow.csv")

