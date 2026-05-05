import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image, ImageOps
from .config import MODEL_ID, IMAGE_AI_THRESHOLD
from .utils import setup_logger

logger = setup_logger(__name__)

class Processor:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Processor, cls).__new__(cls)
            try:
                logger.info(f"Loading processor and model: {MODEL_ID}")
                cls._instance.processor = AutoImageProcessor.from_pretrained(MODEL_ID)
                cls._instance.model = AutoModelForImageClassification.from_pretrained(MODEL_ID)
                cls._instance.model.eval()
                
                # Verify and log label mapping
                mapping = cls._instance.model.config.id2label
                logger.info(f"!!! MODEL LABEL MAPPING: {mapping}")
                
                # Check for known dima806 mapping if labels are generic
                if "LABEL_0" in str(mapping):
                    logger.warning("Generic labels detected. Using standard mapping for dima806: 0=Real, 1=Fake")
                    cls._instance.ai_idx = 1
                    cls._instance.real_idx = 0
                else:
                    cls._instance.ai_idx = -1
                    cls._instance.real_idx = -1
                    for idx, label in mapping.items():
                        l = label.lower()
                        if "fake" in l or "ai" in l or "synthetic" in l or "artificial" in l:
                            cls._instance.ai_idx = idx
                        elif "real" in l or "human" in l or "authentic" in l:
                            cls._instance.real_idx = idx
                    
                    if cls._instance.ai_idx == -1 or cls._instance.real_idx == -1:
                        logger.error("COULD NOT DETERMINE LABEL MAPPING. Defaulting to 0=Real, 1=Fake")
                        cls._instance.ai_idx = 1
                        cls._instance.real_idx = 0
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                cls._instance.model = None
        return cls._instance

    def get_tta_images(self, image):
        """
        Generate TTA (Test-Time Augmentation) images.
        """
        images = [image] # Original
        
        # Horizontal flip
        images.append(ImageOps.mirror(image))
        
        # Center crop / Slightly zoom
        w, h = image.size
        crop_size = 0.9
        left = (1 - crop_size) / 2 * w
        top = (1 - crop_size) / 2 * h
        right = (1 + crop_size) / 2 * w
        bottom = (1 + crop_size) / 2 * h
        images.append(image.crop((left, top, right, bottom)))
        
        return images

    def predict_image(self, image):
        if self.model is None:
            return None
        
        # Ensure RGB
        if image.mode != "RGB":
            image = image.convert("RGB")
            
        tta_images = self.get_tta_images(image)
        all_probs = []
        
        with torch.no_grad():
            for img in tta_images:
                inputs = self.processor(images=img, return_tensors="pt")
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.nn.functional.softmax(logits, dim=-1)
                all_probs.append(probs[0].numpy())
        
        # Average probabilities across TTA passes
        avg_probs = np.mean(all_probs, axis=0)
        
        # Map labels using fixed indices
        ai_idx = self.ai_idx
        real_idx = self.real_idx
        
        ai_prob = float(avg_probs[ai_idx])
        human_prob = float(avg_probs[real_idx])
        
        logger.info(f"--- PREDICTION DEBUG ---")
        logger.info(f"Raw Probailities (Avg across TTA): {avg_probs}")
        logger.info(f"AI Index: {ai_idx} | Real Index: {real_idx}")
        logger.info(f"AI Prob: {ai_prob:.4f} | Real Prob: {human_prob:.4f}")
        logger.info(f"------------------------")
        
        return {
            "ai_prob": ai_prob,
            "human_prob": human_prob,
            "id2label": self.model.config.id2label
        }

import numpy as np
preprocess_service = Processor()
