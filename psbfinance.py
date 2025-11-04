import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from datetime import datetime

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

# Load homepage image
if section == "About Us":
    st.image("capilot_image.png", use_column_width=True)  # Make sure this image is in your app folder
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
        st.success("✅ File uploaded successfully.")
        st.markdown("### 🔍 Summary of Uploaded Content")
        st.info("This section will summarize the key concepts, definitions, and insights from your uploaded document.")

        # Placeholder for now
        st.write("📘 Example: If you upload a book on corporate finance, this section will explain topics like capital structure, valuation, and financial ratios.")
    else:
        st.warning("📂 Please upload a document to begin.")
