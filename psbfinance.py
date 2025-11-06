import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# --------- CONFIG ---------
st.set_page_config(page_title="PSP Finance", layout="wide")

# --------- SIDEBAR NAVIGATION ---------
st.sidebar.title("PSP Finance")
st.sidebar.caption("Explore professional tools for finance students and analysts.")
st.sidebar.markdown("---")

tabs = st.sidebar.radio("📁 Navigate", [
    "Home",  # << This MUST match the condition you check later
    "Ticker Research",
    "Compare Companies"
])
# --------- HOME TAB ---------
if tabs == "Home":
    col1, col2 = st.columns([2, 1])
    with col1:
        st.title("Welcome to PSP Finance")
        st.markdown("""
        PSP Finance is a research-grade financial analytics platform built for finance students, researchers, and analysts.

        **Capabilities:**
        - Research public and private companies with explainable financials  
        - Visualize income, balance sheet, and cash flow with decomposition plots  
        - Compare company fundamentals side-by-side with scoring  
        - Read real-time financial news from professional RSS feeds  
        - Track FX rates, commodity exposure, and derivative risks  
        - Upload and manage multiple student or investor portfolios  
        - Learn from historical financial crises, regulations, and Basel reforms  

        > Designed to bridge classroom theory with real-world financial analysis.
        """)
    with col2:
        st.image("capilotimage.png", caption="Explore charts, fundamentals, and markets", width=280)

