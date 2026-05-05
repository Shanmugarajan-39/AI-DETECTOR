import google.generativeai as genai
from PIL import Image
from core.config import GEMINI_API_KEY, GEMINI_MODEL, LABEL_AI, LABEL_HUMAN, LABEL_EDITED, LABEL_INCONCLUSIVE
from core.utils import setup_logger
import json
import os

logger = setup_logger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def detect_image_gemini(filepath):
    """
    Use Gemini 2.5 Flash to analyze the image for AI generation.
    """
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Open image for Gemini within context to release file lock
        with Image.open(filepath) as img:
            prompt = """
            Perform an objective forensic analysis on this image to determine its origin.
            
            You must decide if the image is:
            1. AI-GENERATED: Created by models like Midjourney, DALL-E, or Stable Diffusion.
            2. HUMAN EDITED/COMPOSITE: Real photos that have been manually manipulated (Photoshop, collage, filters).
            3. AUTHENTIC: Untouched photography or high-quality digital art by a human.

            Analysis Criteria:
            - ANATOMICAL COHERENCE: Check for subtle AI errors in hands, eyes, teeth, and background figures.
            - NOISE & TEXTURE: AI often lacks consistent sensor noise found in real photography. Look for 'too smooth' areas or repetitive patterns.
            - LIGHTING & REFLECTIONS: Check if shadows and catchlights in eyes follow consistent physics.
            - COMPRESSION ARTIFACTS: Real images often have JPG artifacts. Do not mistake low resolution or compression for AI generation.

            Be balanced. If there is no clear evidence of AI, classify as 'authentic'.
            
            Respond ONLY with a JSON object:
            {
                "classification": "ai" | "edited" | "authentic",
                "confidence": float (0.0 to 1.0),
                "reason": "Brief technical explanation of your finding."
            }
            """

            response = model.generate_content([prompt, img])
        
        # Parse response
        try:
            res_text = response.text.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(res_text)
            
            classification = str(data.get("classification", "authentic")).lower().strip()
            
            # More flexible mapping to catch variations
            if "ai" in classification or "synthetic" in classification:
                prediction = LABEL_AI
            elif "edited" in classification or "composite" in classification:
                prediction = LABEL_EDITED
            else:
                prediction = LABEL_HUMAN
            
            # Calibration: Use model's confidence but ensure it's displayed reasonably
            raw_conf = data.get("confidence", 0.5)
            # If the model says AI but confidence is low, maybe it's human?
            # Actually, let's trust the classification but reflect the confidence.
            display_conf = round(raw_conf * 100, 2)
            
            return {
                "prediction": prediction,
                "confidence": display_conf,
                "ai_probability": round(raw_conf, 4) if prediction == LABEL_AI else round(1.0 - raw_conf, 4),
                "human_probability": round(1.0 - raw_conf, 4) if prediction == LABEL_AI else round(raw_conf, 4),
                "details": {
                    "reason": data.get("reason", "Analysis complete."),
                    "model_used": GEMINI_MODEL,
                    "determination": classification
                }
            }

        except Exception as parse_error:
            logger.error(f"Failed to parse Gemini response: {parse_error}")
            return {"error": "AI response was malformed."}

    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return {"error": f"Gemini API failed: {str(e)}"}
