from PIL import Image
from core.preprocessing import preprocess_service
from core.config import IMAGE_AI_THRESHOLD, IMAGE_INCONCLUSIVE_THRESHOLD, LABEL_AI, LABEL_HUMAN, LABEL_INCONCLUSIVE
from core.utils import setup_logger

logger = setup_logger(__name__)

def detect_image(filepath):
    try:
        img = Image.open(filepath)
        results = preprocess_service.predict_image(img)
        
        if results is None:
            return {"error": "Model not loaded"}
            
        ai_prob = results["ai_prob"]
        human_prob = results["human_prob"]
        
        # New Decision logic with Inconclusive zone
        if ai_prob >= IMAGE_AI_THRESHOLD:
            prediction = LABEL_AI
            confidence = ai_prob
        elif ai_prob >= IMAGE_INCONCLUSIVE_THRESHOLD:
            prediction = LABEL_INCONCLUSIVE
            confidence = ai_prob
        else:
            prediction = LABEL_HUMAN
            confidence = human_prob
            
        return {
            "prediction": prediction,
            "confidence": round(confidence * 100, 2),
            "ai_probability": round(ai_prob, 4),
            "human_probability": round(human_prob, 4),
            "details": {
                "threshold_used": IMAGE_AI_THRESHOLD,
                "label_mapping": results["id2label"]
            }
        }
    except Exception as e:
        logger.error(f"Image detection error: {e}")
        return {"error": str(e)}
