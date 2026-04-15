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

def transcribe_full_audio(file_path, target_segment_duration=5.0):
    """
    Transcribes the entire audio file while creating natural segments.
    For songs, uses the larger model for better accuracy.
    Returns: dictionary with full text, segments, and language
    
    Args:
        file_path: Path to audio file
        target_segment_duration: Desired duration for each segment (in seconds)
    """
    model_name = "small"  # Use small model for faster processing, can upgrade to "medium" for songs
    model = get_model(model_name)
    
    # Transcribe with timestamps and settings optimized for singing
    options = {
        "fp16": False,  # Use float32 on CPU
        "language": None,  # Auto-detect
        "task": "transcribe",
        "best_of": 5,  # Better quality for singing
        "beam_size": 5,  # Better beam search for accuracy
        "patience": 1.0,  # Better accuracy
    }
    
    result = model.transcribe(file_path, **options)
    
    # Get total audio duration
    import librosa
    total_duration = librosa.get_duration(path=file_path)
    
    # Process segments - ensure we cover the entire song
    segments = []
    for s in result["segments"]:
        segment_duration = s["end"] - s["start"]
        
        # Skip very small segments that might be artifacts
        if segment_duration < 0.3:
            continue
        
        # If segment is too long, try to split it at sentence boundaries
        if segment_duration > target_segment_duration * 1.5:
            sub_segments = _split_long_segment(s, target_segment_duration)
            segments.extend(sub_segments)
        else:
            segments.append({
                "text": s["text"].strip(),
                "start": s["start"],
                "end": s["end"]
            })
    
    # Merge very short segments and fill gaps
    segments = merge_short_segments(segments, min_duration=0.5)
    segments = fill_gaps_in_segments(segments, total_duration)
    
    print(f"Created {len(segments)} segments from audio (total duration: {total_duration:.1f}s)")
    
    return {
        "text": result["text"].strip(),
        "segments": segments,
        "language": result.get("language", "en")
    }

def _split_long_segment(segment, target_duration=5.0):
    """
    Splits a long segment into smaller chunks at sentence boundaries.
    """
    text = segment["text"]
    start = segment["start"]
    end = segment["end"]
    total_duration = end - start
    
    # Split by sentence-like boundaries (., !, ?)
    import re
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    if len(sentences) <= 1:
        # No clear sentence breaks, split evenly
        return [{
            "text": text,
            "start": start,
            "end": end
        }]
    
    # Distribute sentences across time
    sub_segments = []
    chars_per_second = len(text) / total_duration if total_duration > 0 else 1
    
    current_text = ""
    current_start = start
    
    for sentence in sentences:
        if current_text:
            current_text += " "
        current_text += sentence
        
        # Estimate duration based on character count
        estimated_duration = len(current_text) / chars_per_second
        
        # If we exceed target duration or it's the last sentence, create segment
        if estimated_duration > target_duration or sentence == sentences[-1]:
            current_end = start + estimated_duration
            if current_end > end:
                current_end = end
            
            if current_text.strip():
                sub_segments.append({
                    "text": current_text.strip(),
                    "start": current_start,
                    "end": current_end
                })
            
            current_text = ""
            current_start = current_end
    
    return sub_segments if sub_segments else [{
        "text": text,
        "start": start,
        "end": end
    }]

def merge_short_segments(segments, min_duration=0.5):
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

def fill_gaps_in_segments(segments, total_duration):
    """
    Fill gaps in transcribed segments to ensure entire song is covered.
    Inserts placeholder segments for instrumental/silence sections.
    
    Args:
        segments: List of transcribed segments
        total_duration: Total duration of the audio in seconds
    
    Returns:
        List of segments with gaps filled
    """
    if not segments:
        return [{
            "text": "[Instrumental]",
            "start": 0,
            "end": total_duration
        }]
    
    filled = []
    
    # Add segment for content before first segment
    if segments[0]["start"] > 0.1:
        filled.append({
            "text": "[Instrumental Intro]",
            "start": 0,
            "end": segments[0]["start"]
        })
    
    # Add original segments and fill gaps between them
    for i, segment in enumerate(segments):
        filled.append(segment)
        
        # Check for gap to next segment
        if i < len(segments) - 1:
            gap_start = segment["end"]
            gap_end = segments[i + 1]["start"]
            gap_duration = gap_end - gap_start
            
            # Fill gaps larger than 0.5 seconds
            if gap_duration > 0.5:
                filled.append({
                    "text": "[Instrumental Break]",
                    "start": gap_start,
                    "end": gap_end
                })
    
    # Add segment for content after last segment
    last_segment_end = segments[-1]["end"]
    if total_duration - last_segment_end > 0.1:
        filled.append({
            "text": "[Instrumental Outro]",
            "start": last_segment_end,
            "end": total_duration
        })
    
    return filled
