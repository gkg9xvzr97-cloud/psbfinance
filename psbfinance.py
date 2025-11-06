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
    # ... your code for homepage ...
