"""
detector.py — Traffic sign detection pipeline using a custom-trained YOLOv8 model.

Drop your trained best.pt into the weights/ folder, then import this module.
"""

import cv2
import numpy as np
from ultralytics import YOLO

# ── Config ────────────────────────────────────────────────────────────────────
WEIGHTS_PATH  = "weights/best.pt"   # ← update after training
CONF_THRESHOLD = 0.25               # lower = more detections, higher = fewer false positives
IMG_SIZE       = 640
CLASS_NAMES    = ["Go straight", "Stop", "Turn Left", "Turn Right", "Workers"]
BLUR_THRESHOLD = 10.0               # Laplacian variance below this → image too blurry (bajado para debug)

# Colour per class (BGR)
CLASS_COLORS = {
    "Go straight":      (0,   255, 0),     # green
    "Stop":             (0,   0,   255),   # red
    "Turn Left":        (255, 200, 0),     # cyan
    "Turn Right":       (255, 100, 200),   # purple
    "Workers":          (0,   165, 255),   # orange
}
# ─────────────────────────────────────────────────────────────────────────────


class TrafficSignDetection:
    def __init__(self, weights: str = WEIGHTS_PATH):
        print(f"[Detector] Loading model from: {weights}")
        self.model = YOLO(weights)
        self.class_names = CLASS_NAMES

    # ── Acercamiento A: Image Quality Filter ──────────────────────────────────
    def is_blurry(self, image: np.ndarray, threshold: float = BLUR_THRESHOLD) -> bool:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        fm = cv2.Laplacian(gray, cv2.CV_64F).var()
        return fm < threshold

    # ── Acercamiento B: CNN Detection ─────────────────────────────────────────
    def detect_signs(self, image: np.ndarray):
        """
        Run the full detection pipeline on a single BGR frame.

        Returns
        -------
        annotated_image : np.ndarray   frame with bounding boxes drawn
        detected_sign   : str          label of the highest-confidence detection,
                                       or "None" / "Blurry"
        """
        if self.is_blurry(image):
            cv2.putText(image, "⚠ Blurry frame — skipping", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            return image, "Blurry"

        results = self.model(image, conf=CONF_THRESHOLD, imgsz=IMG_SIZE, verbose=False)

        best_sign  = "None"
        best_conf  = 0.0

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                conf   = float(box.conf[0])

                label = (self.class_names[cls_id]
                         if cls_id < len(self.class_names)
                         else f"Unknown_{cls_id}")

                color = CLASS_COLORS.get(label, (200, 200, 200))

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{label} {conf:.2f}",
                            (x1, max(y1 - 10, 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)

                if conf > best_conf:
                    best_conf  = conf
                    best_sign  = label

        return image, best_sign
