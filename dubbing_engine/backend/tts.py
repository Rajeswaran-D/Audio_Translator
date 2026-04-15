import edge_tts
import asyncio
import os
from .config import LANGUAGE_VOICE_MAPS, VOICE_MAP, TAMIL_VOICE_MAP, DEFAULT_VOICE_MAP

async def generate_speech_async(text, voice_profile, output_path, lang="ta"):
    """
    Generates speech using Edge-TTS with character-based voice selection.
    Uses exponential backoff for reliability.
    """
    if not text or not text.strip():
        raise ValueError("Cannot generate speech for empty text")
    
    # 1. Select the best voice using language routing
    voice_map = LANGUAGE_VOICE_MAPS.get(lang, VOICE_MAP)
    
    # Try to find voice profile, fallback if not found
    voice = voice_map.get(voice_profile)
    if not voice:
        # Fallback to neutral variant
        neutral_profile = f"{voice_profile.split('_')[0]}_{voice_profile.split('_')[1]}_neutral"
        voice = voice_map.get(neutral_profile)
    if not voice:
        # Ultimate fallback to safe default
        voice = DEFAULT_VOICE_MAP.get("male_adult_neutral", "en-US-AndrewNeural")
    
    print(f"Selected voice: {voice} for profile: {voice_profile}")
    
    # 2. Adjust Rate and Pitch based on Emotion
    # - Happy: Slightly faster
    # - Angry: Faster, higher pitch
    # - Sad: Slower, lower pitch
    rate = "+0%"
    pitch = "+0Hz"
    
    if "happy" in voice_profile:
        rate = "+10%"
    elif "angry" in voice_profile:
        rate = "+15%"
        pitch = "+5Hz"
    elif "sad" in voice_profile:
        rate = "-15%"
        pitch = "-5Hz"
    
    # 3. Generate with Edge-TTS, with retry on transient failures
    max_retries = 3
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            await communicate.save(output_path)
            
            # Verify file was created
            if not os.path.exists(output_path):
                raise RuntimeError("TTS output file was not created")
            
            return output_path
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"TTS attempt {attempt + 1} failed: {e}, retrying...")
                await asyncio.sleep(2 ** attempt)
            else:
                raise

def generate_speech_sync(text, voice_profile, output_path, lang="ta"):
    """
    Synchronous wrapper for generate_speech_async.
    """
    asyncio.run(generate_speech_async(text, voice_profile, output_path, lang))
    return output_path
