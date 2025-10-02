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
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items=None
)

# Custom CSS for vibrant, animated styling
st.markdown("""
    <style>
    /* Animated gradient background */
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.8; }
    }
    
    @keyframes slideIn {
        from { transform: translateX(-20px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes shimmer {
        0% { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    
    /* Main container with colorful gradient background */
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradientBG 15s ease infinite;
    }
    
    .main > div {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 30px;
        margin: 20px auto;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        animation: slideIn 0.5s ease-out;
    }
    
    /* Main title styling with rainbow gradient */
    .main h1 {
        font-weight: 800;
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(45deg, #ff6b6b, #ee5a6f, #c06c84, #6c5b7b, #355c7d, #2a9d8f, #e9c46a, #f4a261, #e76f51);
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientBG 8s ease infinite;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        filter: drop-shadow(0 0 20px rgba(255,255,255,0.5));
    }
    
    /* Subtitle and section headers with vibrant colors */
    .main h2 {
        color: #e73c7e;
        font-weight: 700;
        margin-top: 20px;
        animation: float 3s ease-in-out infinite;
    }
    
    .main h3 {
        color: #23a6d5;
        font-weight: 600;
        margin-top: 20px;
    }
    
    /* Colorful card containers */
    .stContainer {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        border-radius: 15px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stContainer:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    /* File uploader with animated border */
    .stFileUploader {
        background: linear-gradient(135deg, #ffeaa7, #fdcb6e, #e17055, #d63031);
        background-size: 300% 300%;
        animation: gradientBG 10s ease infinite;
        border: 3px dashed #ffffff;
        border-radius: 15px;
        padding: 25px;
        transition: all 0.4s ease;
    }
    
    .stFileUploader:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 30px rgba(230, 126, 34, 0.4);
    }
    
    /* Animated buttons */
    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        transition: all 0.3s ease;
        border: none;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255,255,255,0.3);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    /* Colorful primary buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        background-size: 200% 200%;
        animation: gradientBG 3s ease infinite;
        color: white;
        font-size: 1.1em;
    }
    
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
    }
    
    /* Vibrant selectbox */
    .stSelectbox {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-radius: 12px;
        padding: 5px;
        transition: all 0.3s ease;
    }
    
    .stSelectbox:hover {
        transform: scale(1.02);
        box-shadow: 0 5px 15px rgba(168, 237, 234, 0.4);
    }
    
    /* Animated progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #f093fb 0%, #f5576c 25%, #ffd140 50%, #43e97b 75%, #38f9d7 100%);
        background-size: 400% 400%;
        animation: gradientBG 2s ease infinite;
        box-shadow: 0 0 20px rgba(240, 147, 251, 0.6);
    }
    
    /* Colorful alert boxes */
    .stAlert {
        border-radius: 12px;
        border-left: 5px solid;
        padding: 18px;
        animation: slideIn 0.5s ease-out;
        background: linear-gradient(135deg, #ffeaa722 0%, #fdcb6e22 100%);
    }
    
    /* Vibrant text areas */
    .stTextArea textarea {
        border-radius: 12px;
        border: 3px solid transparent;
        background: linear-gradient(white, white) padding-box,
                    linear-gradient(135deg, #667eea, #764ba2, #f093fb) border-box;
        transition: all 0.3s ease;
    }
    
    .stTextArea textarea:focus {
        border-color: transparent;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
        transform: scale(1.01);
    }
    
    /* Colorful divider */
    hr {
        margin: 30px 0;
        border: none;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #667eea);
        background-size: 300% 300%;
        animation: gradientBG 5s ease infinite;
    }
    
    /* Video player with glow effect */
    video {
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        animation: pulse 3s ease-in-out infinite;
    }
    
    /* Animated download buttons */
    .stDownloadButton > button {
        width: 100%;
        padding: 15px 24px;
        border-radius: 12px;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
    }
    
    /* Spacing improvements */
    .element-container {
        margin-bottom: 20px;
        animation: slideIn 0.6s ease-out;
    }
    
    /* Enhanced subtitle review section with colors */
    .subtitle-pair {
        background: linear-gradient(135deg, #ffffff 0%, #ffeaa7 100%);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(253, 203, 110, 0.3);
        border-left: 5px solid #fdcb6e;
        transition: all 0.3s ease;
    }
    
    .subtitle-pair:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(253, 203, 110, 0.5);
    }
    
    /* Success message with celebration colors */
    .stSuccess {
        background: linear-gradient(135deg, #43e97b22 0%, #38f9d722 100%);
        border-left-color: #43e97b !important;
        animation: float 2s ease-in-out infinite;
    }
    
    /* Info message colorful */
    .stInfo {
        background: linear-gradient(135deg, #667eea22 0%, #764ba222 100%);
        border-left-color: #667eea !important;
    }
    
    /* Subheader badges with colors */
    .main .stMarkdown h2::before,
    .main .stMarkdown h3::before {
        content: '✨';
        margin-right: 10px;
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Fix mobile view text truncation */
    @media (max-width: 768px) {
        .stFileUploader label small {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: clip !important;
            word-wrap: break-word !important;
            display: block !important;
        }
    }
    
    /* Progress tracker styling */
    .progress-tracker {
        background: white;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        padding: 15px;
        margin: 10px 0;
        border-radius: 10px;
        transition: all 0.3s ease;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .progress-step.completed {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 5px solid #28a745;
    }
    
    .progress-step.processing {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border-left: 5px solid #ffc107;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .progress-step.pending {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-left: 5px solid #6c757d;
    }
    
    .progress-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 15px;
        font-size: 1.2em;
        font-weight: bold;
    }
    
    .progress-icon.completed {
        background: #28a745;
        color: white;
        animation: checkmark 0.5s ease-in-out;
    }
    
    .progress-icon.processing {
        background: #ffc107;
        color: white;
        animation: spin 2s linear infinite;
    }
    
    .progress-icon.pending {
        background: #6c757d;
        color: white;
    }
    
    @keyframes checkmark {
        0% { transform: scale(0); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .progress-text {
        flex: 1;
        font-weight: 600;
        color: #2c3e50;
    }
    
    .progress-text.completed {
        color: #28a745;
    }
    
    .progress-text.processing {
        color: #ffc107;
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
if 'progress_status' not in st.session_state:
    st.session_state.progress_status = {
        'audio_extraction': 'pending',
        'transcription': 'pending',
        'translation': 'pending',
        'subtitle_generation': 'pending',
        'audio_generation': 'pending',
        'video_merging': 'pending'
    }
if 'start_stage2' not in st.session_state:
    st.session_state.start_stage2 = False

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

def display_progress_tracker():
    """Display animated progress tracker for video processing"""
    tasks = [
        ('audio_extraction', '🎵 Audio Extraction', 'Extracting audio from video'),
        ('transcription', '📝 Transcription', 'Converting speech to text'),
        ('translation', '🌐 Translation', 'Translating to target language'),
        ('subtitle_generation', '📄 Subtitle Generation', 'Creating subtitle files'),
        ('audio_generation', '🎤 Audio Generation', 'Generating dubbed audio'),
        ('video_merging', '🎬 Video Merging', 'Creating final video')
    ]
    
    st.markdown("<div class='progress-tracker'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #667eea; margin-bottom: 20px;'>📊 Processing Status</h3>", unsafe_allow_html=True)
    
    for task_id, task_name, task_desc in tasks:
        status = st.session_state.progress_status[task_id]
        
        if status == 'completed':
            icon = '✓'
            icon_class = 'completed'
        elif status == 'processing':
            icon = '⟳'
            icon_class = 'processing'
        else:
            icon = '○'
            icon_class = 'pending'
        
        st.markdown(f"""
        <div class='progress-step {status}'>
            <div class='progress-icon {icon_class}'>{icon}</div>
            <div class='progress-text {status}'>
                <strong>{task_name}</strong>
                <br><small style='opacity: 0.8;'>{task_desc}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def cleanup_temp_dir():
    """Clean up temporary directory"""
    if st.session_state.temp_dir and os.path.exists(st.session_state.temp_dir):
        try:
            shutil.rmtree(st.session_state.temp_dir)
            st.session_state.temp_dir = None
        except Exception as e:
            st.error(f"Error cleaning up temporary files: {str(e)}")

def reset_progress_status():
    """Reset all progress statuses to pending"""
    st.session_state.progress_status = {
        'audio_extraction': 'pending',
        'transcription': 'pending',
        'translation': 'pending',
        'subtitle_generation': 'pending',
        'audio_generation': 'pending',
        'video_merging': 'pending'
    }

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
        
        progress_container = st.empty()
        status_text = st.empty()
        progress_bar = st.progress(0)
        
        # Step 1: Extract audio
        st.session_state.progress_status['audio_extraction'] = 'processing'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        status_text.text("🎵 Extracting audio from video...")
        progress_bar.progress(20)
        audio_path = os.path.join(temp_dir, "extracted_audio.wav")
        extract_audio(video_path, audio_path)
        st.session_state.progress_status['audio_extraction'] = 'completed'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        
        # Step 2: Transcribe audio
        st.session_state.progress_status['transcription'] = 'processing'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        status_text.text("📝 Transcribing audio (this may take a few minutes)...")
        progress_bar.progress(40)
        language, segments = transcribe_audio(audio_path)
        st.session_state.progress_status['transcription'] = 'completed'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        
        # Step 3: Generate original subtitle file
        st.session_state.progress_status['subtitle_generation'] = 'processing'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        status_text.text("📄 Generating subtitle file...")
        progress_bar.progress(60)
        original_subtitle_path = os.path.join(temp_dir, f"subtitles_{language}.srt")
        generate_subtitle_file(segments, original_subtitle_path)
        
        # Step 4: Translate subtitles
        st.session_state.progress_status['translation'] = 'processing'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        status_text.text(f"🌐 Translating subtitles to {target_language}...")
        progress_bar.progress(80)
        translated_subtitle_path = os.path.join(temp_dir, f"subtitles_{LANGUAGES[target_language]}.srt")
        translate_subtitles(original_subtitle_path, translated_subtitle_path, 
                          LANGUAGES[target_language], source_language)
        st.session_state.progress_status['translation'] = 'completed'
        st.session_state.progress_status['subtitle_generation'] = 'completed'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        
        # Complete stage 1
        progress_bar.progress(100)
        status_text.text("✅ Subtitles ready for review!")
        
        return video_path, audio_path, original_subtitle_path, translated_subtitle_path
        
    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        cleanup_temp_dir()
        reset_progress_status()
        return None, None, None, None

def process_video_stage2(video_path, translated_subtitle_path, target_lang_code, progress_container):
    """Stage 2: Generate dubbed audio and create final video"""
    try:
        temp_dir = st.session_state.temp_dir
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Step 1: Generate dubbed audio
        st.session_state.progress_status['audio_generation'] = 'processing'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        status_text.text("🎤 Generating dubbed audio (this may take a few minutes)...")
        progress_bar.progress(30)
        dubbed_audio_path = os.path.join(temp_dir, "dubbed_audio.wav")
        generate_dubbed_audio(translated_subtitle_path, dubbed_audio_path, target_lang_code)
        st.session_state.progress_status['audio_generation'] = 'completed'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        
        # Step 2: Replace audio track
        st.session_state.progress_status['video_merging'] = 'processing'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        status_text.text("🎬 Creating final dubbed video...")
        progress_bar.progress(70)
        output_video_path = os.path.join(temp_dir, "output_dubbed_video.mp4")
        replace_audio_track(video_path, dubbed_audio_path, output_video_path)
        st.session_state.progress_status['video_merging'] = 'completed'
        progress_container.empty()
        with progress_container.container():
            display_progress_tracker()
        
        # Complete
        progress_bar.progress(100)
        status_text.text("✅ Video dubbing completed successfully!")
        
        return output_video_path
        
    except Exception as e:
        st.error(f"Error during dubbing: {str(e)}")
        reset_progress_status()
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
    st.markdown("<h3 style='color: #e73c7e; font-weight: 700;'>📤 Upload Video</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose an MP4 video file",
        type=['mp4'],
        help="Upload the video you want to dub",
        disabled=st.session_state.processing
    )

with col2:
    st.markdown("<h3 style='color: #23a6d5; font-weight: 700;'>🌍 Select Language</h3>", unsafe_allow_html=True)
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
        reset_progress_status()
        
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

# Stage 2 Processing (after review approval)
if st.session_state.start_stage2 and not st.session_state.processed_video:
    st.session_state.processing = True
    
    # Create progress container in the same location as stage 1
    progress_container = st.empty()
    
    # Process stage 2 - Generate dubbed video
    output_path = process_video_stage2(
        st.session_state.video_path,
        st.session_state.translated_subtitle,
        st.session_state.target_lang_code,
        progress_container
    )
    
    if output_path and os.path.exists(output_path):
        st.session_state.processed_video = output_path
        st.session_state.start_stage2 = False
    
    st.session_state.processing = False
    st.rerun()

# Subtitle Review Stage
if st.session_state.review_stage and not st.session_state.processed_video:
    st.divider()
    st.success("✅ Subtitles are ready for review!")
    st.markdown("<h3 style='color: #2a9d8f; font-weight: 700; text-align: center;'>📝 Review and Edit Subtitles</h3>", unsafe_allow_html=True)
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
                # Update translated subtitles data with edited text
                for i, sub in enumerate(st.session_state.translated_subtitles_data):
                    sub['text'] = st.session_state.edited_translations[i]
                
                # Save edited subtitles
                save_edited_subtitles(
                    st.session_state.translated_subtitles_data,
                    st.session_state.translated_subtitle
                )
                
                # Set flag to start stage 2 and hide review
                st.session_state.start_stage2 = True
                st.session_state.review_stage = False
                st.session_state.edited_translations = {}
                st.rerun()
        
        with col3:
            if st.button("🔄 Start Over", use_container_width=True):
                cleanup_temp_dir()
                reset_progress_status()
                st.session_state.review_stage = False
                st.session_state.start_stage2 = False
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
        reset_progress_status()
        st.session_state.processed_video = None
        st.session_state.original_subtitle = None
        st.session_state.translated_subtitle = None
        st.session_state.review_stage = False
        st.session_state.start_stage2 = False
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
