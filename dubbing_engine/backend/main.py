from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
import asyncio

from .manager import pipeline_manager
from .config import UPLOADS_DIR, OUTPUTS_DIR, SUPPORTED_LANGUAGES

app = FastAPI(title="Professional Audio Dubbing Engine")

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
    # Warm up models if needed
    from . import stt
    stt.get_model()
    print("System Ready.")

@app.post("/translate")
async def translate_audio(
    file: UploadFile = File(...),
    target_lang: str = Form("ta")
):
    """
    Main endpoint for professional audio translation.
    """
    if target_lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language")
        
    # 1. Save input file
    input_path = os.path.join(UPLOADS_DIR, file.filename)
    
    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        # 2. Run Pipeline
        print(f"Processing {file.filename} -> {target_lang}")
        final_output_path, processed_segments = await pipeline_manager.process_audio_file(input_path, target_lang)
        
        # 3. Return result
        output_filename = os.path.basename(final_output_path)
        return {
            "status": "success",
            "audio_url": f"/outputs/{output_filename}",
            "original_file": file.filename,
            "segments": processed_segments
        }
    except Exception as e:
        print(f"Pipeline Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
