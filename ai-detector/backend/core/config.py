import os

# Gemini Configuration
GEMINI_API_KEY = "AIzaSyDlRdwz2jWJGThwJZI6XJrkpz3Jxga04xk"
GEMINI_MODEL = "models/gemini-flash-latest" # Using the latest flash alias for reliability

# Offline Model Configuration
MODEL_ID = "umm-maybe/AI-image-detector"
HF_CACHE = "D:\\huggingface_cache"
os.environ["HF_HOME"] = HF_CACHE

# Detection Calibration
IMAGE_AI_THRESHOLD = 0.90
IMAGE_INCONCLUSIVE_THRESHOLD = 0.80
VIDEO_FRAME_AI_THRESHOLD = 0.85
VIDEO_VOTE_RATIO = 0.65

# Video Sampling
MIN_VIDEO_FRAMES = 16
MAX_VIDEO_FRAMES = 24

# Labels
LABEL_AI = "AI Generated"
LABEL_HUMAN = "Human Created"
LABEL_AI_AUDIO = "AI Synthesized"
LABEL_REAL_AUDIO = "Authentic Voice"
LABEL_AI_TEXT = "AI Generated Text"
LABEL_HUMAN_TEXT = "Human Written Text"
LABEL_EDITED = "Human Edited / Composite"
LABEL_INCONCLUSIVE = "Inconclusive"

# Upload Config
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
