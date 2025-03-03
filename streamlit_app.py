import streamlit as st
import pdfplumber
import docx
import openai
from streamlit_option_menu import option_menu

# Function to extract text from uploaded files
def extract_text(file):
    page_string = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as reader:
            for page in reader.pages:
                page_string += page.extract_text() + "\n" if page.extract_text() else ""
    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
        doc = docx.Document(file)
        for para in doc.paragraphs:
            page_string += para.text + "\n"
    else:
        return "Unsupported file type"
    return page_string.strip()

# Function to call the LLM API
def call_llm(parsed_text):
    final_query = """
    You are given a list of strings which are comma-separated.
    Also, you are given a parsed string. Extract information for a list of comma-separated items from the parsed string.
    If any information is not found, return 'Information Not Found'.
    The returned string should contain only the values in a comma-separated format (e.g., value1,value2).
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """You are a very good Resume Parser Software.
            Extract primary information from resumes, such as Name, Email, and Phone Number.
            Return the content as:
            1. Name: [Name]
            2. Phone: [Phone]
            3. Email: [Email]
            If any field is missing, return "Information Not Found" for that field."""},
            {"role": "user", "content": f"{final_query} \n Parsed String: {parsed_text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Function to handle primary information extraction
def primary_info(file):
    if not file:
        st.warning("Please upload a file to extract information.")
        return
    
    if 'primary_info' not in st.session_state:
        st.session_state['primary_info'] = None
    
    if st.session_state['primary_info'] is None:
        parsed_text = extract_text(file)
        if not parsed_text:
            st.error("Could not extract text from the file.")
            return
        
        try:
            st.session_state['primary_info'] = call_llm(parsed_text)
        except Exception as e:
            st.error(f"Error during LLM processing: {e}")
            return

    # Tabs for displaying extracted information
    tab1, tab2 = st.tabs(["Primary Info", "View PDF"])
    
    with tab1:
        with st.container():
            st.subheader("Primary Details", divider='blue')
            st.markdown(st.session_state['primary_info'])
    
    with tab2:
        st.write("File preview feature can be added here.")

# Placeholder for insights logic
def insights():
    st.info("Insights feature coming soon.")

# Sidebar file uploader
fileUploader = st.sidebar.file_uploader("Upload Files (PDF, DOCX)", type=['pdf', 'docx', 'doc'])

# Sidebar Navigation Menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["About The App", "Primary Info", "Key Insights"],
        icons=["info-circle", "person-badge", "lightbulb"],
        menu_icon="cast",
        default_index=0
    )

# Main App Logic
if selected == "About The App":
    st.write("This app extracts primary information from resumes.")
elif selected == "Primary Info":
    primary_info(fileUploader)
elif selected == "Key Insights":
    insights()
