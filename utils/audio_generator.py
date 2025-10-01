import pysrt
from gtts import gTTS
from pydub import AudioSegment
import os
import tempfile

def generate_dubbed_audio(subtitle_path, output_audio_path, language):
    """
    Generate dubbed audio from translated subtitles with proper timing
    
    Args:
        subtitle_path: Path to translated SRT subtitle file
        output_audio_path: Path where dubbed audio will be saved
        language: Language code for text-to-speech
    """
    try:
        # Load the subtitle file
        subs = pysrt.open(subtitle_path, encoding='utf-8')
        
        # Initialize an empty AudioSegment
        combined = AudioSegment.silent(duration=0)
        
        # Create a temporary directory for intermediate audio files
        temp_dir = tempfile.mkdtemp()
        
        # Iterate through each subtitle
        for index, sub in enumerate(subs):
            start_time = sub.start.ordinal / 1000.0  # convert to seconds
            end_time = sub.end.ordinal / 1000.0
            text = sub.text.strip()
            
            if not text:
                continue
            
            # Generate speech using gTTS
            temp_audio_path = os.path.join(temp_dir, f'temp_{index}.mp3')
            
            try:
                tts = gTTS(text, lang=language)
                tts.save(temp_audio_path)
                
                # Load the temporary mp3 file
                audio = AudioSegment.from_mp3(temp_audio_path)
                
                # Calculate the position to insert the audio
                current_duration = len(combined)
                silent_duration = start_time * 1000 - current_duration
                
                if silent_duration > 0:
                    # Add silence to fill the gap between the current audio and the next subtitle
                    combined += AudioSegment.silent(duration=silent_duration)
                
                # Calculate duration of subtitle segment
                segment_duration = (end_time - start_time) * 1000
                
                # Speed up or slow down audio to fit the subtitle duration if needed
                if len(audio) > segment_duration:
                    # Speed up audio to fit
                    speedup_factor = len(audio) / segment_duration
                    audio = audio.speedup(playback_speed=speedup_factor)
                elif len(audio) < segment_duration:
                    # Add slight pause after audio
                    audio = audio + AudioSegment.silent(duration=segment_duration - len(audio))
                
                # Append the audio to the combined AudioSegment
                combined += audio
                
                # Clean up temporary file
                if os.path.exists(temp_audio_path):
                    os.remove(temp_audio_path)
                    
            except Exception as e:
                # If TTS fails for this segment, add silence
                segment_duration = (end_time - start_time) * 1000
                combined += AudioSegment.silent(duration=segment_duration)
        
        # Export the combined audio as a WAV file
        combined.export(output_audio_path, format='wav')
        
        # Clean up temporary directory
        try:
            os.rmdir(temp_dir)
        except:
            pass
            
    except Exception as e:
        raise Exception(f"Error generating dubbed audio: {str(e)}")
