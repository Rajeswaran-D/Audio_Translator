from deep_translator import GoogleTranslator
import time

def translate_full_text(text, target_lang="ta"):
    """
    Translates the entire text while preserving global context.
    """
    if not text: return ""
    
    try:
        # Use Google Translate via deep-translator
        translator = GoogleTranslator(source="auto", target=target_lang)
        translated = translator.translate(text)
        return translated
    except Exception as e:
        print(f"Translation failed: {e}")
        return text

def translate_segments_in_context(segments, target_lang="ta"):
    """
    Efficiently translates segments while maintaining context.
    For each segment, translates its text.
    """
    translator = GoogleTranslator(source="auto", target=target_lang)
    
    translated_segments = []
    for seg in segments:
        try:
            # We translate them one-by-one for now to keep mapping simple,
            # but using the same translator instance for better performance.
            trans_text = translator.translate(seg["text"])
            translated_segments.append({
                **seg,
                "translated_text": trans_text
            })
            # Small delay to avoid rate limiting
            time.sleep(0.05)
        except Exception as e:
            print(f"Segment translation failed: {e}")
            translated_segments.append({
                **seg,
                "translated_text": seg["text"]
            })
    return translated_segments

def optimize_for_speech(text):
    """
    Director-Level Text Optimization:
    - Simplifies complex words.
    - Adds natural pauses using punctuation.
    - Sanitizes phonetic output.
    """
    # Simple rule-based optimizations for now
    # We can expand this with LLM later if needed
    text = text.replace(" (", ", ").replace(")", "")
    text = text.strip()
    return text
