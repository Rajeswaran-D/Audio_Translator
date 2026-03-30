import whisper
import os
import torch
from .config import SAMPLE_RATE

_model = None

def get_model(model_name="base"):
    """Load the whisper model lazily."""
    global _model
    if _model is None:
        # Check if GPU is available, else CPU
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model = whisper.load_model(model_name, device=device)
    return _model

def transcribe_full_audio(file_path):
    """
    Transcribes the entire audio file at once to preserve context.
    Returns a dictionary with full text and segments.
    """
    model = get_model()
    
    # Transcribe with timestamps
    options = {
        "fp16": False, # Use float32 on CPU
        "language": None, # Auto-detect
        "task": "transcribe",
    }
    
    result = model.transcribe(file_path, **options)
    
    # Process segments to ensure they aren't TOO small
    # but keep them clean for translation
    segments = []
    for s in result["segments"]:
        segments.append({
            "text": s["text"].strip(),
            "start": s["start"],
            "end": s["end"]
        })
        
    return {
        "text": result["text"].strip(),
        "segments": segments,
        "language": result.get("language", "en")
    }

def merge_short_segments(segments, min_duration=1.5):
    """
    Merge segments that are too short to improve translation context.
    """
    merged = []
    if not segments:
        return merged
        
    current = segments[0]
    for next_seg in segments[1:]:
        duration = current["end"] - current["start"]
        if duration < min_duration:
            current["text"] += " " + next_seg["text"]
            current["end"] = next_seg["end"]
        else:
            merged.append(current)
            current = next_seg
    merged.append(current)
    return merged
