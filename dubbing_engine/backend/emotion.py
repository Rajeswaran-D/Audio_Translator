import librosa
import numpy as np

def detect_segment_emotion(audio_segment, sr=16000):
    """
    Extracts emotion features and returns a simplified mapping.
    - Pitch (F0)
    - Energy (RMS)
    - Speech Rate
    """
    # 1. Pitch Detection
    pitches, magnitudes = librosa.piptrack(y=audio_segment, sr=sr)
    pitch = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 150 # Default middle pitch
    
    # 2. Energy Detection
    rms = librosa.feature.rms(y=audio_segment)[0]
    avg_energy = np.mean(rms)
    
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

def get_character_voice_profile(features):
    """
    Maps detected features to a character voice profile string.
    Format: {gender}_{age}_{emotion}
    """
    profile = f"{features['gender']}_{features['age']}_{features['emotion']}"
    return profile
