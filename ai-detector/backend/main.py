from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from core.config import UPLOAD_DIR, MAX_CONTENT_LENGTH, GEMINI_MODEL
from detectors.gemini_detector import detect_image_gemini as detect_image
from detectors.video_detector import detect_video_gemini as detect_video
from detectors.audio_detector import detect_audio_gemini as detect_audio
from detectors.text_detector import detect_text_gemini as detect_text

app = FastAPI(title="VeriTruth AI - Forensic Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

# Standardized extensions
SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
SUPPORTED_VIDEOS = {".mp4", ".mov", ".avi", ".mkv"}
SUPPORTED_AUDIO = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"}

def safe_remove(filepath, delay=1.0):
    if os.path.exists(filepath):
        time.sleep(delay)
        try: os.remove(filepath)
        except Exception:
            time.sleep(1.0)
            try: os.remove(filepath)
            except Exception as e: logger.error(f"Cleanup failed: {e}")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"REQUEST: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

@app.post("/detect")
async def detect_file(file: UploadFile = File(...)):
    filename = file.filename.strip().lower()
    ext = os.path.splitext(filename)[1]
    
    logger.info(f"ANALYZING MEDIA: {filename} (Detected Ext: '{ext}')")
    
    file_type = None
    if ext in SUPPORTED_IMAGES: file_type = "image"
    elif ext in SUPPORTED_VIDEOS: file_type = "video"
    elif ext in SUPPORTED_AUDIO: file_type = "audio"
    
    if not file_type:
        # Final fallback check in case ext parsing failed
        if any(filename.endswith(e) for e in SUPPORTED_AUDIO): file_type = "audio"
        elif any(filename.endswith(e) for e in SUPPORTED_IMAGES): file_type = "image"
        elif any(filename.endswith(e) for e in SUPPORTED_VIDEOS): file_type = "video"

    if not file_type:
        logger.error(f"FATAL: {filename} is NOT SUPPORTED. Ext: '{ext}'")
        raise HTTPException(status_code=400, detail=f"Unsupported format: '{ext}'")
    
    unique_filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Processing forensic {file_type} analysis...")
        if file_type == "image": result = detect_image(filepath)
        elif file_type == "video": result = detect_video(filepath)
        elif file_type == "audio": result = detect_audio(filepath)
            
        safe_remove(filepath)
        if "error" in result: raise HTTPException(status_code=500, detail=result["error"])
        return result
        
    except Exception as e:
        logger.error(f"Forensic error: {e}")
        safe_remove(filepath)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect/text")
async def detect_text_content(content: str = Form(...)):
    logger.info(f"ANALYZING TEXT. Input size: {len(content)}")
    try:
        result = detect_text(content)
        if "error" in result: raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Text check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "operational", "engine": "VeriTruth 2.0", "model": GEMINI_MODEL}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
