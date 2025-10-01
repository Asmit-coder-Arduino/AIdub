import ffmpeg
import os
from moviepy.editor import VideoFileClip, AudioFileClip

def extract_audio(video_path, output_audio_path):
    """
    Extract audio from video file using ffmpeg
    
    Args:
        video_path: Path to input video file
        output_audio_path: Path where extracted audio will be saved
    """
    try:
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(stream, output_audio_path, acodec='pcm_s16le', ac=1, ar='16k')
        ffmpeg.run(stream, overwrite_output=True, quiet=True)
    except ffmpeg.Error as e:
        raise Exception(f"Error extracting audio: {e.stderr.decode() if e.stderr else str(e)}")

def replace_audio_track(video_path, audio_path, output_path):
    """
    Replace the audio track of a video with new audio
    
    Args:
        video_path: Path to original video file
        audio_path: Path to new audio file
        output_path: Path where output video will be saved
    """
    try:
        # Load the video file
        video = VideoFileClip(video_path)
        
        # Load the new audio file
        audio = AudioFileClip(audio_path)
        
        # Set the new audio to the video
        video_with_new_audio = video.set_audio(audio)
        
        # Save the new video file
        video_with_new_audio.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            logger=None  # Suppress moviepy output
        )
        
        # Clean up
        video.close()
        audio.close()
        video_with_new_audio.close()
        
    except Exception as e:
        raise Exception(f"Error replacing audio track: {str(e)}")
