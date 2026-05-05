import google.generativeai as genai
import os
import json
from core.config import GEMINI_API_KEY, GEMINI_MODEL, LABEL_AI_AUDIO, LABEL_REAL_AUDIO
from core.utils import setup_logger

logger = setup_logger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

def detect_audio_gemini(filepath):
    """
    Analyze audio file for AI synthesis using Gemini.
    """
    try:
        # 1. Upload audio to Gemini
        logger.info(f"Uploading audio to Gemini: {os.path.basename(filepath)}")
        audio_file = genai.upload_file(path=filepath)
        
        # 2. Analyze
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = """
        Analyze this audio file objectively as a digital forensic expert.
        Your goal is to distinguish between a real human voice recording and an AI-synthesized voice (deepfake).
        
        Analysis Criteria:
        1. NATURAL BREATHING & PROSODY: Listen for subtle human breaths and natural emotional variations in tone. AI often has mechanical rhythm or holds vowels unnaturally.
        2. SPECTRAL TRACES: Check for digital artifacts, 'chirps', or robotic transitions between words that are not caused by low bit-rate compression.
        3. BACKGROUND NOISE COHERENCE: In real recordings, background noise is often consistent. AI voices sometimes have perfectly silent backgrounds or 'vacuum' silence between sentences.

        If the voice sounds authentic with no clear digital artifacts, classify as 'human'.
        
        Respond ONLY with a JSON object:
        {
            "classification": "ai" | "authentic",
            "confidence": float (0.0 to 1.0),
            "reason": "Identify specific AI voice artifacts or confirm human characteristics. Use 'ai' for synthetic voices."
        }
        """

        response = model.generate_content([prompt, audio_file])
        
        # Cleanup
        genai.delete_file(audio_file.name)

        # Parse
        res_text = response.text.strip()
        if "```json" in res_text:
            res_text = res_text.split("```json")[1].split("```")[0].strip()
        elif "```" in res_text:
            res_text = res_text.split("```")[1].split("```")[0].strip()
        
        data = json.loads(res_text)
        classification = str(data.get("classification", "authentic")).lower().strip()
        is_ai = "ai" in classification or "synthetic" in classification
        
        prediction = LABEL_AI_AUDIO if is_ai else LABEL_REAL_AUDIO
        raw_conf = data.get("confidence", 0.5)
        
        return {
            "prediction": prediction,
            "confidence": round(raw_conf * 100, 2),
            "ai_probability": round(raw_conf, 4) if is_ai else round(1.0 - raw_conf, 4),
            "human_probability": round(1.0 - raw_conf, 4) if is_ai else round(raw_conf, 4),
            "details": {
                "reason": data.get("reason", "Analysis complete."),
                "model_used": GEMINI_MODEL,
                "raw_confidence": raw_conf,
                "determination": classification
            }
        }

    except Exception as e:
        logger.error(f"Gemini Audio API error: {e}")
        return {"error": str(e)}
