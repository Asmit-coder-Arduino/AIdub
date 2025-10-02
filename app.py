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

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    /* Main title styling */
    .main h1 {
        color: #1f77b4;
        font-weight: 700;
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Subtitle and section headers */
    .main h2, .main h3 {
        color: #2c3e50;
        font-weight: 600;
        margin-top: 20px;
    }
    
    /* Card-like containers for sections */
    .stContainer {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* File uploader styling */
    .stFileUploader {
        background-color: white;
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        border-color: #764ba2;
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Primary button enhancement */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Selectbox styling */
    .stSelectbox {
        background-color: white;
        border-radius: 8px;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Info/Success/Warning boxes */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid;
        padding: 15px;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        transition: border-color 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
    }
    
    /* Divider styling */
    hr {
        margin: 30px 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
    
    /* Video player styling */
    video {
        border-radius: 12px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    /* Download button section */
    .stDownloadButton > button {
        width: 100%;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Footer styling */
    .main > div:last-child {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin-top: 30px;
    }
    
    /* Spacing improvements */
    .element-container {
        margin-bottom: 15px;
    }
    
    /* Enhanced subtitle review section */
    .subtitle-pair {
        background-color: white;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'processed_video' not in st.session_state:
    st.session_state.processed_video = None
if 'temp_dir' not in st.session_state:
    st.session_state.temp_dir = None
if 'review_stage' not in st.session_state:
    st.session_state.review_stage = False
if 'original_subtitles_data' not in st.session_state:
    st.session_state.original_subtitles_data = []
if 'translated_subtitles_data' not in st.session_state:
    st.session_state.translated_subtitles_data = []
if 'video_path' not in st.session_state:
    st.session_state.video_path = None
if 'audio_path' not in st.session_state:
    st.session_state.audio_path = None
if 'target_lang_code' not in st.session_state:
    st.session_state.target_lang_code = None

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

def read_srt_file(srt_path):
    """Read and parse SRT file into a list of subtitle dictionaries"""
    import pysrt
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')
        subtitles_data = []
        for sub in subs:
            subtitles_data.append({
                'index': sub.index,
                'start': str(sub.start),
                'end': str(sub.end),
                'text': sub.text
            })
        return subtitles_data
    except Exception as e:
        st.error(f"Error reading SRT file: {str(e)}")
        return []

def save_edited_subtitles(subtitles_data, output_path):
    """Save edited subtitles back to SRT file"""
    import pysrt
    try:
        subs = pysrt.SubRipFile()
        for sub_data in subtitles_data:
            sub = pysrt.SubRipItem(
                index=sub_data['index'],
                start=sub_data['start'],
                end=sub_data['end'],
                text=sub_data['text']
            )
            subs.append(sub)
        subs.save(output_path, encoding='utf-8')
    except Exception as e:
        st.error(f"Error saving edited subtitles: {str(e)}")

def process_video_stage1(video_file, target_language, source_language):
    """Stage 1: Transcribe and translate subtitles for review"""
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
        progress_bar.progress(20)
        audio_path = os.path.join(temp_dir, "extracted_audio.wav")
        extract_audio(video_path, audio_path)
        
        # Step 2: Transcribe audio
        status_text.text("📝 Transcribing audio (this may take a few minutes)...")
        progress_bar.progress(40)
        language, segments = transcribe_audio(audio_path)
        
        # Step 3: Generate original subtitle file
        status_text.text("📄 Generating subtitle file...")
        progress_bar.progress(60)
        original_subtitle_path = os.path.join(temp_dir, f"subtitles_{language}.srt")
        generate_subtitle_file(segments, original_subtitle_path)
        
        # Step 4: Translate subtitles
        status_text.text(f"🌐 Translating subtitles to {target_language}...")
        progress_bar.progress(80)
        translated_subtitle_path = os.path.join(temp_dir, f"subtitles_{LANGUAGES[target_language]}.srt")
        translate_subtitles(original_subtitle_path, translated_subtitle_path, 
                          LANGUAGES[target_language], source_language)
        
        # Complete stage 1
        progress_bar.progress(100)
        status_text.text("✅ Subtitles ready for review!")
        
        return video_path, audio_path, original_subtitle_path, translated_subtitle_path
        
    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        cleanup_temp_dir()
        return None, None, None, None

def process_video_stage2(video_path, translated_subtitle_path, target_lang_code):
    """Stage 2: Generate dubbed audio and create final video"""
    try:
        temp_dir = st.session_state.temp_dir
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Generate dubbed audio
        status_text.text("🎤 Generating dubbed audio (this may take a few minutes)...")
        progress_bar.progress(30)
        dubbed_audio_path = os.path.join(temp_dir, "dubbed_audio.wav")
        generate_dubbed_audio(translated_subtitle_path, dubbed_audio_path, target_lang_code)
        
        # Step 2: Replace audio track
        status_text.text("🎬 Creating final dubbed video...")
        progress_bar.progress(70)
        output_video_path = os.path.join(temp_dir, "output_dubbed_video.mp4")
        replace_audio_track(video_path, dubbed_audio_path, output_video_path)
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Video dubbing completed successfully!")
        
        return output_video_path
        
    except Exception as e:
        st.error(f"Error during dubbing: {str(e)}")
        return None

# Main app UI
st.title("🎬 Video Dubbing Application")
st.markdown("""
<div style='text-align: center; padding: 10px 0 30px 0;'>
    <p style='font-size: 1.2em; color: #555; margin-bottom: 10px;'>
        Transform your videos with AI-powered dubbing in multiple languages
    </p>
    <p style='color: #777; font-size: 0.95em;'>
        Upload a video, select your target language, and get a professionally dubbed version with translated audio.<br/>
        ✨ Powered by local AI models • No external API keys required • 100% private and secure
    </p>
</div>
""", unsafe_allow_html=True)

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
        index=4,  # Default to Hindi
        help="Select the language you want to dub the video into",
        disabled=st.session_state.processing
    )
    
    source_language = st.selectbox(
        "Source Language",
        options=list(LANGUAGES.keys()),
        index=0,
        help="Select the source language of your video",
        disabled=st.session_state.processing
    )

# Process button
if uploaded_file is not None and not st.session_state.review_stage:
    st.divider()
    
    if st.button("🚀 Start Dubbing Process", disabled=st.session_state.processing, type="primary"):
        st.session_state.processing = True
        
        # Get source language code
        src_lang = LANGUAGES[source_language]
        
        # Process the video - Stage 1 (transcribe and translate)
        video_path, audio_path, original_srt, translated_srt = process_video_stage1(
            uploaded_file, 
            target_language,
            src_lang
        )
        
        if original_srt and translated_srt:
            # Read and store subtitle data for review
            st.session_state.original_subtitles_data = read_srt_file(original_srt)
            st.session_state.translated_subtitles_data = read_srt_file(translated_srt)
            st.session_state.video_path = video_path
            st.session_state.audio_path = audio_path
            st.session_state.original_subtitle = original_srt
            st.session_state.translated_subtitle = translated_srt
            st.session_state.target_lang_code = LANGUAGES[target_language]
            st.session_state.review_stage = True
        
        st.session_state.processing = False
        st.rerun()

# Subtitle Review Stage
if st.session_state.review_stage and not st.session_state.processed_video:
    st.divider()
    st.success("✅ Subtitles are ready for review!")
    st.markdown("### 📝 Review and Edit Subtitles")
    st.info("Compare the original and translated subtitles below. You can edit the translated text before generating the dubbed audio.")
    
    # Create scrollable container for subtitles
    if st.session_state.original_subtitles_data and st.session_state.translated_subtitles_data:
        # Store edited translations in session state if not already there
        if 'edited_translations' not in st.session_state:
            st.session_state.edited_translations = {
                i: sub['text'] for i, sub in enumerate(st.session_state.translated_subtitles_data)
            }
        
        # Display subtitle pairs
        st.markdown("---")
        
        for i, (orig_sub, trans_sub) in enumerate(zip(
            st.session_state.original_subtitles_data,
            st.session_state.translated_subtitles_data
        )):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**#{orig_sub['index']} - {orig_sub['start']} → {orig_sub['end']}**")
                st.text_area(
                    f"Original {i}",
                    value=orig_sub['text'],
                    height=80,
                    disabled=True,
                    key=f"orig_{i}",
                    label_visibility="collapsed"
                )
            
            with col2:
                st.markdown(f"**#{trans_sub['index']} - {trans_sub['start']} → {trans_sub['end']}**")
                edited_text = st.text_area(
                    f"Translated {i}",
                    value=st.session_state.edited_translations[i],
                    height=80,
                    key=f"trans_{i}",
                    label_visibility="collapsed"
                )
                # Update edited translation in session state
                st.session_state.edited_translations[i] = edited_text
            
            if i < len(st.session_state.original_subtitles_data) - 1:
                st.markdown("---")
        
        # Approval buttons
        st.divider()
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("✅ Approve and Generate Dubbed Video", type="primary", use_container_width=True):
                st.session_state.processing = True
                
                # Update translated subtitles data with edited text
                for i, sub in enumerate(st.session_state.translated_subtitles_data):
                    sub['text'] = st.session_state.edited_translations[i]
                
                # Save edited subtitles
                save_edited_subtitles(
                    st.session_state.translated_subtitles_data,
                    st.session_state.translated_subtitle
                )
                
                # Process stage 2 - Generate dubbed video
                output_path = process_video_stage2(
                    st.session_state.video_path,
                    st.session_state.translated_subtitle,
                    st.session_state.target_lang_code
                )
                
                if output_path and os.path.exists(output_path):
                    st.session_state.processed_video = output_path
                    st.session_state.review_stage = False
                    st.session_state.edited_translations = {}
                
                st.session_state.processing = False
                st.rerun()
        
        with col3:
            if st.button("🔄 Start Over", use_container_width=True):
                cleanup_temp_dir()
                st.session_state.review_stage = False
                st.session_state.original_subtitles_data = []
                st.session_state.translated_subtitles_data = []
                st.session_state.edited_translations = {}
                st.session_state.video_path = None
                st.session_state.audio_path = None
                st.rerun()

# Display results if processing is complete
if st.session_state.processed_video and os.path.exists(st.session_state.processed_video):
    st.divider()
    st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); border-radius: 10px; margin: 20px 0;'>
        <h2 style='color: #667eea; margin: 0;'>🎉 Your Dubbed Video is Ready!</h2>
        <p style='color: #666; margin-top: 10px;'>Download your files below and preview the result</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create download section
    st.markdown("<h3 style='text-align: center; color: #2c3e50; margin: 30px 0 20px 0;'>📥 Download Files</h3>", unsafe_allow_html=True)
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
        st.session_state.review_stage = False
        st.session_state.original_subtitles_data = []
        st.session_state.translated_subtitles_data = []
        st.session_state.edited_translations = {}
        st.session_state.video_path = None
        st.session_state.audio_path = None
        st.session_state.target_lang_code = None
        st.rerun()

# Footer
st.divider()
st.markdown("""
<div style='background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 30px; border-radius: 15px; margin-top: 40px;'>
    <h3 style='color: #2c3e50; text-align: center; margin-bottom: 25px;'>ℹ️ How It Works</h3>
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;'>
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='color: #667eea; margin-bottom: 10px;'>🎵 1. Audio Extraction</h4>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>Extracts the audio track from your uploaded video file</p>
        </div>
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='color: #667eea; margin-bottom: 10px;'>📝 2. Transcription</h4>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>Uses faster-whisper AI to transcribe speech to text</p>
        </div>
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='color: #667eea; margin-bottom: 10px;'>🌐 3. Translation</h4>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>Translates transcribed text to your target language</p>
        </div>
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='color: #667eea; margin-bottom: 10px;'>📄 4. Subtitle Generation</h4>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>Creates SRT files for original and translated text</p>
        </div>
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='color: #667eea; margin-bottom: 10px;'>🎤 5. Audio Generation</h4>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>Generates dubbed audio using Text-to-Speech</p>
        </div>
        <div style='background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <h4 style='color: #667eea; margin-bottom: 10px;'>🎬 6. Video Merging</h4>
            <p style='color: #666; font-size: 0.9em; margin: 0;'>Replaces original audio with the dubbed version</p>
        </div>
    </div>
    <p style='text-align: center; color: #555; margin-top: 25px; font-size: 0.9em;'>
        ⏱️ <strong>Note:</strong> Processing time depends on video length. Longer videos will take more time to process.
    </p>
</div>
""", unsafe_allow_html=True)
