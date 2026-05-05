import google.generativeai as genai
import time
from core.config import GEMINI_API_KEY, GEMINI_MODEL, LABEL_AI, LABEL_HUMAN, LABEL_INCONCLUSIVE
from core.utils import setup_logger
import json
import os
import cv2
from PIL import Image
from detectors.gemini_detector import detect_image_gemini

logger = setup_logger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def detect_video_gemini(filepath):
    """
    Optimized Video Forensic Engine.
    Extracts key frames and performs parallel visual forensics to identify AI motion artifacts.
    This is significantly faster than full video upload and more accurate than single-frame checks.
    """
    try:
        logger.info(f"Extracting forensic frames from: {os.path.basename(filepath)}")
        
        cap = cv2.VideoCapture(filepath)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            return {"error": "Invalid video file or codec error."}

        # Extract 8 evenly spaced frames to stay within token limits and maintain speed
        frames = []
        indices = [int(total_frames * i / 8) for i in range(8)]
        
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                # Convert BGR (OpenCV) to RGB (PIL)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(frame_rgb)
                frames.append(pil_img)
        
        cap.release()

        if not frames:
            return {"error": "Could not extract frames for analysis."}

        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = """
        Analyze these sequential frames from a video to determine if it is AI-generated (e.g., Sora, Kling, Luma) or a real human recording.
        
        Forensic Checklist:
        1. TEMPORAL CONSISTENCY: Do objects or background details morph or disappear between frames?
        2. ANATOMICAL DRIFT: Check if hands, hair, or facial features maintain a consistent structure. AI often has 'shimmering' details.
        3. PHYSICS & MOTION: Is the motion natural? Look for 'too smooth' interpolation or glitchy transitions.
        4. LIGHTING: Does the light source remain consistent across the sequence?

        Be objective. If the video looks like a natural recording without AI artifacts, classify as 'human'.
        
        Respond ONLY with a JSON object:
        {
            "classification": "ai" | "edited" | "authentic",
            "confidence": float (0.0 to 1.0),
            "reason": "Brief technical explanation. Use 'ai' for synthetic, 'authentic' for human photography."
        }
        """

        # Send all frames in one request for temporal context
        response = model.generate_content([prompt] + frames)
        
        res_text = response.text.strip()
        if "```json" in res_text: res_text = res_text.split("```json")[1].split("```")[0].strip()
        elif "```" in res_text: res_text = res_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(res_text)
        classification = str(data.get("classification", "authentic")).lower().strip()
        
        # Consistent mapping
        if "ai" in classification or "synthetic" in classification:
            prediction = LABEL_AI
            is_ai = True
        elif "edited" in classification or "composite" in classification:
            prediction = LABEL_AI # Or LABEL_EDITED if defined, but video uses LABEL_AI for high flags
            is_ai = True
        else:
            prediction = LABEL_HUMAN
            is_ai = False
            
        raw_conf = data.get("confidence", 0.5)

        return {
            "prediction": prediction,
            "confidence": round(raw_conf * 100, 2),
            "ai_probability": round(raw_conf, 4) if is_ai else round(1.0 - raw_conf, 4),
            "human_probability": round(1.0 - raw_conf, 4) if is_ai else round(raw_conf, 4),
            "details": {
                "reason": data.get("reason", "Multi-frame forensic analysis complete."),
                "model_used": GEMINI_MODEL,
                "frames_analyzed": len(frames),
                "determination": classification
            }
        }

    except Exception as e:
        logger.error(f"Detection engine failed: {e}")
        return {"error": f"Forensic engine failure: {str(e)}"}
