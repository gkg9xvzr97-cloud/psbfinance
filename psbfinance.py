import streamlit as st

# Page config
st.set_page_config(page_title="PSBFinance", layout="wide")

# Sidebar navigation
section = st.sidebar.radio("📂 Navigate", ["About Us", "General Knowledge", "Finance News", "Global Financials"])

# Section 1: About Us
if section == "About Us":
    st.title("🧠 Welcome to PSBFinance")

    # Upload image manually from laptop
    uploaded_image = st.file_uploader("📷 Upload CAPILOTIMAGE.png", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, use_column_width=True)
    else:
        st.info("Please upload the CAPILOTIMAGE.png file from your laptop to display it here.")

    st.markdown("""
    ### Built by students for students.

    PSBFinance was born out of a challenge: our professor asked us to create a finance project, and we realized how hard it is to find clean, downloadable financial data. So we built this browser — not just for ourselves, but for every student and curious mind who wants to understand finance.

    Our goal is to make financial knowledge accessible, visual, and practical.

    **Team Members:**  
    - Amelie-Nour  
    - Sai Vinay  
    - N. Pooja  
    - Ira.Divine (Founder)
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
ook on corporate finance, this section will explain topics like capital structure, valuation, and financial ratios.")
    else:
        st.warning("📂 Please upload a document to begin.")
