import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.metric_cards import *
from groq import Groq
from pyresparser import ResumeParser
import nltk

session_options = ['college_name', 'company_names', 'degree', 'designation', 'email','mobile_number','name','no_of_pages','skills','total_experience','count']
for i in session_options:
    if i not in st.session_state:
        st.session_state[i] = None

if "session_dict" not in st.session_state:
    st.session_state["session_dict"] = {}

def primary_info(file):
    try:
        if not check_status() and file is not None:
            nltk.download('stopwords')  # Ensure stopwords are available
            nltk.download('punkt')  # Some parsers require this too
            from nltk.corpus import stopwords  # Import after downloading

            parsed_document = ResumeParser(file)
            result_dict = parsed_document.get_extracted_data()
            if result_dict:
                st.session_state['college_name'] = result_dict.get('college_name')
                st.session_state['company_names'] = result_dict.get('company_names')
                st.session_state['degree'] = result_dict.get('degree')
                st.session_state['designation'] = result_dict.get('designation')
                st.session_state['email'] = result_dict.get('email')
                st.session_state['mobile_number'] = result_dict.get('mobile_number')
                st.session_state['name'] = result_dict.get('name')
                st.session_state['no_of_pages'] = result_dict.get('no_of_pages')
                st.session_state['skills'] = result_dict.get('skills')
                st.session_state['total_experience'] = result_dict.get('total_experience')
                st.session_state['count'] = 1
    except Exception as e:
        st.error(f"You got the following error: {e}")


def insights():
    pass

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
