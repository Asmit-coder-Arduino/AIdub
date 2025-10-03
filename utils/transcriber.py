from faster_whisper import WhisperModel
import os

def transcribe_audio(audio_path):
    """
    Transcribe audio file using faster-whisper model
    """
    try:
        # Use base model for faster loading on cloud
        model = WhisperModel("base", device="cpu", compute_type="int8")
        
        # Transcribe the audio
        segments, info = model.transcribe(audio_path, beam_size=3)
        
        # Get detected language
        detected_language = info.language
        
        # Convert generator to list
        segments_list = list(segments)
        
        return detected_language, segments_list
        
    except Exception as e:
        raise Exception(f"Error during transcription: {str(e)}")

def format_segment_info(segment):
    """
    Format segment information for display
    """
    return f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
