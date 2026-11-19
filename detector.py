"""
Person detection for Sports Meet 2026.
YOLOv8 (fast & highly accurate when ultralytics is available) with an
OpenCV HOG default fallback that requires zero external model downloads.
"""
import os
import cv2
import numpy as np


class PersonDetector:
    def __init__(self, backend="auto", confidence=0.45, yolo_model="yolov8n.pt"):
        self.confidence = confidence
        self.backend = None
        self.model = None
        self.hog = None

        if backend in ("auto", "yolo"):
            try:
                from ultralytics import YOLO
                if not os.path.isabs(yolo_model) and not os.path.exists(yolo_model):
                    local_model = os.path.join(os.path.dirname(os.path.abspath(__file__)), yolo_model)
                    if os.path.exists(local_model):
                        yolo_model = local_model
                self.model = YOLO(yolo_model)
                self.backend = "yolo"
                print(f"[detector] Using YOLO model: {yolo_model}")
            except Exception as exc:
                msg = "YOLO not installed" if backend == "auto" else "Could not load YOLO"
                print(f"[detector] {msg} ({exc}). Using OpenCV HOG.")

        if self.backend is None:
            self.hog = cv2.HOGDescriptor()
            self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            self.backend = "hog"
            print("[detector] Using OpenCV HOG person detector (lightweight built-in).")

    def detect(self, frame):
        """Return a list of (x1, y1, x2, y2, confidence) boxes for detected people."""
        if frame is None or frame.size == 0:
            return []
        try:
            if self.backend == "yolo":
                return self._detect_yolo(frame)
            return self._detect_hog(frame)
        except Exception as exc:
            print(f"[detector] Detection frame error: {exc}")
            return []

    def _detect_yolo(self, frame):
        result = self.model(frame, classes=[0], conf=self.confidence, imgsz=384, verbose=False)[0]
        if result.boxes is None or len(result.boxes) == 0:
            return []
        xyxy = result.boxes.xyxy.cpu().numpy()
        conf = result.boxes.conf.cpu().numpy()
        return [(int(a), int(b), int(c), int(d), float(s)) for (a, b, c, d), s in zip(xyxy, conf)]

    def _detect_hog(self, frame):
        h, w = frame.shape[:2]
        scale = 640.0 / w if w > 640 else 1.0
        small = cv2.resize(frame, (int(w * scale), int(h * scale))) if scale != 1.0 else frame
        rects, weights = self.hog.detectMultiScale(
            small, winStride=(8, 8), padding=(8, 8), scale=1.05
        )
        if len(rects) == 0:
            return []
        weights = np.array(weights).flatten().astype(float)
        boxes = [[int(x), int(y), int(bw), int(bh)] for (x, y, bw, bh) in rects]
        # HOG scores are not strictly 0-1; standard threshold of 0.45-0.5 works reliably
        keep = cv2.dnn.NMSBoxes(boxes, weights.tolist(), 0.4, 0.45)
        out = []
        for i in np.array(keep).flatten():
            x, y, bw, bh = boxes[i]
            x1 = max(0, int(x / scale))
            y1 = max(0, int(y / scale))
            x2 = min(w, int((x + bw) / scale))
            y2 = min(h, int((y + bh) / scale))
            out.append((x1, y1, x2, y2, float(min(max(weights[i], 0.1), 1.0))))
        return out
