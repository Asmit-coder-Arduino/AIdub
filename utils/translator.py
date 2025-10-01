import pysrt
from translate import Translator

def translate_text(text, to_lang, from_lang="auto"):
    """
    Translate text from one language to another
    
    Args:
        text: Text to translate
        to_lang: Target language code
        from_lang: Source language code (default: auto-detect)
        
    Returns:
        str: Translated text
    """
    try:
        translator = Translator(to_lang=to_lang, from_lang=from_lang)
        translated_text = translator.translate(text)
        return translated_text
    except Exception as e:
        # If translation fails, return original text
        return text

def translate_subtitles(input_srt_path, output_srt_path, target_lang, source_lang="auto"):
    """
    Translate an SRT subtitle file to target language
    
    Args:
        input_srt_path: Path to input SRT file
        output_srt_path: Path where translated SRT file will be saved
        target_lang: Target language code
        source_lang: Source language code (default: auto-detect)
    """
    try:
        # Load the subtitle file
        subs = pysrt.open(input_srt_path, encoding='utf-8')
        
        # Translate each subtitle
        for sub in subs:
            original_text = sub.text
            translated_text = translate_text(original_text, target_lang, source_lang)
            sub.text = translated_text
        
        # Save the translated subtitles
        subs.save(output_srt_path, encoding='utf-8')
        
    except Exception as e:
        raise Exception(f"Error translating subtitles: {str(e)}")
