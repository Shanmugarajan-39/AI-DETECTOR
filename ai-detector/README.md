# AI Content Detector Pro

A professional, high-performance web application designed to distinguish between AI-generated (synthetic) and human-created (authentic) images and videos using Vision Transformers (ViT).

## ✨ Key Features
- **Pro Detection Pipeline**: Uses Test-Time Augmentation (TTA) for images and robust voting for videos.
- **Advanced Video Filtering**: Automatically ignores blurry, dark, or duplicate frames to increase accuracy.
- **Glassmorphism UI**: High-end dark theme with smooth animations and responsive design.
- **Inconclusive Handling**: Provides an "Inconclusive" result when media quality is too low for reliable detection.
- **Analysis History**: Keeps track of your last 10 detections locally in the browser.

## 📁 Project Structure
```text
ai-detector/
├── backend/
│   ├── main.py              # FastAPI Entry Point
│   ├── detectors/           # Specialized detection logic
│   │   ├── image_detector.py
│   │   └── video_detector.py
│   ├── core/                # System core logic
│   │   ├── config.py        # ALL THRESHOLDS & CONSTANTS
│   │   ├── preprocessing.py # ViT Processing & TTA
│   │   └── utils.py         # Frame filtering utilities
│   ├── evaluate.py          # Benchmark/Testing tool
│   └── requirements.txt     # Dependencies
├── frontend/
│   ├── index.html           # UI Structure
│   ├── style.css            # Premium System Styles
│   └── script.js            # Frontend Logic
└── uploads/                 # Processing workspace
```

## 🚀 How to Run the System

### 1. Backend Setup
Recommended: Python 3.9+
Navigate to the `backend` folder and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### 2. Start the Backend
```bash
python main.py
```
- The server initializes at `http://localhost:8000`.
- **Note**: On the first run, it will download the Vision Transformer model (~350MB).

### 3. Run the Frontend
The frontend is a standalone web app. You can open `frontend/index.html` directly in your browser, but for full functionality (CORS/Caching), using a local server is recommended:
```bash
# Using Python's built-in server
cd frontend
python -m http.server 3000
```
Then visit `http://localhost:3000` in your browser.

---

## 📊 Evaluation & Testing
To test the accuracy of the system against your own dataset:
1. Create a `test_data` folder in `backend/`.
2. Organize files as follows: `test_data/images/ai/`, `test_data/images/real/`, etc.
3. Run the evaluation script:
```bash
python evaluate.py --dir test_data
```
This will generate a detailed accuracy report and a `misclassified_report.json`.

---

## 🛠️ Calibration
You can tune the sensitivity of the AI detector in `backend/core/config.py`:
- `IMAGE_AI_THRESHOLD = 0.65`: Probability needed to label an image as AI.
- `VIDEO_VOTE_RATIO = 0.60`: Percentage of frames that must be flagged as AI to mark the entire video as AI.
- `VIDEO_FRAME_AI_THRESHOLD = 0.70`: Strictness applied to individual video frames.
