import streamlit as st
from streamlit_option_menu import option_menu
import yt_dlp
from streamlit_extras.add_vertical_space import add_vertical_space
from groq import Groq
from fpdf import FPDF
import os
import re
import speech_recognition as sr
from pydub import AudioSegment
import imageio

# Ensure ffmpeg is available
imageio.plugins.ffmpeg.download()
ffmpeg_path = imageio.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

# Initialize session state variables
if "articles" not in st.session_state:
    st.session_state["articles"] = {}
if "videos" not in st.session_state:
    st.session_state["videos"] = {}

# Function to extract audio from YouTube video
def extract_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'audio.%(ext)s',
        'ffmpeg_location': ffmpeg_path,  # Set the ffmpeg path
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return "audio.mp3"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert audio to text
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    audio = AudioSegment.from_mp3(audio_file)
    audio.export("audio.wav", format="wav")
    with sr.AudioFile("audio.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except Exception as e:
            return f"Error: {str(e)}"

# Function to call LLM API
def call_llm(query, api_key):
    try:
        client = Groq(api_key=api_key)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a very good educator, content explainer, and professional article writer who writes with simple English."},
                {"role": "user", "content": f"Write a long article on this query: {query}."}
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
            response = call_llm(query, api_key)
            st.write(response)
            st.session_state["articles"][query] = response

class VideoLectures:
    def display(self, api_key):
        url = st.text_input("Enter YouTube URL")
        if url:
            try:
                audio_file = extract_audio(url)
                if "Error" not in audio_file:
                    description = audio_to_text(audio_file)
                    response = call_llm(description, api_key)
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.video(url)
                        st.write(response)
                    with col2:
                        notes = st.text_area("Your Notes", height=400)
                        save = st.button("Save", use_container_width=True)
                        download = st.button("Download", use_container_width=True)
                        if save:
                            st.session_state["videos"][url] = [response, notes]
                        if download:
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            pdf.multi_cell(0, 10, f"Video Summary:\n{response}\n\nYour Notes:\n{notes}")
                            pdf_file = f"{re.sub('[^a-zA-Z0-9]', '_', url)}.pdf"
                            pdf.output(pdf_file)
                            with open(pdf_file, "rb") as file:
                                st.download_button("Download PDF", file, file_name=pdf_file)
                            os.remove(pdf_file)
                else:
                    st.error(audio_file)
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")

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
        "Menu", ["Read Articles", "Learn From YouTube", "Your History"],
        icons=["book", "youtube", "clock"],
        menu_icon="menu-hamburger",
        default_index=0
    )

# Route based on selection
if selected == "Read Articles":
    ReadArticles().display(api_key)
elif selected == "Learn From YouTube":
    VideoLectures().display(api_key)
elif selected == "Your History":
    History().display()
