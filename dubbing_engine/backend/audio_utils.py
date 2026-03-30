import os
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment
import noisereduce as nr

def load_audio(file_path, sr=16000):
    """Load audio file to numpy array."""
    audio, _ = librosa.load(file_path, sr=sr)
    return audio

def save_audio(audio, file_path, sr=16000):
    """Save numpy array to audio file."""
    sf.write(file_path, audio, sr)
    return file_path

def reduce_noise(audio, sr=16000):
    """Apply noise reduction to audio."""
    try:
        # Stationary noise reduction
        reduced_noise = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.8)
        return reduced_noise
    except Exception as e:
        print(f"Noise reduction failed: {e}")
        return audio

def normalize_audio(file_path):
    """Normalize audio levels using pydub."""
    audio = AudioSegment.from_file(file_path)
    normalized = audio.normalize()
    normalized.export(file_path, format=os.path.splitext(file_path)[1][1:])
    return file_path

def split_segment(audio, start_ms, end_ms, sr=16000):
    """Extract a segment from the audio array."""
    start_sample = int((start_ms / 1000) * sr)
    end_sample = int((end_ms / 1000) * sr)
    return audio[start_sample:end_sample]

def get_audio_duration(file_path):
    """Return duration of audio in seconds."""
    return librosa.get_duration(path=file_path)
