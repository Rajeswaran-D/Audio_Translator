import librosa
import numpy as np
from .config import MIN_SEGMENT_DURATION

def detect_segment_emotion(audio_segment, sr=16000):
    """
    Extracts emotion features and returns a simplified mapping.
    - Pitch (F0)
    - Energy (RMS)
    - Speech Rate
    
    Returns safe defaults for segments that are too short or silent.
    """
    # Safety check: Minimum segment duration
    min_samples = int(MIN_SEGMENT_DURATION * sr)
    if len(audio_segment) < min_samples:
        return {
            "gender": "male",
            "age": "adult",
            "emotion": "neutral",
            "pitch": 150,
            "energy": 0.02
        }
    
    try:
        # 1. Pitch Detection
        pitches, magnitudes = librosa.piptrack(y=audio_segment, sr=sr)
        pitch_values = pitches[pitches > 0]
        
        if len(pitch_values) > 0:
            pitch = float(np.mean(pitch_values))
        else:
            pitch = 150  # Default middle pitch for silent/unvoiced segments
        
        # Handle NaN or Inf
        if not np.isfinite(pitch):
            pitch = 150
        
        # 2. Energy Detection
        rms = librosa.feature.rms(y=audio_segment)[0]
        avg_energy = float(np.mean(rms)) if len(rms) > 0 else 0.02
        
        # 3. Simple Gender/Age Detection based on Pitch
        # - Male: ~85Hz to 180Hz
        # - Female: ~165Hz to 255Hz
        # - Child: >250Hz
        gender = "male"
        age = "adult"
        
        if pitch > 220:
            gender = "female"
            if pitch > 280:
                age = "child"
        elif pitch < 80:
            age = "elderly"
            
        # 4. Simple Emotion Classification
        # - Angry: High energy, higher pitch
        # - Sad: Low energy, lower pitch, slower
        # - Happy: Higher energy, variable pitch
        emotion = "neutral"
        
        if avg_energy > 0.05: # High energy
            if pitch > 200:
                emotion = "happy"
            else:
                emotion = "angry"
        elif avg_energy < 0.01: # Low energy
            emotion = "sad"
            
        return {
            "gender": gender,
            "age": age,
            "emotion": emotion,
            "pitch": pitch,
            "energy": avg_energy
        }
    except Exception as e:
        print(f"Emotion detection failed: {e}, returning defaults")
        return {
            "gender": "male",
            "age": "adult",
            "emotion": "neutral",
            "pitch": 150,
            "energy": 0.02
        }

def get_character_voice_profile(features, lang="en"):
    """
    Maps detected features to a character voice profile string.
    Format: {gender}_{age}_{emotion}
    
    Falls back to safe default if profile not found.
    """
    from .config import LANGUAGE_VOICE_MAPS, DEFAULT_VOICE_MAP
    
    profile = f"{features['gender']}_{features['age']}_{features['emotion']}"
    
    # Get language-specific voice map
    voice_map = LANGUAGE_VOICE_MAPS.get(lang, {})
    
    # Return profile if it exists, else fallback to neutral version
    if profile in voice_map:
        return profile
    else:
        # Fallback to neutral emotion
        fallback_profile = f"{features['gender']}_{features['age']}_neutral"
        if fallback_profile in voice_map:
            return fallback_profile
        else:
            # Ultimate fallback
            return "male_adult_neutral"
