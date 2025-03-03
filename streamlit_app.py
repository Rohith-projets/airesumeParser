import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import *
from groq import Groq
from pypdf import PdfReader
import pandas as pd

# Initialize session state variables
session_options = ['college_name', 'company_names', 'degree', 'designation',
                   'email', 'mobile_number', 'name', 'no_of_pages', 'skills', 'total_experience', 'count']
for i in session_options:
    if i not in st.session_state:
        st.session_state[i] = None

if "session_dict" not in st.session_state:
    st.session_state["session_dict"] = {}

def check_status():
    return st.session_state.get('count', 0) == 1

def parsed_string(file):
    reader = PdfReader(file)
    page_string = ""
    for i in range(len(reader.pages)):
        page_string += "\n" + reader.pages[i].extract_text()  # Extract text properly
    return page_string

def call_llm(parsed_text, query):
    if "count" in query:
        query.remove("count")  # Fix: Use remove() properly
    query_str = ",".join(query)
    
    final_query = """You are given a list of strings which are comma-separated.
    Also, you are given a parsed string. Just extract information for a list of comma-separated items from the parsed string.
    If any information is not found, return 'Information Not Found'.
    The returned string should contain only the values in a comma-separated format (e.g., value1,value2).
    So just return a string with the corresponding and accurate values, comma-separated.
    """
    
    client = Groq(api_key="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")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": """You are a very good Resume Parser Software.
            You have to return the parsed content from the parsed string.
            Note: You are given a parsed string from the documents and a query.
            You have to extract the information related to the query."""},
            {"role": "user", "content": f"{final_query} \n Parsed String: {parsed_text} \n Information To Extract: {query_str}"}
        ],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content  # Fix: Correct response handling

def primary_info(file):
    if not file:
        st.warning("Please upload a file to extract information.")
        return
    
    parsed_text = parsed_string(file)  # Fix: Use correct function name
    try:
        value = call_llm(parsed_text, session_options)
        value_list = value.split(',')
        
        extracted_data = {}
        for i in range(len(session_options) - 1):
            if session_options[i] != 'count' and i < len(value_list):
                st.session_state[session_options[i]] = value_list[i]
                extracted_data[session_options[i]] = [value_list[i]]
        
        st.success("Information extracted successfully!")
        
        tab1, tab2 = st.tabs(["Primary Details", "Uploaded PDF"])
        with tab1:
            st.subheader("Primary Details")
            df = pd.DataFrame(extracted_data)
            st.dataframe(df)
        
        with tab2:
            st.subheader("Uploaded PDF")
            st.download_button("Download Extracted Data", df.to_csv(index=False), "extracted_info.csv", "text/csv")
            st.text_area("Extracted Text", parsed_text, height=300)
        
    except Exception as e:
        st.error(f"You got the following error: {e}")

def insights():
    pass  # Placeholder for insights logic

# File uploader
fileUploader = st.sidebar.file_uploader("Upload Files Of Type PDF, DOCX", type=['pdf', 'docx', 'doc'])

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["About The App", "Primary Info", "Key Insights"],
        icons=["info-circle", "person-badge", "lightbulb"],
        menu_icon="cast",
        default_index=0
    )

# Content handling
if selected == "About The App":
    pass  # Placeholder for future content
elif selected == "Primary Info":
    primary_info(fileUploader)
elif selected == "Key Insights":
    insights()
