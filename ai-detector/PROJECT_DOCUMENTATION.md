# AI Detector: Workflow & Technical Documentation

This document provides a comprehensive overview of how the AI Image and Video Detector application works and the technologies that power it.

---

## 1. System Workflow

The following outlines the step-by-step process from user interaction to AI analysis.

### Frontend Interaction
- **Selection**: The user chooses between **Image Authenticator** or **Video Authenticator** mode.
- **Upload**: The user uploads a file via the drag-and-drop zone or file selector.
- **Preview**: The application provides an instant preview of the uploaded image or video.
- **Submission**: Upon clicking **"Check Authenticity"**, the frontend sends the file to the backend API using a `multipart/form-data` request.

### Backend Processing (FastAPI)
- **Reception**: The `/detect` endpoint receives the incoming file.
- **Validation**: The server checks if the file type is supported (JPG/PNG/WEBP for images, MP4/MOV/AVI for videos) and ensures the size does not exceed 50MB.
- **Temporary Storage**: The file is assigned a unique UUID and saved to the `uploads/` folder temporarily to prevent filename collisions.

### Core Analysis Logic (Detector)
- **Image Detection**:
    - The image is opened using **Pillow** and converted to RGB.
    - It is passed through a pre-trained **Vision Transformer (ViT)** model (`dima806/ai_vs_real_image_detection`).
    - The model returns a confidence score for "Fake" (AI) and "Real" (Human).
- **Video Detection**:
    - The video is processed using **OpenCV**.
    - 10 frames are sampled at equal intervals across the video duration.
    - Each frame is analyzed individually, and the final result is the **average confidence score**.

### Result Delivery
- **Normalization**: The backend converts labels into user-friendly terms: **"AI Generated"** or **"Human Created"**.
- **UI Update**: The frontend displays the result with a dynamic progress bar and color-coded alerts.
- **History**: Results are saved to the browser's `localStorage` for quick reference.

---

## 2. Libraries and Tools Guide

The project utilizes a specialized stack for web performance and deep learning accuracy.

### Backend (Python)
| Library | Purpose |
| :--- | :--- |
| **FastAPI** | High-performance web framework for the API. |
| **Uvicorn** | ASGI server to run the application. |
| **Transformers** | Interface for loading Hugging Face AI models. |
| **PyTorch** | Deep learning engine for model inference. |
| **OpenCV** | Handles video frame extraction and processing. |
| **Pillow (PIL)** | Image manipulation and format conversion. |
| **NumPy** | Mathematical operations for data processing. |

### Frontend (Web)
| Tool/Library | Purpose |
| :--- | :--- |
| **Bootstrap 5** | Responsive layout and UI components. |
| **Vanilla JavaScript** | Core logic, API calls, and DOM manipulation. |
| **Local Storage** | Stores the history of the last 10 analyses. |
| **CSS3** | Glassmorphism effects and custom animations. |

---

## 3. AI Model Details
- **Architecture**: Vision Transformer (ViT).
- **Function**: Binary classification (AI vs. Human).
- **Source**: Hugging Face Hub (Model: `dima806/ai_vs_real_image_detection`).
