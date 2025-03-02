import os
import pandas as pd
import streamlit as st
from pyresparser import ResumeParser

# Set page configuration
st.set_page_config(page_title="Resume Parser", layout="wide")

# Sidebar - File Uploader
st.sidebar.header("Upload Resume File")
uploaded_file = st.sidebar.file_uploader("Upload a Resume (PDF/DOCX)", type=["pdf", "docx"])

# Main body - Tabs
tab1, tab2, tab3 = st.tabs(["Perform Parsing", "View Data", "Insights"])

# Initialize parsed data variable
parsed_data = {}

if uploaded_file is not None:
    # Save uploaded file temporarily
    file_extension = uploaded_file.name.split('.')[-1]
    temp_file_path = f"temp_resume.{file_extension}"
    
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Perform Resume Parsing
    parsed_data = ResumeParser(temp_file_path).get_extracted_data()

    # Remove temporary file
    os.remove(temp_file_path)

# Tab 1: Perform Parsing
with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📄 Resume File")
        if uploaded_file:
            st.write(f"**Uploaded:** {uploaded_file.name}")
        else:
            st.warning("No resume uploaded yet.")

    with col2:
        st.subheader("📝 Extracted Information")
        if parsed_data:
            st.write(f"**Name:** {parsed_data.get('name', 'N/A')}")
            st.write(f"**Email:** {parsed_data.get('email', 'N/A')}")
            st.write(f"**Phone:** {parsed_data.get('mobile_number', 'N/A')}")
            st.write(f"**Skills:** {', '.join(parsed_data.get('skills', [])) if parsed_data.get('skills') else 'N/A'}")
            st.write(f"**Education:** {parsed_data.get('degree', 'N/A')}")
            st.write(f"**Experience:** {parsed_data.get('total_experience', 'N/A')} years")
        else:
            st.info("Upload a file to see extracted information.")

# Tab 2: View Data
with tab2:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📂 Resume Details")
        st.write("View structured extracted resume data.")

    with col2:
        if parsed_data:
            df = pd.DataFrame([parsed_data])
            st.dataframe(df)
            csv_file = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", data=csv_file, file_name="parsed_resume.csv", mime="text/csv")
        else:
            st.warning("No parsed data available.")

# Tab 3: Insights
with tab3:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Insights")
        st.write("Basic insights from the resume.")

    with col2:
        if parsed_data:
            st.write(f"📌 **Key Skills:** {', '.join(parsed_data.get('skills', [])) if parsed_data.get('skills') else 'N/A'}")
            st.write(f"🎓 **Education Level:** {parsed_data.get('degree', 'N/A')}")
            st.write(f"📈 **Years of Experience:** {parsed_data.get('total_experience', 'N/A')} years")
        else:
            st.warning("No insights available.")
