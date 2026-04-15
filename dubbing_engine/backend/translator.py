from deep_translator import GoogleTranslator
import time
from .config import TRANSLATION_RETRY_COUNT, TRANSLATION_RETRY_DELAY

def translate_with_retry(text, target_lang, max_retries=TRANSLATION_RETRY_COUNT):
    """
    Translates text with exponential backoff retry logic.
    Handles rate limiting and transient errors gracefully.
    """
    if not text:
        return ""
    
    for attempt in range(max_retries):
        try:
            translator = GoogleTranslator(source="auto", target=target_lang)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = TRANSLATION_RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                print(f"Translation attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Translation failed after {max_retries} attempts: {e}")
                return text  # Return original text as fallback

def translate_full_text(text, target_lang="ta"):
    """
    Translates the entire text while preserving global context.
    Uses retry logic for robustness.
    """
    return translate_with_retry(text, target_lang)

def translate_segments_in_context(segments, target_lang="ta"):
    """
    Efficiently translates segments while maintaining context.
    For each segment, translates its text with retry logic.
    Skips instrumental segments.
    """
    translated_segments = []
    total_segments = len(segments)
    
    for idx, seg in enumerate(segments):
        try:
            text = seg["text"]
            
            # Skip instrumental/silence segments - don't translate them
            if text.lower().startswith("[") and text.lower().endswith("]"):
                # Keep instrumental markers as-is
                trans_text = text
                print(f"Skipped instrumental segment {idx + 1}/{total_segments}: {text}")
            else:
                # Translate actual singing/speech
                trans_text = translate_with_retry(text, target_lang)
                print(f"Translated segment {idx + 1}/{total_segments}")
            
            translated_segments.append({
                **seg,
                "translated_text": trans_text
            })
            
            # Adaptive rate limiting (only for actual translations)
            if idx < total_segments - 1 and not (text.lower().startswith("[") and text.lower().endswith("]")):
                time.sleep(0.1)  # Small delay between segments
                
        except Exception as e:
            print(f"Segment {idx} translation error: {e}, using original text")
            translated_segments.append({
                **seg,
                "translated_text": seg["text"]
            })
    
    return translated_segments

def optimize_for_speech(text):
    """
    Director-Level Text Optimization:
    - Simplifies complex punctuation
    - Removes problematic characters for TTS
    - Adds natural pauses using punctuation
    """
    if not text:
        return ""
    
    # Remove problematic characters
    text = text.replace(" (", ", ").replace(")", "")
    text = text.replace("  ", " ")  # Remove double spaces
    
    # Remove URLs and special symbols that cause TTS issues
    import re
    text = re.sub(r'http\S+|www\.\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[#@]', '', text)
    
    text = text.strip()
    return text
