import streamlit as st
from streamlit_option_menu import option_menu
from groq import Groq  # Ensure the correct import for your API client

def call_llm(parsed_text):
    """Calls the LLM for resume parsing and extracts structured information."""
    if "llm_response" not in st.session_state:
        query = "Extract and format resume details clearly."
        client = Groq(api_key="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")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional resume parser."},
                {"role": "user", "content": f"{query}\n\nParsed Text:\n{parsed_text}"}
            ],
            model="llama-3.3-70b-versatile"
        )
        st.session_state["llm_response"] = chat_completion.choices[0].message.content
    return st.session_state["llm_response"]

def call_llm1(parsed_text, query):
    """Calls the LLM for extracting insights based on a query."""
    session_key = f"insight_{query}"
    if session_key not in st.session_state:
        formatted_query = f"Act like an article writer and write an article for {query} using {parsed_text}. The article should contain paragraphs and points."
        client = Groq(api_key="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")
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a great analyzer & report writer."},
                {"role": "user", "content": formatted_query}
            ],
            model="llama-3.3-70b-versatile"
        )
        st.session_state[session_key] = chat_completion.choices[0].message.content
    return st.session_state[session_key]

def primary_info(file):
    """Handles primary information extraction from the uploaded file."""
    if not file:
        st.warning("Please upload a file to extract information.")
        return
    
    if "parsed_text" not in st.session_state:
        st.session_state["parsed_text"] = parsed_string(file)
    
    response = call_llm(st.session_state["parsed_text"])
    st.subheader("Extracted Information", divider="blue")
    st.markdown(response, unsafe_allow_html=True)

def insights():
    """Handles insights extraction and display."""
    if "parsed_text" not in st.session_state:
        st.warning("Please upload a file first to extract insights.")
        return
    
    queries = {
        "Projects Done": "What are the projects that the user has completed?",
        "Project Relevance": "How are these projects related to the given role?",
        "Related Projects": "What projects are most relevant to the role?",
        "ATS Score": "What is the ATS score out of 100? Justify the rating.",
        "Skill Gaps": "What skills does the user lack for the given role?",
        "Skill Fit": "What skills match the role, and what are the missing skills?",
        "Job Performance": "How will the candidate perform based on skills and projects? Extract capabilities.",
        "Selection Reasons": "Why should this candidate be selected for the role?",
        "Rejection Reasons": "Why should this candidate be rejected for the role?"
    }
    
    col1, col2 = st.columns([1, 2])
    with col1:
        selected_query = st.radio("Select an insight to explore:", list(queries.keys()))
    
    if selected_query:
        response = call_llm1(st.session_state["parsed_text"], queries[selected_query])
        with col2:
            st.subheader(f"Insight: {selected_query}")
            st.markdown(response, unsafe_allow_html=True)

# File uploader
file = st.sidebar.file_uploader("Upload Files (PDF, DOCX, DOC)", type=['pdf', 'docx', 'doc'])

if file:
    primary_info(file)

# Sidebar menu
with st.sidebar:
    selected = option_menu(
        menu_title="Navigation",
        options=["Extract Information", "Insights"],
        icons=["file-earmark-text", "lightbulb"],
        menu_icon="list",
        default_index=0
    )

if selected == "Extract Information":
    primary_info(file)
elif selected == "Insights":
    insights()
