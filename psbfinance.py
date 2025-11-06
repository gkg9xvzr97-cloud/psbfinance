import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

# Sample data for Apple (replace with real values if available)
sector_pe_avg = 25
competitor_caps = {"Apple": 3991684251648, "Microsoft": 3000000000000, "NVIDIA": 2500000000000}

# 1. Valuation Decomposition
st.markdown("### 📊 Valuation Decomposition")

fig, ax = plt.subplots()
ax.bar(["Apple PE", "Sector Avg PE"], [36.26, sector_pe_avg], color=["red", "green"])
ax.set_ylabel("PE Ratio")
st.pyplot(fig)

# 2. Market Cap Comparison
st.markdown("### 💰 Market Cap vs Competitors")

fig2, ax2 = plt.subplots()
ax2.bar(competitor_caps.keys(), competitor_caps.values(), color=["blue", "purple", "orange"])
ax2.set_ylabel("Market Cap (USD)")
st.pyplot(fig2)

# 3. Profitability Breakdown
st.markdown("### 📈 Profitability Breakdown")

profit_data = {"Net Income": 72880000000, "Operating Income": 81453000000, "Gross Profit": 97858000000}
fig3, ax3 = plt.subplots()
ax3.pie(profit_data.values(), labels=profit_data.keys(), autopct="%1.1f%%", startangle=90)
ax3.axis("equal")
st.pyplot(fig3)

# 4. Risk Score Visual
st.markdown("### 🧪 Risk Meter")

risk_score = 3  # 1 = Low, 2 = Moderate, 3 = High
colors = ["green", "yellow", "red"]
labels = ["Low", "Moderate", "High"]

fig4, ax4 = plt.subplots()
ax4.barh(["Risk"], [risk_score], color=colors[risk_score - 1])
ax4.set_xlim(0, 3)
ax4.set_xticks([1, 2, 3])
ax4.set_xticklabels(labels)
st.pyplot(fig4)

            st.markdown("### 🧠 AI Summary")
            st.info(f"""
            {info.get('longName', query)} operates in the {info.get('sector', 'N/A')} sector and specializes in {info.get('industry', 'N/A')}.
            It has a market capitalization of ${info.get('marketCap', 0):,} and a PE ratio of {pe}.
            Based on valuation and size, the company is classified as: {risk}.
            """)

        except Exception:
            st.error("⚠️ Could not retrieve company data. Please check the ticker or try again later.")
