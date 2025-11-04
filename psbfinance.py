import streamlit as st

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

# Section 1: About Us
if section == "About Us":
    st.title("🧠 Welcome to PSBFinance")

    # Display image from GitHub
    st.image("https://raw.githubusercontent.com/gkyash97-st-cloud/psbfinance/main/capilotimage.png", use_column_width=True)

    st.markdown("""
    ### Built by students for students.

    PSBFinance was born out of a challenge: our professor asked us to create a finance project, and we realized how hard it is to find clean, downloadable financial data. So we built this browser — not just for ourselves, but for every student and curious mind who wants to understand finance.

    Our goal is to make financial knowledge accessible, visual, and practical.

    **Team Members:**  
    - Amelie-Nour  
    - Sai Vinay  
    - N. Pooja  
    - Ira.Divine (Founder & Architect )
    """)
# Comment this in only after PyMuPDF is installed via requirements.txt
# import fitz  # PyMuPDF

if section == "General Knowledge":
    st.header("📚 General Finance Knowledge")

    try:
        # Load Hull book PDF
        doc = fitz.open("Hull J.C.-Options, Futures and Other Derivatives_11th edition[1].pdf")
        text = ""
        for page in doc:
            text += page.get_text()

        st.success("✅ Book loaded successfully.")
        st.markdown("### 🔍 Summary of Hull's Derivatives Book")

        # Display first 2000 characters
        st.write(text[:2000])
        st.info("This is a preview. Future versions will include topic-based summaries and definitions.")
    except Exception as e:
        st.warning("📂 Book not found or PyMuPDF not installed. Please check your repo and requirements.txt.")
