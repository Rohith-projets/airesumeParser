import streamlit as st
from streamlit_option_menu import option_menu
import yt_dlp
from streamlit_extras.add_vertical_space import add_vertical_space
from groq import Groq
import re

# Initialize session state variables
if "articles" not in st.session_state:
    st.session_state["articles"] = {}
if "videos" not in st.session_state:
    st.session_state["videos"] = {}

# Function to fetch video transcript or description
def fetch_video_info(url):
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": ["en"],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            transcript = None
            if "subtitles" in info and "en" in info["subtitles"]:
                transcript = " ".join([s["text"] for s in info["subtitles"]["en"]])
            description = info.get("description", "No description available")
            query=(transcript,description)
            return query
    except Exception as e:
        return f"Error: {str(e)}"

# Function to call LLM API
def call_llm(query, api_key):
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a very good educator, content explainer, and professional article writer who writes with simple English."},
                {"role": "user", "content": f"Write a long article on the main concept extracted from this query: {query}."}
            ],
            model="llama-3.3-70b-versatile",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

class ReadArticles:
    def display(self, api_key):
        query = st.chat_input("Ask something...")
        if query:
            if query not in st.session_state["articles"]:
                response = call_llm(query, api_key)
                st.session_state["articles"][query] = response
            st.write(st.session_state["articles"][query])

class VideoLectures:
    def display(self, api_key):
        url = st.text_input("Enter YouTube URL")
        if url:
            if url not in st.session_state["videos"]:
                video_info = fetch_video_info(url)
                if "Error" in video_info:
                    st.error(video_info)
                    return
                response = call_llm(video_info, api_key)
                st.session_state["videos"][url] = [response, ""]  # Store response and empty notes

            col1, col2 = st.columns([1, 1],border=True)
            with col1:
                st.video(url)
                st.write(st.session_state["videos"][url][0])  # Display saved response
                if st.button("Give Response Again", use_container_width=True):
                    response = call_llm(fetch_video_info(url), api_key)
                    st.session_state["videos"][url][0] = response
            with col2:
                notes = st.text_area("Your Notes", value=st.session_state["videos"][url][1], height=3900)
                save = st.button("Save", use_container_width=True)
                if save:
                    st.session_state["videos"][url][1] = notes

class History:
    def display(self):
        choice = st.selectbox("View History", ["Articles", "YouTube Videos"])
        col1, col2 = st.columns([1, 2])
        if choice == "Articles" and st.session_state["articles"]:
            with col1:
                query = st.radio("Saved Queries", list(st.session_state["articles"].keys()))
            with col2:
                st.write(st.session_state["articles"].get(query, ""))
        elif choice == "YouTube Videos" and st.session_state["videos"]:
            with col1:
                url = st.radio("Saved Videos", list(st.session_state["videos"].keys()))
            with col2:
                response, notes = st.session_state["videos"].get(url, ["", ""])
                st.video(url)
                st.write(response)
                st.text_area("Your Notes", notes, height=400)
        else:
            st.write("No history available.")

# Sidebar for API key input
st.sidebar.header("Learning Platform")
api_key = st.sidebar.text_input("Enter Groq API Key", type="password", key="api_key")

# Navigation menu
with st.sidebar:
    selected = option_menu(
        "Menu", ["How To Use This Website","Read Articles", "Learn From YouTube", "Your History"],
        icons=["question","book", "youtube", "clock"],
        menu_icon="menu-hamburger",
        default_index=0
    )

# Route based on selection
if selected=="How To Use This Website":
    st.video("https://youtu.be/iFDMocUeN2g?si=tuWiIasWqt8L7HxU")
elif selected == "Read Articles":
    ReadArticles().display(api_key)
elif selected == "Learn From YouTube":
    VideoLectures().display(api_key)
elif selected == "Your History":
    History().display()
