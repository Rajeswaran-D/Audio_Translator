import os
import numpy as np
import librosa
import librosa.effects
import soundfile as sf
from pydub import AudioSegment
import noisereduce as nr
from .config import MAX_FILE_SIZE_BYTES, SAMPLE_RATE

try:
    import pyrubberband as pyrb
    PYRUBBERBAND_AVAILABLE = True
except ImportError:
    PYRUBBERBAND_AVAILABLE = False

# Supported audio formats
SUPPORTED_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', '.wma'}

def stretch_audio_to_duration(audio_path, target_duration_seconds, sr=SAMPLE_RATE):
    """
    Time-stretches audio to match target duration without changing pitch.
    Uses Rubber Band for high-quality stretching, falls back to librosa if unavailable.
    
    Args:
        audio_path: Path to audio file
        target_duration_seconds: Desired duration in seconds
        sr: Sample rate
    
    Returns:
        Stretched audio array
    """
    try:
        # Load the audio
        audio, loaded_sr = librosa.load(audio_path, sr=sr)
        
        # Calculate stretch factor
        current_duration = len(audio) / sr
        if current_duration <= 0:
            return audio
        
        stretch_factor = target_duration_seconds / current_duration
        
        # Avoid extreme stretching (limit to 0.5x - 2.0x)
        stretch_factor = max(0.5, min(2.0, stretch_factor))
        
        if abs(stretch_factor - 1.0) < 0.05:  # Close enough to 1.0
            return audio
        
        # Use Rubber Band for high-quality stretching if available
        if PYRUBBERBAND_AVAILABLE:
            try:
                # Rubber Band's time_stretch preserves pitch while changing tempo
                # t_stretch is the time stretch ratio (1.0 = no change)
                stretched_audio = pyrb.time_stretch(audio, sr, stretch_factor)
                print(f"[RubberBand] Stretched audio from {current_duration:.2f}s to {target_duration_seconds:.2f}s (factor: {stretch_factor:.2f})")
                return stretched_audio
            except Exception as e:
                print(f"RubberBand stretching failed: {e}, falling back to librosa phase vocoder")
        
        # Fallback: Use librosa's phase vocoder with improved parameters
        # Higher n_fft and hop_length for better quality on lower frequencies
        n_fft = 2048
        hop_length = 512
        stretched_audio = librosa.effects.time_stretch(audio, rate=stretch_factor)
        
        print(f"[Librosa] Stretched audio from {current_duration:.2f}s to {target_duration_seconds:.2f}s (factor: {stretch_factor:.2f})")
        return stretched_audio
        
    except Exception as e:
        print(f"Time-stretch failed: {e}, returning original")
        return librosa.load(audio_path, sr=sr)[0]

def validate_audio_file(file_path, file_size):
    """
    Validates audio file before processing.
    Returns (is_valid, error_message, is_speech_or_song)
    """
    # Check file size
    if file_size > MAX_FILE_SIZE_BYTES:
        return False, f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum ({MAX_FILE_SIZE_BYTES / 1024 / 1024:.0f}MB)", None
    
    # Check file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in SUPPORTED_FORMATS:
        return False, f"Unsupported format: {file_ext}. Supported: {', '.join(SUPPORTED_FORMATS)}", None
    
    # Check file exists and is readable
    if not os.path.exists(file_path):
        return False, "File not found", None
    
    if not os.access(file_path, os.R_OK):
        return False, "File is not readable", None
    
    # Try to read file metadata
    try:
        duration = librosa.get_duration(path=file_path)
        if duration < 0.5:
            return False, "Audio file is too short (minimum 0.5 seconds)", None
        
        # Detect if it's likely a song (high energy + longer duration)
        audio, sr = librosa.load(file_path, sr=SAMPLE_RATE)
        energy = librosa.feature.rms(y=audio)[0].mean()
        is_likely_song = energy > 0.25 and duration > 15
        
        audio_type = "song" if is_likely_song else "speech"
        return True, None, audio_type
        
    except Exception as e:
        return False, f"Invalid audio file: {str(e)}", None

def load_audio(file_path, sr=SAMPLE_RATE):
    """Load audio file to numpy array with error handling."""
    try:
        audio, _ = librosa.load(file_path, sr=sr)
        return audio
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {str(e)}")

def save_audio(audio, file_path, sr=SAMPLE_RATE):
    """Save numpy array to audio file with error handling."""
    try:
        sf.write(file_path, audio, sr)
        return file_path
    except Exception as e:
        raise RuntimeError(f"Failed to save audio: {str(e)}")

def reduce_noise(audio, sr=SAMPLE_RATE):
    """Apply noise reduction to audio with error handling."""
    try:
        # Stationary noise reduction
        reduced_noise = nr.reduce_noise(y=audio, sr=sr, prop_decrease=0.8)
        return reduced_noise
    except Exception as e:
        print(f"Noise reduction failed: {e}")
        return audio

def normalize_audio(file_path):
    """Normalize audio levels using pydub with error handling."""
    try:
        audio = AudioSegment.from_file(file_path)
        normalized = audio.normalize()
        file_ext = os.path.splitext(file_path)[1][1:] or "mp3"
        normalized.export(file_path, format=file_ext)
        return file_path
    except Exception as e:
        print(f"Audio normalization failed: {e}")
        return file_path

def split_segment(audio, start_ms, end_ms, sr=SAMPLE_RATE):
    """Extract a segment from the audio array."""
    start_sample = int((start_ms / 1000) * sr)
    end_sample = int((end_ms / 1000) * sr)
    return audio[start_sample:end_sample]

def get_audio_duration(file_path):
    """Return duration of audio in seconds with error handling."""
    try:
        return librosa.get_duration(path=file_path)
    except Exception as e:
        raise RuntimeError(f"Failed to get audio duration: {str(e)}")
