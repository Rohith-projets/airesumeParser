import streamlit as st
from streamlit_option_menu import option_menu
from langchain.document_loaders import PyPDFLoader, UnstructuredWordDocumentLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from groq import Groq

# Initialize session variables
session_variables = ['name', 'college', 'place', 'email', 'phone', 'working company', 'years of experience']
for i in session_variables:
    if i not in st.session_state:
        st.session_state[i] = None

# Function to load and process resume
def process_resume(uploaded_file):
    if uploaded_file is not None:
        file_type = uploaded_file.name.split(".")[-1]
        
        if file_type == "pdf":
            loader = PyPDFLoader(uploaded_file)
        elif file_type in ["doc", "docx"]:
            loader = UnstructuredWordDocumentLoader(uploaded_file)
        else:
            st.error("Unsupported file format")
            return None
        
        documents = loader.load()
        return documents
    return None

# Function to store in vectorDB and retrieve information
def store_and_retrieve_info(documents, groq_api_key):
    embeddings = OpenAIEmbeddings()
    vectordb = FAISS.from_documents(documents, embeddings)
    retriever = vectordb.as_retriever()
    llm = Groq(api_key=groq_api_key, model="mixtral-8x7b-32768")
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    
    queries = {
        "name": "Extract the candidate's name from the resume.",
        "college": "Extract the candidate's college/university.",
        "place": "Extract the location of the candidate.",
        "email": "Extract the email address.",
        "phone": "Extract the phone number.",
        "working company": "Extract the current or most recent company the candidate worked at.",
        "years of experience": "Extract the years of experience of the candidate."
    }
    
    extracted_data = {}
    for key, query in queries.items():
        extracted_data[key] = qa_chain.run(query)
    
    return extracted_data

# Main App Layout
with st.sidebar():
    options = option_menu("Choose Stage", ["About The App", "Resume Parser"], menu_icon="gear", icons=['sun', 'moon'])

if options == "About The App":
    st.title("About The App")
    st.write("This application parses resumes using AI and provides insights.")

elif options == "Resume Parser":
    st.title("Resume Parser")
    groq_api_key = st.text_input("Enter your Groq API Key", type="password")
    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "doc", "docx"])
    
    if uploaded_file and groq_api_key:
        documents = process_resume(uploaded_file)
        if documents:
            extracted_data = store_and_retrieve_info(documents, "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")
            for key, value in extracted_data.items():
                st.session_state[key] = value
            
            tab1, tab2, tab3 = st.tabs(["Parsed Information", "View Resume", "Insights"])
            
            with tab1:
                st.header("Extracted Information")
                for key in session_variables:
                    st.write(f"**{key.capitalize()}:** {st.session_state[key]}")
                
            with tab2:
                st.header("Uploaded Resume")
                st.write("Resume preview will be displayed here.")  # Implement file display logic
            
            with tab3:
                st.header("Insights")
                st.write("Advanced resume insights coming soon...")
