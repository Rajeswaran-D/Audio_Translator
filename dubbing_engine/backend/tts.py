import edge_tts
import asyncio
import os
from .config import TAMIL_VOICE_MAP, VOICE_MAP

async def generate_speech_async(text, voice_profile, output_path, lang="ta"):
    """
    Generates speech using Edge-TTS with character-based voice selection.
    """
    # 1. Select the best voice
    # Default to a safe voice if the profile isn't matched
    voice = TAMIL_VOICE_MAP.get("male_adult_neutral", "ta-IN-ValluvarNeural")
    
    if lang == "ta":
        voice = TAMIL_VOICE_MAP.get(voice_profile, TAMIL_VOICE_MAP["male_adult_neutral"])
    else:
        # Falls back to English profiles if lang is unsupported or English
        voice = VOICE_MAP.get(voice_profile, VOICE_MAP["male_adult_neutral"])
        
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
        
    # 3. Commmunicate with Edge-TTS
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await communicate.save(output_path)
    
    return output_path

def generate_speech_sync(text, voice_profile, output_path, lang="ta"):
    """
    Synchronous wrapper for generate_speech_async.
    """
    asyncio.run(generate_speech_async(text, voice_profile, output_path, lang))
    return output_path
