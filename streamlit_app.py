import streamlit as st
from streamlit_option_menu import option_menu
from groq import Groq
from pypdf import PdfReader

def parsed_string(file):
    """Extract text from a PDF file."""
    reader = PdfReader(file)
    page_string = ""
    for page in reader.pages:
        page_string += "\n" + page.extract_text()
    return page_string

def call_llm(parsed_text):
    """Calls the LLM model to extract structured information."""
    query = """Extract the primary details such as name, phone number, email, degree, designation, company names, college name, total experience, and skills from the parsed text. 
    Return the extracted details in the following format:

    Primary Information Extracted From PDF:
    1. **Name**: <value>
    2. **Phone**: <value>
    3. **Email**: <value>
    ..."""
    
    client = Groq(api_key="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")
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a professional resume parser. Extract and format details clearly."},
            {"role": "user", "content": f"{query}\n\nParsed Text:\n{parsed_text}"}
        ],
        model="llama-3.3-70b-versatile"
    )
    return chat_completion.choices[0].message.content

def primary_info(file):
    """Handles primary information extraction from the uploaded file."""
    if not file:
        st.warning("Please upload a file to extract information.")
        return
    
    parsed_text = parsed_string(file)
    try:
        response = call_llm(parsed_text)
        st.session_state["llm_response"] = response  # Store response in session state
        
        # Display response in full width
        st.subheader("Extracted Information", divider="blue")
        st.markdown(response, unsafe_allow_html=True)
        
    except Exception as e:
        st.error(f"Error: {e}")

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
    st.subheader("About The App")
    st.write("This app extracts key resume information using AI.")

elif selected == "Primary Info":
    primary_info(fileUploader)

elif selected == "Key Insights":
    insights()
