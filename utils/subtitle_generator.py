import math

def format_time(seconds):
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm)
    
    Args:
        seconds: Time in seconds (float)
        
    Returns:
        str: Formatted timestamp string
    """
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    return formatted_time

def generate_subtitle_file(segments, output_path):
    """
    Generate SRT subtitle file from transcription segments
    
    Args:
        segments: List of transcription segments from faster-whisper
        output_path: Path where SRT file will be saved
    """
    try:
        text = ""
        for index, segment in enumerate(segments):
            segment_start = format_time(segment.start)
            segment_end = format_time(segment.end)
            text += f"{str(index + 1)}\n"
            text += f"{segment_start} --> {segment_end}\n"
            text += f"{segment.text.strip()}\n"
            text += "\n"
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
            
    except Exception as e:
        raise Exception(f"Error generating subtitle file: {str(e)}")
