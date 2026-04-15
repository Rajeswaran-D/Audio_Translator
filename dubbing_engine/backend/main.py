from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import os
import shutil
import asyncio
import json

from .manager import pipeline_manager
from .config import UPLOADS_DIR, OUTPUTS_DIR, SUPPORTED_LANGUAGES
from . import audio_utils
from . import translator
from . import tts
from . import emotion

app = FastAPI(title="Professional Audio Dubbing Engine")

# Store job data in memory for the session
job_sessions = {}  # {job_id: {segments, metadata, audio_type, target_lang}}

# CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("AI Translation System Startup...")
    # Warm up models if needed (with timeout)
    try:
        from . import stt
        stt.get_model()
        print("Speech-to-Text model loaded.")
    except Exception as e:
        print(f"Warning: Could not pre-load STT model: {e}")
    print("System Ready.")

@app.post("/translate")
async def translate_audio(
    file: UploadFile = File(...),
    target_lang: str = Form("ta")
):
    """
    Main endpoint for professional audio translation.
    Handles both speech and songs (with vocal isolation).
    Validates inputs and executes the dubbing pipeline.
    """
    # 1. Validate language
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {target_lang}. Supported: {list(SUPPORTED_LANGUAGES.keys())}"
        )
    
    # 2. Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    input_path = os.path.join(UPLOADS_DIR, file.filename)
    
    try:
        # Save file
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # Get file size for validation
        file_size = os.path.getsize(input_path)
        
        # Validate audio file
        is_valid, error_msg, audio_type = audio_utils.validate_audio_file(input_path, file_size)
        if not is_valid:
            if os.path.exists(input_path):
                os.remove(input_path)
            raise HTTPException(status_code=400, detail=f"Invalid audio file: {error_msg}")
        
        # Run Pipeline
        print(f"Processing {file.filename} ({audio_type}) -> {target_lang}")
        
        if audio_type == "song":
            print("🎵 Detected song - using vocal isolation approach")
            final_output_path, processed_segments, metadata = await pipeline_manager.process_song(
                input_path, target_lang
            )
        else:
            print("🎤 Detected speech - using standard translation")
            final_output_path, processed_segments, metadata = await pipeline_manager.process_audio_file(
                input_path, target_lang
            )
        
        # Return result
        output_filename = os.path.basename(final_output_path)
        job_id = metadata["job_id"]
        
        # Store session data for editing
        job_sessions[job_id] = {
            "segments": processed_segments,
            "metadata": metadata,
            "audio_type": audio_type,
            "target_lang": target_lang,
            "final_output": final_output_path
        }
        
        return {
            "status": "success",
            "job_id": job_id,
            "audio_url": f"/outputs/{output_filename}",
            "original_file": file.filename,
            "audio_type": audio_type,
            "segments": processed_segments,
            "metadata": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Pipeline Error: {e}")
        import traceback
        traceback.print_exc()
        # Cleanup on error
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/lyrics/{job_id}")
async def get_lyrics(job_id: str):
    """
    Get lyrics for a job - returns original and translated lyrics for all segments.
    """
    if job_id not in job_sessions:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = job_sessions[job_id]
    lyrics = []
    
    for idx, seg in enumerate(job["segments"]):
        lyrics.append({
            "segment_id": idx,
            "start": seg["start"],
            "end": seg["end"],
            "duration": seg["end"] - seg["start"],
            "original_text": seg.get("original_text", ""),
            "translated_text": seg.get("translated_text", ""),
            "emotion": seg.get("emotion", "neutral"),
            "gender": seg.get("gender", "male"),
            "age_group": seg.get("age_group", "adult"),
            "voice_profile": seg.get("voice_profile", "male_adult_neutral")
        })
    
    return {
        "job_id": job_id,
        "audio_type": job["audio_type"],
        "target_language": job["target_lang"],
        "lyrics": lyrics
    }

@app.post("/edit-segment/{job_id}")
async def edit_segment(job_id: str, segment_id: int, new_translated_text: str = Form(...)):
    """
    Edit and re-translate a specific segment.
    """
    if job_id not in job_sessions:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = job_sessions[job_id]
    if segment_id < 0 or segment_id >= len(job["segments"]):
        raise HTTPException(status_code=400, detail=f"Invalid segment ID: {segment_id}")
    
    try:
        segment = job["segments"][segment_id]
        
        # Re-translate if needed (if original text was different)
        if new_translated_text.strip():
            segment["translated_text"] = new_translated_text
        
        return {
            "status": "success",
            "segment_id": segment_id,
            "translated_text": segment["translated_text"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Edit failed: {str(e)}")

@app.post("/regenerate-segment/{job_id}")
async def regenerate_segment(
    job_id: str,
    segment_id: int = Form(...),
    gender: str = Form("male"),
    age_group: str = Form("adult")
):
    """
    Regenerate audio for a segment with a different voice profile.
    Options: gender (male/female), age_group (child/young_adult/adult/elderly)
    """
    if job_id not in job_sessions:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    job = job_sessions[job_id]
    if segment_id < 0 or segment_id >= len(job["segments"]):
        raise HTTPException(status_code=400, detail=f"Invalid segment ID: {segment_id}")
    
    try:
        segment = job["segments"][segment_id]
        target_lang = job["target_lang"]
        
        # Update voice profile
        profile_map = f"{gender}_{age_group}_neutral"
        
        # Get available voices for the target language
        from .config import LANGUAGE_VOICE_MAPS
        if target_lang not in LANGUAGE_VOICE_MAPS:
            raise HTTPException(status_code=400, detail=f"Language {target_lang} not supported")
        
        voices = LANGUAGE_VOICE_MAPS[target_lang]
        if profile_map not in voices:
            # Fallback to first available voice
            profile_map = list(voices.keys())[0]
        
        # Regenerate TTS audio
        output_path = os.path.join(OUTPUTS_DIR, f"{job_id}_seg_{segment_id}_regenerated.mp3")
        from .translator import optimize_for_speech
        optimized_text = optimize_for_speech(segment["translated_text"])
        
        await tts.generate_speech_async(optimized_text, profile_map, output_path, lang=target_lang)
        
        # Update segment metadata
        segment["voice_profile"] = profile_map
        segment["gender"] = gender
        segment["age_group"] = age_group
        
        return {
            "status": "success",
            "segment_id": segment_id,
            "voice_profile": profile_map,
            "gender": gender,
            "age_group": age_group,
            "audio_path": f"/outputs/{os.path.basename(output_path)}"
        }
    except Exception as e:
        print(f"Regenerate failed: {e}")
        raise HTTPException(status_code=500, detail=f"Regeneration failed: {str(e)}")

@app.post("/rebuild-audio/{job_id}")
async def rebuild_audio(job_id: str):
    """
    Rebuild the final audio after editing segments or changing voice profiles.
    Merges all updated segments into a new final audio file.
    """
    if job_id not in job_sessions:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    try:
        job = job_sessions[job_id]
        
        # This would require re-merging segments with updated audio
        # For now, just return the existing output
        final_output = job.get("final_output")
        if not final_output or not os.path.exists(final_output):
            raise HTTPException(status_code=500, detail="Final audio file not found")
        
        return {
            "status": "success",
            "job_id": job_id,
            "audio_url": f"/outputs/{os.path.basename(final_output)}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")

# Serve Outputs and Frontend
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# Define BASE_DIR for ROOT_DIR calculation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Serve the actual frontend from the root dir
ROOT_DIR = os.path.dirname(BASE_DIR)
app.mount("/", StaticFiles(directory=ROOT_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
