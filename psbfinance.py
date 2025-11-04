import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from datetime import datetime
import os

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

# Section 1: About Us
if section == "About Us":
    st.title("🧠 Welcome to PSBFinance")

    # Load homepage image
    if os.path.exists("CAPLOIT_IMAGE.png"):
        st.image("CAPLOIT_IMAGE.png", use_column_width=True)
    else:
        st.warning("Homepage image not found. Please upload 'CAPLOIT_IMAGE.png'.")

    st.markdown("""
    ### Built by students for students.

    PSBFinance was born out of a challenge: our professor asked us to create a finance project, and we realized how hard it is to find clean, downloadable financial data. So we built this browser — not just for ourselves, but for every student and curious mind who wants to understand finance.

    Our goal is to make financial knowledge accessible, visual, and practical.

    **Team Members:**  
    - Amelie-Nour  
    - Sai Vinay  
    - N. Pooja  
    - Ira.Divine (Founder & Architect — mentioned here only)
    """)
