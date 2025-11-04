import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from datetime import datetime

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

import os

if os.path.exists("capilot_image.png"):
    st.image("capilot_image.png", use_column_width=True)
else:
    st.warning("Homepage image not found. Please upload 'capilot_image.png'.")

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

    st.markdown("### 🔍 Summary of Uploaded Book: *Hull – Options, Futures, and Other Derivatives*")
    st.write("""
    This book introduces key concepts in financial derivatives, including:
    - **Options**: Contracts giving the right to buy/sell assets at a set price
    - **Futures**: Agreements to buy/sell assets at a future date
    - **Swaps**: Contracts to exchange cash flows
    - **Risk Management**: Using derivatives to hedge against market volatility
    - **Pricing Models**: Black-Scholes, binomial trees, and Monte Carlo simulations

    It’s essential reading for finance students and professionals interested in trading, hedging, and financial engineering.
    """)

    uploaded_file = st.file_uploader("Upload your own notes or books (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
    if uploaded_file:
        st.success("✅ File uploaded successfully. Summary will be generated below.")
        st.info("📘 Custom summarization coming soon.")
