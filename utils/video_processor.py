import os
from moviepy.editor import VideoFileClip, AudioFileClip  # FIXED: movtepy → moviepy

def extract_audio(video_path, output_audio_path):
    """
    Extract audio from video file using moviepy
    """
    try:
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_audio_path, verbose=False, logger=None)
        audio.close()
        video.close()
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")

def replace_audio_track(video_path, audio_path, output_path):
    """
    Replace the audio track of a video with new audio
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
            verbose=False,
            logger=None,
            threads=1
        )
        
        # Clean up
        video.close()
        audio.close()
        video_with_new_audio.close()
        
    except Exception as e:
        raise Exception(f"Error replacing audio track: {str(e)}")
