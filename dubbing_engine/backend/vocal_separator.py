"""
Vocal isolation using Demucs
Separates vocals from background music for song translation
"""

import os
import librosa
import soundfile as sf
import numpy as np
import subprocess
from typing import Tuple, Dict

def separate_vocals_demucs(
    audio_path: str,
    output_dir: str = None
) -> Tuple[str, str]:
    """
    Separates vocals from background music using Demucs.
    
    Args:
        audio_path: Path to input audio file
        output_dir: Directory to save separated files
    
    Returns:
        Tuple of (vocals_path, music_path)
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(audio_path), "separated")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("🎵 Separating vocals from music using Demucs...")
        
        # Run demucs command with MP3 output format (more compatible)
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        cmd = [
            "demucs",
            "-n", "htdemucs",  # Model: Hybrid Transformers
            "-o", output_dir,
            "--two-stems=vocals",  # Split into vocals and other
            "--mp3-bitrate", "192",  # Use MP3 output instead of WAV
            audio_path
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"Demucs stdout: {result.stdout}")
        if result.stderr:
            print(f"Demucs stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise RuntimeError(f"Demucs failed with code {result.returncode}: {result.stderr}")
        
        # Find output files - try both WAV and MP3 formats
        separator_dir = os.path.join(output_dir, "htdemucs", base_name)
        
        # Check for vocals file
        vocals_path = os.path.join(separator_dir, "vocals.wav")
        if not os.path.exists(vocals_path):
            vocals_path = os.path.join(separator_dir, "vocals.mp3")
        
        # Check for instrumental/music file - Demucs creates "no_vocals.wav" or "other.wav"
        music_path = os.path.join(separator_dir, "no_vocals.wav")
        if not os.path.exists(music_path):
            music_path = os.path.join(separator_dir, "other.wav")
        if not os.path.exists(music_path):
            music_path = os.path.join(separator_dir, "no_vocals.mp3")
        if not os.path.exists(music_path):
            music_path = os.path.join(separator_dir, "other.mp3")
        
        # List directory contents for debugging
        try:
            if os.path.exists(separator_dir):
                contents = os.listdir(separator_dir)
                print(f"Directory contents: {contents}")
            else:
                print(f"Separator directory not found: {separator_dir}")
                # Try to find where demucs actually created files
                if os.path.exists(output_dir):
                    all_contents = os.walk(output_dir)
                    for root, dirs, files in all_contents:
                        print(f"Found dir: {root} with files: {files}")
        except Exception as e:
            print(f"Could not list directory: {e}")
        
        if not os.path.exists(vocals_path) or not os.path.exists(music_path):
            raise RuntimeError(
                f"Demucs output files not found.\n"
                f"Expected: {separator_dir}/(vocals|no_vocals|other).* and (no_vocals|other).*\n"
                f"Vocals exists: {os.path.exists(vocals_path)} at {vocals_path}\n"
                f"Music exists: {os.path.exists(music_path)} at {music_path}"
            )
        
        print(f"✅ Vocals extracted: {vocals_path}")
        print(f"✅ Instrumental extracted: {music_path}")
        
        return vocals_path, music_path
        
    except FileNotFoundError:
        raise RuntimeError(
            "❌ Demucs not found. Install with:\n"
            "  pip install demucs\n\n"
            "Or if installation fails, try:\n"
            "  pip install -U demucs torch torchaudio"
        )
    except Exception as e:
        raise RuntimeError(f"Vocal separation failed: {str(e)}")

def load_and_process_vocals(vocals_path: str, sr: int = 16000) -> np.ndarray:
    """
    Load and normalize vocals for transcription/translation.
    
    Args:
        vocals_path: Path to vocals audio
        sr: Sample rate
    
    Returns:
        Audio array normalized to optimal level for TTS
    """
    audio, _ = librosa.load(vocals_path, sr=sr)
    
    # Normalize to reasonable level (avoid too quiet or too loud)
    current_rms = np.sqrt(np.mean(audio ** 2))
    if current_rms > 0:
        target_rms = 0.2  # Optimal for TTS
        audio = audio * (target_rms / current_rms)
    
    # Ensure no clipping
    if np.max(np.abs(audio)) > 1.0:
        audio = audio / np.max(np.abs(audio)) * 0.99
    
    return audio

def remix_audio(
    vocals_path: str,
    music_path: str,
    output_path: str,
    vocal_level: float = 0.7,
    music_level: float = 0.5
) -> str:
    """
    Remixes translated vocals with original instrumental.
    
    Args:
        vocals_path: Path to new vocals
        music_path: Path to original instrumental
        output_path: Output file path
        vocal_level: Volume level for vocals (0-1)
        music_level: Volume level for music (0-1)
    
    Returns:
        Path to remixed audio
    """
    print("🎼 Remixing vocals with original music...")
    
    try:
        # Load audios at same sample rate
        vocals, sr_v = librosa.load(vocals_path, sr=None)
        music, sr_m = librosa.load(music_path, sr=sr_v)
        
        # Match lengths
        min_length = min(len(vocals), len(music))
        vocals = vocals[:min_length]
        music = music[:min_length]
        
        # Normalize and apply volume levels
        vocals = vocals / (np.max(np.abs(vocals)) + 1e-10) * vocal_level
        music = music / (np.max(np.abs(music)) + 1e-10) * music_level
        
        # Mix
        mixed = vocals + music
        
        # Prevent clipping
        peak = np.max(np.abs(mixed))
        if peak > 1.0:
            mixed = mixed / peak * 0.98
        
        # Save
        # Convert to mp3 if needed
        if output_path.endswith(".mp3"):
            # Save as wav first, then convert
            temp_wav = output_path.replace(".mp3", "_temp.wav")
            sf.write(temp_wav, mixed, sr_v)
            
            # Convert to mp3 using ffmpeg
            cmd = ["ffmpeg", "-i", temp_wav, "-q:a", "9", "-y", output_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
            
            if result.returncode != 0:
                print(f"Warning: ffmpeg conversion had issues: {result.stderr}")
        else:
            sf.write(output_path, mixed, sr_v)
        
        print(f"✅ Remixed audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Remixing failed: {str(e)}")

def check_demucs_installed() -> bool:
    """Check if Demucs is installed and working."""
    try:
        result = subprocess.run(
            ["demucs", "--help"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def install_demucs_instructions() -> str:
    """Get installation instructions for Demucs."""
    return """
    To enable SONG translation, install Demucs:
    
    1. Basic installation:
       pip install demucs
    
    2. If that fails, install dependencies first:
       pip install -U torch torchaudio
       pip install demucs
    
    3. Verify installation:
       demucs --help
    
    Then restart the server.
    """
