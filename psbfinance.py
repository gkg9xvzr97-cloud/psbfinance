# app.py

import streamlit as st

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="PSP Finance", layout="wide")

# ---------------------- Custom Styling ----------------------
st.markdown("""
<style>
:root{
  --ink:#0e1a2b; --muted:#6b7b91; --card:#f6f8fb; --accent:#0d6efd;
}
html, body, .block-container { color: var(--ink); }
.stButton>button {
  background: var(--accent); color: #fff; border: 0; border-radius: 10px;
  padding: 10px 18px; font-weight: 600;
}
.card {
  background: var(--card); border: 1px solid #e6ebf2; border-radius: 14px; padding: 16px 18px;
}
.smallnote { color: var(--muted); font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ---------------------- Navigation ----------------------
PAGES = [
    "Home",
    "Dashboard",
    "Portfolio Optimizer",
    "Failed Companies",
    "Unpopular Investments",
    "Why Financial Models Fail",
    "Charts & Data",
    "Lessons for the Future",
    "News Feed",
    "Public Company Financials Lookup",
    "About"
]

st.sidebar.title("PSP Finance")
page = st.sidebar.radio("Navigate", PAGES)

# ---------------------- Page Functions ----------------------
def home():
    st.title("Welcome to PSP Finance")
    st.write("This is the starting point. We’ll add features step by step.")

def dashboard():
    st.title("Dashboard")
    st.info("Placeholder: will show live market charts and risk metrics.")

def optimizer():
    st.title("Portfolio Optimizer")
    st.info("Placeholder: will implement Modern Portfolio Theory.")

def failed_companies():
    st.title("Failed Companies")
    st.info("Placeholder: case studies like Enron, Lehman Brothers, Wirecard.")

def unpopular_investments():
    st.title("Unpopular Investments")
    st.info("Placeholder: assets that underperformed or lost investor confidence.")

def models_fail():
    st.title("Why Financial Models Fail")
    st.info("Placeholder: explanations of model limitations.")

def charts_data():
    st.title("Charts & Data")
    st.info("Placeholder: company comparisons, index performance, risk/return scatter.")

def lessons_future():
    st.title("Lessons for the Future")
    st.info("Placeholder: diversification, risk management, realistic assumptions.")

def news_feed():
    st.title("News Feed")
    st.info("Placeholder: finance RSS feeds and keyword filters.")

def financials_lookup():
    st.title("Public Company Financials Lookup")
    st.info("Placeholder: income statement, balance sheet, cash flow.")

def about():
    st.title("About PSP Finance")
    st.markdown("""
    ### What is PSP Finance?
    PSP Finance is a research and learning platform that combines **live market data**,  
    **portfolio optimization models**, and **educational case studies**.

    ### Features
    - **Dashboard:** Multi-ticker charts, rolling risk, sector snapshots.
    - **Portfolio Optimizer:** Mean-variance analytics, efficient frontier, Sharpe ratio.
    - **Failed Companies:** Case studies of collapsed firms.
    - **Unpopular Investments:** Lessons from risky bets.
    - **Why Models Fail:** Educational breakdown of assumptions and pitfalls.
    - **Charts & Data:** Company comparisons, index performance, risk/return scatter.
    - **Lessons for the Future:** Practical takeaways for investors.
    - **News Feed:** Live updates from financial sources.
    - **Financials Lookup:** Company fundamentals (Income, Balance Sheet, Cash Flow).
    """)

# ---------------------- Router ----------------------
ROUTES = {
    "Home": home,
    "Dashboard": dashboard,
    "Portfolio Optimizer": optimizer,
    "Failed Companies": failed_companies,
    "Unpopular Investments": unpopular_investments,
    "Why Financial Models Fail": models_fail,
    "Charts & Data": charts_data,
    "Lessons for the Future": lessons_future,
    "News Feed": news_feed,
    "Public Company Financials Lookup": financials_lookup,
    "About": about,
}

ROUTES[page]()
