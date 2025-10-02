# Video Dubbing Application

## Overview

This is a Streamlit-based video dubbing application that automates the process of translating and dubbing videos into different languages. The application extracts audio from videos, transcribes it using AI speech recognition, translates the transcription, generates dubbed audio in the target language, and produces a final video with the new audio track.

The application follows a modular architecture with separate utility modules handling distinct aspects of the video dubbing pipeline: video processing, audio transcription, subtitle generation, translation, and text-to-speech synthesis.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Technology**: Streamlit web framework

The application uses Streamlit for its web interface, providing an interactive UI for video upload, language selection, and processing controls. Custom CSS animations and styling create an engaging user experience with gradient backgrounds, floating elements, and smooth transitions.

**Design Pattern**: Single-page application with step-by-step workflow
- Users upload videos through file upload widgets
- Progress is displayed using Streamlit's progress bars and status messages
- Results are downloadable through the interface

### Backend Architecture

**Processing Pipeline**: Sequential task execution

The application follows a linear processing pipeline:

1. **Video Input** → Extract audio from uploaded video
2. **Audio Extraction** → Transcribe audio to text using Whisper AI
3. **Transcription** → Generate timestamped subtitles (SRT format)
4. **Subtitle Generation** → Translate subtitles to target language
5. **Translation** → Generate dubbed audio using text-to-speech
6. **Audio Synthesis** → Replace original audio track with dubbed version
7. **Video Output** → Produce final dubbed video

**Rationale**: This pipeline approach ensures each step completes before the next begins, making debugging easier and allowing for intermediate file inspection. While less performant than parallel processing, it provides better error handling and transparency for users.

### Modular Component Design

**Structure**: Utility modules organized by function

Each processing step is isolated in its own utility module:

- `video_processor.py` - FFmpeg and MoviePy operations for video/audio manipulation
- `transcriber.py` - Faster-Whisper integration for speech-to-text
- `subtitle_generator.py` - SRT file format generation with precise timing
- `translator.py` - Text translation using the translate library
- `audio_generator.py` - Text-to-speech synthesis with gTTS and audio timing alignment

**Benefits**: 
- Clear separation of concerns
- Easy to test individual components
- Simple to swap implementations (e.g., changing translation service)
- Reusable functions across different workflows

**Tradeoffs**: Adds file organization overhead but significantly improves maintainability

### File Processing Strategy

**Approach**: Temporary file system storage

All intermediate files (extracted audio, subtitle files, dubbed audio) are stored in temporary directories using Python's `tempfile` module. Files are cleaned up after processing completes.

**Rationale**: Streamlit runs in a stateless environment, so persistent storage isn't required. Temporary files reduce disk usage and prevent accumulation of processed media. This approach works well for single-user deployments but would need modification for multi-tenant scenarios.

### Audio Timing Synchronization

**Method**: Subtitle-based timing with silence padding

The dubbed audio generation uses SRT subtitle timestamps to position speech segments accurately:
- Each translated subtitle segment is converted to speech
- Silent audio segments fill gaps between speech
- Audio segments are concatenated to match original video timing

**Challenge Addressed**: Different languages have different speaking speeds. The current implementation may result in timing mismatches if translated text is significantly longer/shorter than original.

**Alternative Considered**: Speed adjustment of generated audio to fit original timing windows. Not implemented due to potential voice distortion.

## External Dependencies

### AI/ML Services

**Faster-Whisper** - Speech recognition model
- Purpose: Transcribe video audio to text with timestamps
- Model: "small" variant running on CPU with int8 quantization
- Tradeoff: Balances accuracy and processing speed; larger models would be more accurate but slower

**Google Text-to-Speech (gTTS)** - Audio generation
- Purpose: Convert translated text to speech
- Limitation: Requires internet connection; voice quality is basic
- Alternative: Could use more sophisticated TTS services (Azure, AWS Polly) for better voice quality

**Translate Library** - Text translation
- Purpose: Translate subtitles between languages
- Source detection: Auto-detects source language
- Fallback: Returns original text if translation fails

### Media Processing Libraries

**FFmpeg-Python** - Video/audio manipulation
- Purpose: Extract audio from video files
- Audio format: 16kHz mono PCM for optimal Whisper performance
- Usage: Wrapper around FFmpeg command-line tool

**MoviePy** - Video editing
- Purpose: Replace audio track in final video output
- Codec: H.264 video with AAC audio for broad compatibility
- Limitation: Can be memory-intensive for long videos

### File Format Handlers

**pysrt** - Subtitle file parsing
- Purpose: Read and write SRT subtitle files
- Encoding: UTF-8 for multilingual support
- Timing: Millisecond precision for accurate synchronization

**pydub** - Audio manipulation
- Purpose: Concatenate and time audio segments
- Format: Works with MP3 files from gTTS
- Dependency: Requires FFmpeg backend

### Web Framework

**Streamlit** - Application interface
- Purpose: Rapid development of interactive web UI
- Features: File upload, progress tracking, download buttons
- Styling: Custom CSS for enhanced visual design
- Limitation: Not optimized for high-traffic production deployments

### Python Standard Libraries

**tempfile** - Temporary file management
**pathlib** - Cross-platform path handling
**math** - Time format calculations
**os** - File system operations