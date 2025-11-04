import streamlit as st

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

# Section 1: About Us
if section == "About Us":
    st.title("🧠 Welcome to PSBFinance")
    st.image("https://raw.githubusercontent.com/gkyash97-st-cloud/psbfinance/main/capilotimage.png", use_column_width=True)
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

# Section 2: General Knowledge
if section == "General Knowledge":
    st.header("📚 General Finance Knowledge")

    try:
        import fitz  # PyMuPDF
        doc = fitz.open("Hull J.C.-Options, Futures and Other Derivatives_11th edition[1].pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        st.success("✅ Book loaded successfully.")
        st.markdown("### 🔍 Summary of Hull's Derivatives Book")
        st.write(text[:2000])
        st.info("This is a preview. Future versions will include topic-based summaries and definitions.")
    except Exception as e:
        st.warning("⚠️ Book not found or PyMuPDF not installed. Please check your repo and requirements.txt.")
elif section == "Finance News":
    st.header("📰 Latest Finance News")

    st.markdown("""
    Stay updated with the latest headlines from the world of finance, markets, and economics.
    """)

    st.info("This section will soon include live news feeds and curated summaries.")
elif section == "Global Financials":
    st.header("🌍 Global Financial Dashboard")

    st.markdown("""
    Explore global financial data including stock prices, currency exchange rates, and economic indicators.
    """)

    st.info("This section will soon include interactive charts and downloadable datasets.")
import yfinance as yf

elif section == "Global Financials":
    st.header("🌍 Global Financial Dashboard")

    st.markdown("Explore global financial data including stock prices, currency exchange rates, and economic indicators.")

    ticker = st.text_input("Enter a stock ticker (e.g., AAPL, TSLA, MSFT):")

    if ticker:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            price = data["Close"].iloc[-1]
            st.success(f"📈 Current price of {ticker.upper()}: ${price:.2f}")
        except Exception as e:
            st.error("⚠️ Could not retrieve stock data. Please check the ticker symbol.")
