import streamlit as st
import os
import tempfile
import shutil
from pathlib import Path

# Import utility modules
from utils.video_processor import extract_audio, replace_audio_track
from utils.transcriber import transcribe_audio
from utils.subtitle_generator import generate_subtitle_file, format_time
from utils.translator import translate_subtitles
from utils.audio_generator import generate_dubbed_audio

# Page configuration
st.set_page_config(
    page_title="Video Dubbing App",
    page_icon="🎬",
    layout="wide"
)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'processed_video' not in st.session_state:
    st.session_state.processed_video = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = None

# Language options
LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Tamil": "ta",
    "Arabic": "ar",
    "Chinese (Simplified)": "zh-cn",
    "Japanese": "ja",
    "Korean": "ko",
    "Portuguese": "pt",
    "Russian": "ru",
    "Italian": "it",
    "Dutch": "nl",
    "Polish": "pl",
    "Turkish": "tr",
    "Vietnamese": "vi",
    "Thai": "th",
    "Indonesian": "id",
    "Malay": "ms"
}

def cleanup_temp_dir():
    """Clean up temporary directory"""
    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
        try:
            shutil.rmtree(st.session_state.temp_dir)
            st.session_state.temp_dir = None
        except Exception as e:
            st.error(f"Error cleaning up temporary files: {str(e)}")

def process_video(video_file, target_language, source_language):
    """Process the video through all dubbing steps"""
    try:
        # Create temporary directory for processing
        temp_dir = tempfile.mkdtemp()
        st.session_state.temp_dir = temp_dir
        
        # Save uploaded video to temp directory
        video_path = os.path.join(temp_dir, "input_video.mp4")
        with open(video_path, "wb") as f:
            f.write(video_file.read())
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Extract audio
        status_text.text("🎵 Extracting audio from video...")
        progress_bar.progress(10)
        audio_path = os.path.join(temp_dir, "extracted_audio.wav")
        extract_audio(video_path, audio_path)
        
        # Step 2: Transcribe audio
        status_text.text("📝 Transcribing audio (this may take a few minutes)...")
        progress_bar.progress(25)
        language, segments = transcribe_audio(audio_path)
        
        # Step 3: Generate original subtitle file
        status_text.text("📄 Generating subtitle file...")
        progress_bar.progress(40)
        original_subtitle_path = os.path.join(temp_dir, f"subtitles_{language}.srt")
        generate_subtitle_file(segments, original_subtitle_path)
        
        # Step 4: Translate subtitles
        status_text.text(f"🌐 Translating subtitles to {target_language}...")
        progress_bar.progress(50)
        translated_subtitle_path = os.path.join(temp_dir, f"subtitles_{LANGUAGES[target_language]}.srt")
        translate_subtitles(original_subtitle_path, translated_subtitle_path, 
                          LANGUAGES[target_language], source_language)
        
        # Step 5: Generate dubbed audio
        status_text.text("🎤 Generating dubbed audio (this may take a few minutes)...")
        progress_bar.progress(65)
        dubbed_audio_path = os.path.join(temp_dir, "dubbed_audio.wav")
        generate_dubbed_audio(translated_subtitle_path, dubbed_audio_path, LANGUAGES[target_language])
        
        # Step 6: Replace audio track
        status_text.text("🎬 Creating final dubbed video...")
        progress_bar.progress(85)
        output_video_path = os.path.join(temp_dir, "output_dubbed_video.mp4")
        replace_audio_track(video_path, dubbed_audio_path, output_video_path)
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Video dubbing completed successfully!")
        
        return output_video_path, original_subtitle_path, translated_subtitle_path
        
    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        cleanup_temp_dir()
        return None, None, None

# Main app UI
st.title("🎬 Video Dubbing Application")
st.markdown("""
Upload a video file, select a target language, and get an automatically dubbed version with translated audio.
This application uses local AI models for transcription and translation without requiring external API keys.
""")

# Create two columns for layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Upload Video")
    uploaded_file = st.file_uploader(
        "Choose an MP4 video file",
        type=['mp4'],
        help="Upload the video you want to dub",
        disabled=st.session_state.processing
    )

with col2:
    st.subheader("🌍 Select Language")
    target_language = st.selectbox(
        "Target Language",
        options=list(LANGUAGES.keys()),
        index=5,  # Default to Tamil as in original code
        help="Select the language you want to dub the video into",
        disabled=st.session_state.processing
    )
    
    source_language = st.selectbox(
        "Source Language (optional)",
        options=["Auto-detect"] + list(LANGUAGES.keys()),
        index=0,
        help="Leave as 'Auto-detect' to automatically detect the source language",
        disabled=st.session_state.processing
    )

# Process button
if uploaded_file is not None:
    st.divider()
    
    if st.button("🚀 Start Dubbing Process", disabled=st.session_state.processing, type="primary"):
        st.session_state.processing = True
        
        # Determine source language
        src_lang = "auto" if source_language == "Auto-detect" else LANGUAGES[source_language]
        
        # Process the video
        output_path, original_srt, translated_srt = process_video(
            uploaded_file, 
            target_language,
            src_lang
        )
        
        if output_path and os.path.exists(output_path):
            st.session_state.processed_video = output_path
            st.session_state.original_subtitle = original_srt
            st.session_state.translated_subtitle = translated_srt
        
        st.session_state.processing = False
        st.rerun()

# Display results if processing is complete
if st.session_state.processed_video and os.path.exists(st.session_state.processed_video):
    st.divider()
    st.success("🎉 Your dubbed video is ready!")
    
    # Create download section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with open(st.session_state.processed_video, "rb") as f:
            st.download_button(
                label="⬇️ Download Dubbed Video",
                data=f,
                file_name=f"dubbed_video_{LANGUAGES[target_language]}.mp4",
                mime="video/mp4",
                type="primary"
            )
    
    with col2:
        if st.session_state.original_subtitle and os.path.exists(st.session_state.original_subtitle):
            with open(st.session_state.original_subtitle, "rb") as f:
                st.download_button(
                    label="📄 Original Subtitles (SRT)",
                    data=f,
                    file_name="original_subtitles.srt",
                    mime="text/plain"
                )
    
    with col3:
        if st.session_state.translated_subtitle and os.path.exists(st.session_state.translated_subtitle):
            with open(st.session_state.translated_subtitle, "rb") as f:
                st.download_button(
                    label="📄 Translated Subtitles (SRT)",
                    data=f,
                    file_name=f"translated_subtitles_{LANGUAGES[target_language]}.srt",
                    mime="text/plain"
                )
    
    # Preview video
    st.subheader("🎥 Preview Dubbed Video")
    st.video(st.session_state.processed_video)
    
    # Reset button
    if st.button("🔄 Process Another Video"):
        cleanup_temp_dir()
        st.session_state.processed_video = None
        st.session_state.original_subtitle = None
        st.session_state.translated_subtitle = None
        st.rerun()

# Footer
st.divider()
st.markdown("""
### ℹ️ How it works:
1. **Audio Extraction**: Extracts audio track from the uploaded video
2. **Transcription**: Uses faster-whisper AI model to transcribe speech to text
3. **Translation**: Translates the transcribed text to your target language
4. **Subtitle Generation**: Creates SRT subtitle files for both original and translated text
5. **Audio Generation**: Generates dubbed audio using Google Text-to-Speech
6. **Video Merging**: Replaces the original audio with the dubbed version

**Note**: Processing time depends on video length. Longer videos will take more time to process.
""")
