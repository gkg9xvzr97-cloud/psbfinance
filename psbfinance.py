import streamlit as st

# Set page config
st.set_page_config(page_title="PSP Finance", layout="wide")

# Header
st.title("📊 PSP Finance Intelligence Terminal")
st.subheader("Where Future Analysts Discover Financial Truths")

# About the App
st.markdown("""
**PSP Finance** is a student-built platform designed to revolutionize financial research.  
It brings together real-time market data, company financials, AI-powered comparisons, and global news into one intuitive dashboard.  
Whether you're analyzing stocks, bonds, derivatives, or private firms, PSP Finance gives you clarity, speed, and insight — all in one place.
""")

# Navigation
section = st.sidebar.radio("📂 Navigate", [
    "Home",
    "Company Search",
    "AI Comparison",
    "SEC Filings",
    "Bond & Derivatives",
    "Portfolio Tracker",
    "Global Market Dashboard",
    "News Feed",
    "Private Company Insights"
])
import yfinance as yf
import pandas as pd

if section == "Company Search":
    st.header("🏢 Company Search")

    query = st.text_input("Enter a company name or ticker (e.g., AAPL, MSFT, TSLA):", key="company_search_input")

    def calculate_risk(pe, market_cap):
        if pe == "N/A" or market_cap == 0:
            return "Unknown"
        if pe > 30 or market_cap < 1e9:
            return "⚠️ High Risk"
        elif pe > 15:
            return "🟡 Moderate Risk"
        else:
            return "🟢 Low Risk"

    if query:
        try:
            ticker = yf.Ticker(query)
            info = ticker.info

            st.subheader(f"📊 {info.get('longName', query)} ({query.upper()})")
            st.markdown(f"""
            **Sector:** {info.get('sector', 'N/A')}  
            **Industry:** {info.get('industry', 'N/A')}  
            **Market Cap:** {info.get('marketCap', 'N/A'):,}  
            **Description:** {info.get('longBusinessSummary', 'N/A')}
            """)

            st.markdown("### 🧾 Financial Statements")

            income = ticker.financials.T
            st.markdown("#### 📈 Income Statement")
            st.dataframe(income)
            st.download_button("Download Income Statement", income.to_csv().encode(), file_name="income_statement.csv")

            balance = ticker.balance_sheet.T
            st.markdown("#### 🧾 Balance Sheet")
            st.dataframe(balance)
            st.download_button("Download Balance Sheet", balance.to_csv().encode(), file_name="balance_sheet.csv")

            cashflow = ticker.cashflow.T
            st.markdown("#### 💵 Cash Flow Statement")
            st.dataframe(cashflow)
            st.download_button("Download Cash Flow", cashflow.to_csv().encode(), file_name="cash_flow.csv")

            pe = info.get("trailingPE", "N/A")
            market_cap = info.get("marketCap", 0)
            risk = calculate_risk(pe, market_cap)
            st.markdown(f"### 🧪 Risk Score: {risk}")

            st.markdown("### 🧠 AI Summary")
            st.info(f"""
            {info.get('longName', query)} operates in the {info.get('sector', 'N/A')} sector and specializes in {info.get('industry', 'N/A')}.
            It has a market capitalization of ${info.get('marketCap', 0):,} and a PE ratio of {pe}.
            Based on valuation and size, the company is classified as: {risk}.
            """)

        except Exception:
            st.error("⚠️ Could not retrieve company data. Please check the ticker or try again later.")
