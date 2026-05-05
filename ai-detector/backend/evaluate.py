import os
import argparse
from detectors.image_detector import detect_image
from detectors.video_detector import detect_video
from sklearn.metrics import confusion_matrix, classification_report
import json

def run_evaluation(data_dir):
    results = {"image": [], "video": []}
    y_true = {"image": [], "video": []}
    y_pred = {"image": [], "video": []}
    misclassified = []

    # Expected structure: /test_data/images/ai, /test_data/images/real
    for media_type in ["images", "videos"]:
        for label in ["ai", "real"]:
            folder = os.path.join(data_dir, media_type, label)
            if not os.path.exists(folder):
                continue
                
            expected = "AI Generated" if label == "ai" else "Human Created"
            
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                print(f"Testing {media_type}/{label}: {filename}...")
                
                if media_type == "images":
                    res = detect_image(filepath)
                    m_key = "image"
                else:
                    res = detect_video(filepath)
                    m_key = "video"
                
                if "prediction" in res:
                    pred = res["prediction"]
                    y_true[m_key].append(expected)
                    y_pred[m_key].append(pred)
                    
                    if pred != expected:
                        misclassified.append({
                            "file": filepath,
                            "expected": expected,
                            "predicted": pred,
                            "details": res
                        })

    # Print Reports
    for m_key in ["image", "video"]:
        if len(y_true[m_key]) > 0:
            print(f"\n=== {m_key.upper()} EVALUATION REPORT ===")
            print(classification_report(y_true[m_key], y_pred[m_key]))
            print("Confusion Matrix:")
            print(confusion_matrix(y_true[m_key], y_pred[m_key]))

    # Save Misclassified
    with open("misclassified_report.json", "w") as f:
        json.dump(misclassified, f, indent=4)
    print(f"\nMisclassified report saved to misclassified_report.json")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="test_data", help="Directory containing test data")
    args = parser.parse_args()
    
    if os.path.exists(args.dir):
        run_evaluation(args.dir)
    else:
        print(f"Directory {args.dir} not found. Please create it with subfolders images/ai, images/real, etc.")
