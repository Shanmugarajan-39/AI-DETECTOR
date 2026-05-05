import logging
import numpy as np
import cv2

def setup_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(name)

def is_frame_low_info(frame, blur_threshold=100.0, brightness_threshold=30.0):
    """
    Detect if a frame is too blurry or too dark.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Blur detection using Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    is_blurry = laplacian_var < blur_threshold
    
    # Brightness detection
    avg_brightness = np.mean(gray)
    is_dark = avg_brightness < brightness_threshold
    
    return is_blurry or is_dark

def are_frames_duplicate(frame1, frame2, threshold=0.95):
    """
    Simple check to see if two frames are nearly identical.
    """
    if frame1 is None or frame2 is None:
        return False
    
    # Resize for faster comparison
    f1 = cv2.resize(frame1, (64, 64))
    f2 = cv2.resize(frame2, (64, 64))
    
    # Correlation coefficient
    res = cv2.matchTemplate(f1, f2, cv2.TM_CCOEFF_NORMED)
    return res[0][0] > threshold
