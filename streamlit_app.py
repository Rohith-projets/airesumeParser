import streamlit as st
from streamlit_option_menu import option_menu
from youtube_transcript_api import YouTubeTranscriptApi
from streamlit_extras.add_vertical_space import add_vertical_space
from groq import Groq
from fpdf import FPDF
import os


if "articles" not in st.session_state:
    st.session_state.articles = {}
if "videos" not in st.session_state:
    st.session_state.videos = {}

def call_llm(query, api_key):
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a very good educator, content explainer, and professional article writer who writes with simple english"},
            {"role": "user", "content": f"Write a long article on this query: {query}."}
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def call_llm_for_video(transcript, api_key):
    client = Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a professional educator and article writer..."},
            {"role": "user", "content": f"Analyze this transcript and write a detailed article: {transcript}"}
        ],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

class ReadArticles:
    def display(self, api_key):
        query = st.chat_input("Ask something...")
        if query:
            response = call_llm(query, api_key)
            st.write(response)
            st.session_state.articles[query] = response

class VideoLectures:
    def display(self, api_key):
        url = st.text_input("Enter YouTube URL")
        if url:
            video_id = url.split("v=")[-1]
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                transcript_text = " ".join([t["text"] for t in transcript])
                response = call_llm_for_video(transcript_text, api_key)
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.video(url)
                    st.write(response)
                with col2:
                    notes = st.text_area("Your Notes", height=400)
                    save = st.button("Save", use_container_width=True)
                    download = st.button("Download", use_container_width=True)
                    if save:
                        st.session_state.videos[url] = [response, notes]
                    if download:
                        pdf = FPDF()
                        pdf.add_page()
                        pdf.set_font("Arial", size=12)
                        pdf.multi_cell(0, 10, f"Video Summary:\n{response}\n\nYour Notes:\n{notes}")
                        pdf_file = f"{video_id}.pdf"
                        pdf.output(pdf_file)
                        st.download_button("Download PDF", pdf_file)
                        os.remove(pdf_file)

class History:
    def display(self):
        choice = st.selectbox("View History", ["Articles", "YouTube Videos"])
        col1, col2 = st.columns([1, 2])
        if choice == "Articles":
            with col1:
                query = st.radio("Saved Queries", list(st.session_state.articles.keys()))
            with col2:
                st.write(st.session_state.articles.get(query, ""))
        else:
            with col1:
                url = st.radio("Saved Videos", list(st.session_state.videos.keys()))
            with col2:
                response, notes = st.session_state.videos.get(url, ["", ""])
                st.video(url)
                st.write(response)
                st.text_area("Your Notes", notes, height=400)

st.sidebar.header("Learning Platform")
api_key=st.sidebar.text_input("Enter Groq API Key", key="api_key")

selected = option_menu(
    "Menu", ["Read Articles", "Learn From YouTube", "Your History"],
    icons=["book", "youtube", "clock"],
    menu_icon="menu-hamburger",
    default_index=0
)

if selected == "Read Articles":
    ReadArticles().display(api_key)
elif selected == "Learn From YouTube":
    VideoLectures().display(api_key)
elif selected == "Your History":
    History().display()
