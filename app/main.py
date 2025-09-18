import streamlit as st
from utils.transcript import get_video_transcript
from utils.summarizer import summarize_text, translate_to_english
from utils.qa import ask_question_about_text
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenRouter API key and base URL
api_key = os.getenv("GROQ_API_KEY") 
if not api_key:
    st.error("⚠️ API Key Missing! Please set either OPENROUTER_API_KEY or OPENAI_API_KEY environment variable.")
    st.info("You can create a .env file in the project root with: OPENROUTER_API_KEY=your_key_here")
    st.stop()

Groq.api_key = api_key
Groq.api_base = "https://api.groq.com"  # Correct API base

st.title("Welcome to YouTube Assistant")

# Initialize session state for caching transcript
if "transcript_cache" not in st.session_state:
    st.session_state.transcript_cache = {}

# Function to extract video ID from URL
def extract_video_id(video_url):
    import re
    
    if not video_url or not isinstance(video_url, str):
        return None
    
    # Remove any whitespace
    video_url = video_url.strip()
    
    # Common YouTube URL patterns
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*&v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, video_url)
        if match:
            return match.group(1)
    
    # If no pattern matches, try to extract from the end of the URL
    # This handles cases where the URL might be malformed but contains a video ID
    if len(video_url) >= 11:
        # Look for 11-character alphanumeric strings that could be video IDs
        potential_ids = re.findall(r'[a-zA-Z0-9_-]{11}', video_url)
        if potential_ids:
            return potential_ids[0]
    
    return None

# Tabs for functionality
tab1, tab2 = st.tabs(["Summarize", "Ask a Question"])

with tab1:
    st.header("Summarize a YouTube Video")
    video_url = st.text_input("Enter YouTube video URL:", key="summarize_url")
    translate_option = st.checkbox("Translate summary to English", value=True, help="If the video/transcript is in another language, translate the summary to English.")
    if st.button("Fetch and Summarize", key="summarize_button"):
        video_id = extract_video_id(video_url)
        # Debug information
        st.info(f"Input URL: {video_url}")
        st.info(f"Extracted Video ID: {video_id}")
        
        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid URL.")
            st.info("Supported formats: youtube.com/watch?v=VIDEO_ID, youtu.be/VIDEO_ID, etc.")
        else:
            # Check if transcript is already cached
            if video_id not in st.session_state.transcript_cache:
                with st.spinner("Fetching video transcript..."):
                    st.session_state.transcript_cache[video_id] = get_video_transcript(video_id)
            transcript = st.session_state.transcript_cache[video_id]

            if "error" in transcript.lower():
                st.error(transcript)
            elif transcript:
                with st.spinner("Summarizing video content..."):
                    summary = summarize_text(transcript)
                if summary and "error" not in summary.lower():
                    if translate_option:
                        with st.spinner("Translating summary to English..."):
                            translated = translate_to_english(summary)
                        if translated and "error" not in translated.lower():
                            st.subheader("Video Summary (English):")
                            st.markdown(translated)
                        else:
                            st.subheader("Video Summary:")
                            st.markdown(summary)
                            st.info("Translation unavailable; showing original summary.")
                    else:
                        st.subheader("Video Summary:")
                        st.markdown(summary)
                else:
                    st.error("Error summarizing the transcript: " + summary)
            else:
                st.error("No transcript available. Please check the video URL.")

with tab2:
    st.header("Ask a Question About a YouTube Video")
    video_url = st.text_input("Enter YouTube video URL for Q&A:", key="qa_url")
    question = st.text_input("Enter your question:", key="question_input")
    if st.button("Get Answer", key="qa_button"):
        video_id = extract_video_id(video_url)
        # Debug information
        st.info(f"Input URL: {video_url}")
        st.info(f"Extracted Video ID: {video_id}")
        
        if not video_id:
            st.error("Invalid YouTube URL. Please enter a valid URL.")
            st.info("Supported formats: youtube.com/watch?v=VIDEO_ID, youtu.be/VIDEO_ID, etc.")
        elif not question.strip():
            st.error("Please enter a question.")
        else:
            # Check if transcript is already cached
            if video_id not in st.session_state.transcript_cache:
                with st.spinner("Fetching video transcript..."):
                    st.session_state.transcript_cache[video_id] = get_video_transcript(video_id)
            transcript = st.session_state.transcript_cache[video_id]

            if "error" in transcript.lower():
                st.error(transcript)
            elif transcript:
                with st.spinner("Processing your question..."):
                    answer = ask_question_about_text(transcript, question)
                if answer and "error" not in answer.lower():
                    st.subheader("Answer:")
                    st.markdown(answer)
                else:
                    st.error("Error processing your question: " + answer)
            else:
                st.error("No transcript available. Please check the video URL.")

# Optional: Debug section to view transcript
with st.expander("Debug: View Cached Transcript", expanded=False):
    if st.session_state.transcript_cache:
        video_id = st.selectbox("Select video ID:", list(st.session_state.transcript_cache.keys()))
        if video_id:
            st.text_area("Transcript", st.session_state.transcript_cache[video_id], height=200)