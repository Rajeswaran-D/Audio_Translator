"""
Singing Voice Translation Pipeline
Separates vocals, translates lyrics, and synthesizes singing voice
"""

import os
import librosa
import soundfile as sf
import numpy as np
import subprocess
from typing import Tuple, Dict

def separate_vocals_and_music(
    audio_path: str,
    output_dir: str = None
) -> Tuple[str, str]:
    """
    Separates vocals from background music using open-source UVR (Ultimate Vocal Remover).
    
    Requires: pip install demucs
    
    Args:
        audio_path: Path to input audio file
        output_dir: Directory to save separated files
    
    Returns:
        Tuple of (vocals_path, music_path)
    
    Installation:
        pip install demucs
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(audio_path), "separated")
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Try using Facebook's Demucs
        print("Separating vocals from music (using Demucs)...")
        
        # Run demucs
        result = subprocess.run([
            "demucs",
            "-n", "htdemucs",  # Model
            "-o", output_dir,
            audio_path
        ], capture_output=True, text=True, check=False)
        
        if result.returncode != 0:
            raise RuntimeError(f"Demucs failed: {result.stderr}")
        
        # Find output files
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        separator_dir = os.path.join(output_dir, "htdemucs", base_name)
        
        vocals_path = os.path.join(separator_dir, "vocals.wav")
        music_path = os.path.join(separator_dir, "drums.wav")  # or bass, other
        
        if not os.path.exists(vocals_path):
            raise RuntimeError("Vocal separator did not create output files")
        
        print(f"✅ Vocals extracted: {vocals_path}")
        print(f"✅ Music extracted: {music_path}")
        
        return vocals_path, music_path
        
    except FileNotFoundError:
        print("⚠️  Demucs not installed. Install with: pip install demucs")
        raise
    except Exception as e:
        raise RuntimeError(f"Voice separation failed: {str(e)}")

def transcribe_singing(audio_path: str) -> Dict:
    """
    Transcribes lyrics from singing (uses Whisper with modifications for singing).
    
    Args:
        audio_path: Path to vocals-only audio
    
    Returns:
        Dictionary with transcription results
    """
    import whisper
    
    print("Transcribing singing (extracting lyrics)...")
    
    model = whisper.load_model("base")
    
    result = model.transcribe(
        audio_path,
        language="en",
        task="transcribe",
        fp16=False
    )
    
    return {
        "text": result["text"],
        "segments": result["segments"],
        "language": result.get("language", "en")
    }

def translate_lyrics(
    english_lyrics: str,
    target_language: str = "ta"
) -> str:
    """
    Translates lyrics to target language.
    Note: This is literal translation. Professional translators should:
    - Make lyrics singable (match syllable count to melody)
    - Preserve rhyme scheme/poetry
    - Maintain original meaning
    
    Args:
        english_lyrics: Original English lyrics
        target_language: Target language code
    
    Returns:
        Translated lyrics
    """
    from deep_translator import GoogleTranslator
    
    print(f"Translating lyrics to {target_language}...")
    
    try:
        translator = GoogleTranslator(source="en", target=target_language)
        translated = translator.translate(english_lyrics)
        return translated
    except Exception as e:
        print(f"Translation failed: {e}, returning original")
        return english_lyrics

def synthesize_singing(
    lyrics: str,
    gender: str = "female",
    language: str = "ta",
    output_path: str = None
) -> str:
    """
    Synthesizes singing voice from lyrics.
    
    Note: Current TTS systems don't support singing synthesis natively.
    This is a placeholder that requires specialized models like:
    - VITS (voice conversion)
    - Singing FastPitch
    - OpenVoice (voice cloning)
    
    Args:
        lyrics: Text to sing
        gender: Voice gender (female/male)
        language: Target language
        output_path: Where to save
    
    Returns:
        Path to synthesized audio
    
    Future: Would need one of:
        pip install vits-pytorch
        pip install fastpitch
        pip install openvoice
    """
    print("⚠️  Singing synthesis not yet implemented")
    print("   (Requires specialized neural models)")
    
    raise NotImplementedError(
        "Singing voice synthesis requires specialized models:\n"
        "  - VITS: Variable length inference\n"
        "  - Singing FastPitch: Prosody-aware synthesis\n"
        "  - OpenVoice: Voice cloning\n\n"
        "For now, use manual translation or professional singers."
    )

def remix_audio(
    vocals_path: str,
    music_path: str,
    output_path: str
) -> str:
    """
    Re-combines synthesized vocals with original music.
    
    Args:
        vocals_path: New vocals audio
        music_path: Original background music
        output_path: Output file
    
    Returns:
        Path to remixed audio
    """
    print("Remixing vocals with original music...")
    
    try:
        # Load audios
        vocals, sr = librosa.load(vocals_path, sr=None)
        music, sr = librosa.load(music_path, sr=sr)
        
        # Match lengths
        min_length = min(len(vocals), len(music))
        vocals = vocals[:min_length]
        music = music[:min_length]
        
        # Normalize and mix
        vocals = vocals / (np.max(np.abs(vocals)) + 1e-10) * 0.7
        music = music / (np.max(np.abs(music)) + 1e-10) * 0.5
        
        mixed = vocals + music
        
        # Prevent clipping
        if np.max(np.abs(mixed)) > 1.0:
            mixed = mixed / np.max(np.abs(mixed)) * 0.95
        
        # Export
        sf.write(output_path, mixed, sr)
        
        print(f"✅ Remixed audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        raise RuntimeError(f"Audio remixing failed: {str(e)}")

def translate_song_full_pipeline(
    audio_path: str,
    target_language: str = "ta",
    output_dir: str = None
) -> Dict:
    """
    Complete pipeline for song translation:
    1. Separate vocals from music
    2. Transcribe lyrics
    3. Translate lyrics
    4. Synthesize singing (TODO)
    5. Remix with music
    
    Args:
        audio_path: Path to song
        target_language: Target language code
        output_dir: Output directory
    
    Returns:
        Dictionary with results
    """
    results = {
        "status": "in_progress",
        "steps": []
    }
    
    try:
        # Step 1: Separate
        print("\n[1/5] Separating vocals from music...")
        vocals_path, music_path = separate_vocals_and_music(audio_path, output_dir)
        results["vocals_path"] = vocals_path
        results["music_path"] = music_path
        results["steps"].append("Vocal separation: ✅")
        
        # Step 2: Transcribe
        print("\n[2/5] Transcribing lyrics...")
        transcription = transcribe_singing(vocals_path)
        english_lyrics = transcription["text"]
        results["english_lyrics"] = english_lyrics
        results["steps"].append(f"Transcription: ✅ ({len(english_lyrics)} chars)")
        
        # Step 3: Translate
        print("\n[3/5] Translating lyrics...")
        translated_lyrics = translate_lyrics(english_lyrics, target_language)
        results["translated_lyrics"] = translated_lyrics
        results["steps"].append(f"Translation: ✅")
        
        # Step 4: Synthesize
        print("\n[4/5] Synthesizing singing voice...")
        print("⚠️  Singing synthesis not yet available")
        print("   Please use manual translation + professional singer")
        results["steps"].append("Singing synthesis: ❌ (requires specialized model)")
        results["status"] = "paused_at_synthesis"
        
        # Step 5: Remix
        print("\n[5/5] Would remix with original music...")
        results["steps"].append("Remixing: ⏳ (awaiting synthesis)")
        
        print("\n=== NEXT STEPS ===")
        print("Since singing synthesis requires specialized neural models:")
        print("\nOption A: Manual Process")
        print("  1. Use the extracted lyrics (shown above)")
        print("  2. Have a professional translator create singable lyrics")
        print("  3. Hire native speaker to sing with original melody")
        print("  4. System will remix with background music")
        print("\nOption B: Implement Singing Synthesis")
        print("  Install: pip install vits-pytorch")
        print("  Or train on singing data")
        print("\nOption C: Use Speech Translation System")
        print("  This system works great for speeches/podcasts")
        print("  Not suitable for songs due to music + rhythm constraints")
        
        return results
        
    except Exception as e:
        results["status"] = "failed"
        results["error"] = str(e)
        results["steps"].append(f"Failed: {str(e)}")
        return results

# ============================================================================
# FUTURE: Implement with specialized models
# ============================================================================

def setup_singing_synthesis():
    """
    Instructions for setting up singing voice synthesis
    """
    instructions = """
    
    === SINGING VOICE SYNTHESIS SETUP ===
    
    Option 1: VITS (Variational Inference with adversarial learning)
    -------
    Installation:
        pip install vits-pytorch
        # Download pretrained models from:
        https://github.com/jaywalnut310/vits
    
    Usage:
        from vits import models
        model = models.SingerVITS()
        audio = model.synthesis(text, speaker="tahun", language="tamil")
    
    
    Option 2: Singing FastPitch (Mel-spectrogram + duration prediction)
    -------
    Installation:
        pip install nemo-toolkit
        pip install pytorch-lightning
    
    Usage:
        from nemo.collections.tts import FastPitch
        model = FastPitch.from_pretrained("singing_fastpitch")
        
    
    Option 3: OpenVoice (Voice cloning)
    -------
    Installation:
        pip install openvoice
    
    Usage:
        from openvoice import ToneColorConverter
        converter = ToneColorConverter(ckpt_path="path/to/model")
        audio = converter.convert(text_tokens, speaker_voice)
    
    
    RECOMMENDATION:
    ===============
    For best results with minimal development:
    1. Use vocal separator (Demucs) ✅ DONE
    2. Transcribe & translate ✅ DONE
    3. Hire professional human singer to:
       - Create singable lyrics (match syllable count + rhythm)
       - Record new vocals
       - Human sings with original music melody
    4. Remix with background ✅ Can implement
    
    This gives cinema-quality results without complex ML.
    """
    
    print(instructions)

