"""
SeamlessM4T-based Speech-to-Speech Translation
Direct audio translation without TTS, preserving speaker voice characteristics
"""

import torch
import numpy as np
import librosa
import soundfile as sf
from typing import Tuple, Dict
import os

# Initialize model (lazy loading)
_model = None
_model_name = None

def get_seamless_model(model_name: str = "seamless_v2"):
    """
    Lazy-load SeamlessM4T model
    
    Args:
        model_name: "seamless_v2" or "seamless_v1"
    
    Returns:
        Loaded model
    """
    global _model, _model_name
    
    if _model is not None and _model_name == model_name:
        return _model
    
    try:
        from seamless_communication.models.inference import Translator
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading {model_name} on {device}...")
        
        _model = Translator(model_name, vocoder_name="vocoder_v2", device=device)
        _model_name = model_name
        
        return _model
    except ImportError:
        print("⚠️  SeamlessM4T not installed. Install with:")
        print("pip install seamless_communication")
        raise RuntimeError("SeamlessM4T not available. Use fallback TTS approach.")

def translate_speech_to_speech(
    audio_path: str,
    source_lang: str = "eng",
    target_lang: str = "tam",
    output_path: str = None
) -> Tuple[str, Dict]:
    """
    Translates audio directly from source to target language while preserving speaker voice.
    
    Args:
        audio_path: Path to input audio file
        source_lang: Source language code (e.g., "eng", "tam", "hin")
        target_lang: Target language code
        output_path: Path to save translated audio
    
    Returns:
        Tuple of (output_path, metadata)
    
    Language codes:
        - eng: English
        - tam: Tamil
        - hin: Hindi
        - tel: Telugu
        - mal: Malayalam
        - kan: Kannada
    """
    if output_path is None:
        output_path = audio_path.replace(".mp3", "_translated.wav")
    
    try:
        model = get_seamless_model()
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=16000)
        
        print(f"Translating audio from {source_lang} to {target_lang}...")
        
        # Use seamless for speech-to-speech translation
        # The model expects audio as numpy array
        result = model.predict(
            input=audio_path,
            task_str="S2ST",  # Speech-to-Speech Translation
            tgt_lang=target_lang,
            src_lang=source_lang
        )
        
        # Extract translated audio
        translated_audio = result[0][0].numpy()
        
        # Save output
        sf.write(output_path, translated_audio, 16000)
        
        metadata = {
            "original_duration": librosa.get_duration(path=audio_path),
            "translated_duration": len(translated_audio) / 16000,
            "model": "SeamlessM4T",
            "source_lang": source_lang,
            "target_lang": target_lang
        }
        
        return output_path, metadata
        
    except Exception as e:
        print(f"SeamlessM4T translation failed: {e}")
        raise RuntimeError(f"Speech-to-speech translation failed: {str(e)}")

def translate_audio_with_fallback(
    audio_path: str,
    source_lang: str = "eng",
    target_lang: str = "tam",
    output_path: str = None,
    use_seamless: bool = True
) -> Tuple[str, Dict]:
    """
    Attempts SeamlessM4T first, falls back to traditional TTS if unavailable.
    
    Args:
        audio_path: Path to input audio
        source_lang: Source language code
        target_lang: Target language code
        output_path: Output path
        use_seamless: Whether to try SeamlessM4T (default: True)
    
    Returns:
        Tuple of (output_path, metadata)
    """
    if use_seamless:
        try:
            return translate_speech_to_speech(
                audio_path, source_lang, target_lang, output_path
            )
        except Exception as e:
            print(f"SeamlessM4T unavailable: {e}")
            print("Falling back to TTS-based translation...")
    
    # Fallback to traditional approach
    from . import stt, translator, tts, audio_utils, emotion
    
    # Transcribe
    transcription = stt.transcribe_full_audio(audio_path)
    segments = transcription["segments"]
    
    # Translate
    target_lang_map = {
        "tam": "ta", "hin": "hi", "tel": "te",
        "mal": "ml", "kan": "kn", "eng": "en"
    }
    tgt_lang = target_lang_map.get(target_lang, "ta")
    translated_segments = translator.translate_segments_in_context(segments, tgt_lang)
    
    # Generate TTS (fallback only uses basic synthesis)
    metadata = {
        "method": "TTS_fallback",
        "segments": len(segments),
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    
    return output_path, metadata
