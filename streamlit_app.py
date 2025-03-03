import streamlit as st
import fitz  # PyMuPDF for PDF processing
from groq import Groq
from streamlit_option_menu import option_menu

# Initialize session state
if "primary_info" not in st.session_state:
    st.session_state["primary_info"] = None

# Function to extract text from PDF
def parse_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    return text if text.strip() else "No readable text found."

# Function to call LLM from Groq
def call_llm(parsed_text):
    final_query = """Extract the primary details (Name, Email, Phone, etc.) from the given parsed text.
    Format the response as:
    1. Name: <value>
    2. Email: <value>
    3. Phone: <value>
    If any detail is missing, return 'Information Not Found' for that field.
    """

    client = Groq(api_key="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")  # Replace with actual API key

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are an advanced resume parser. Extract primary details in a structured format."},
            {"role": "user", "content": f"{final_query}\nParsed Text:\n{parsed_text}"}
        ],
        model="deepseek-chat"  # Using DeepSeek if available
    )
    return chat_completion.choices[0].message.content

# Function to display primary information
def primary_info(file):
    if not file:
        st.warning("Please upload a file to extract information.")
        return

    if st.session_state["primary_info"] is None:
        parsed_text = parse_pdf(file)
        try:
            st.session_state["primary_info"] = call_llm(parsed_text)
        except Exception as e:
            st.error(f"Error: {e}")
            return

    tab1, tab2 = st.tabs(["Primary Info", "View PDF"])

    with tab1:
        st.subheader("Extracted Primary Details", divider="blue")
        st.markdown(st.session_state["primary_info"])

    with tab2:
        st.write("Uploaded PDF:")
        st.download_button("Download Parsed Text", st.session_state["primary_info"], "parsed_info.txt")

# Placeholder for insights
def insights():
    st.info("Key Insights will be implemented soon.")

# File uploader in sidebar
fileUploader = st.sidebar.file_uploader("Upload PDF Resume", type=["pdf"])

# Sidebar navigation menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["About The App", "Primary Info", "Key Insights"],
        icons=["info-circle", "person-badge", "lightbulb"],
        menu_icon="cast",
        default_index=0
    )

# Main content handling
if selected == "About The App":
    st.write("This app extracts primary information from resumes.")
elif selected == "Primary Info":
    primary_info(fileUploader)
elif selected == "Key Insights":
    insights()
