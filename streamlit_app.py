import streamlit as st
from streamlit_option_menu import option_menu
import time
from groq import Groq

def call_llm(query):
    client = Groq(api_key="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")
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
            {"role": "system", "content": "You are a very good educator, capable of explaining anything."},
            {"role": "user", "content": f"Act like an article writer and write article on {query}, the article aims to explain the content with simple English and a lot of examples. The article should teach the content rather than just displaying it."}
        ]
    )
    return response.choices[0].message.content

# Initialize session state for storing generated content
if "generated_content" not in st.session_state:
    st.session_state["generated_content"] = {}

# Sidebar with option menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Generate Educational Content", "View Generated Content"],
        icons=["book", "eye"],
        menu_icon="cast",
        default_index=0
    )

if selected == "Generate Educational Content":
    query = st.chat_input("Enter a topic to generate educational content:")
    if query:
        with st.spinner("Generating content..."):
            content = call_llm(query)
            st.session_state["generated_content"][query] = content
        st.subheader("Generated Content")
            st.write(content)
elif selected == "View Generated Content":
    if st.session_state["generated_content"]:
        topic = st.selectbox("Select a topic:", list(st.session_state["generated_content"].keys()))
        if topic:
            st.subheader(f"Educational Content on: {topic}")
            st.write(st.session_state["generated_content"][topic])
    else:
        st.write("No content generated yet.")
