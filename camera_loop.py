# Camera detection thread (unchanged logic)
import time, threading
import cv2
import numpy as np
from ultralytics import YOLO

from config import MODEL_NAME, MAX_FPS
from utils_coco import coco_name, normalize_label
from distance import estimate_distance_m
from proximity import proximity_band, direction_from_bbox
from audio_tts import speak
from hazard import scene_has_immediate_hazard

class CameraLoop(threading.Thread):
    def __init__(self, scene):
        super().__init__(daemon=True)
        self.scene = scene
        self.model = YOLO(MODEL_NAME)
        self.cap = cv2.VideoCapture(1)
        self.running = True
        self.last_infer_t = 0.0
        self.frame = None
        self.last_boxes = []

    def run(self):
        if not self.cap.isOpened():
            print("[Camera] Cannot open camera.")
            return
        print("[Camera] Started. Detecting immediately…")
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                break
            self.frame = frame
            h, w, _ = frame.shape
            now = time.time()
            if (now - self.last_infer_t) >= (1.0 / MAX_FPS):
                self.last_infer_t = now
                res = self.model.predict(frame, imgsz=640, verbose=False)[0]
                objects = []
                boxes_draw = []
                for b, c, conf in zip(res.boxes.xyxy.cpu().numpy(),
                                      res.boxes.cls.cpu().numpy().astype(int),
                                      res.boxes.conf.cpu().numpy()):
                    x1, y1, x2, y2 = map(int, b)
                    name = normalize_label(coco_name(c))
                    center = ((x1 + x2)//2, (y1 + y2)//2)
                    dist_m = estimate_distance_m((x1, y1, x2, y2), h, name)
                    direction = direction_from_bbox((x1, y1, x2, y2), w)
                    obj = {
                        "label": name,
                        "distance_m": float(dist_m),
                        "center": center,
                        "bbox": (x1, y1, x2, y2),
                        "direction": direction,
                    }
                    objects.append(obj)
                    band = proximity_band(dist_m)
                    boxes_draw.append((x1, y1, x2, y2, name, float(conf), band, direction))

                self.scene.set_last(objects)
                self.last_boxes = boxes_draw

                scene = {"timestamp": int(time.time()), "environment": "unknown",
                        "objects": [{"label": o["label"],
                                     "distance_m": o["distance_m"]}
                                    | ({"motion": o["motion"]} if "motion" in o else {})
                                    for o in self.scene.last_objects]}
                warn = scene_has_immediate_hazard(scene)
                if warn and (now - self.scene.last_warning_t) > 3.0:
                    self.scene.last_warning_t = now
                    speak(warn)

            overlay = self.draw_overlay()
            cv2.imshow("Visual Assistant — Laptop", overlay)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
        self.cap.release()
        cv2.destroyAllWindows()

    def draw_overlay(self):
        frame = self.frame
        if frame is None:
            return np.zeros((480, 640, 3), dtype=np.uint8)
        overlay = frame.copy()
        for (x1, y1, x2, y2, name, conf, band, direction) in self.last_boxes or []:
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{name} {conf:.2f} ({band}, {direction})"
            cv2.putText(overlay, label, (x1, max(20, y1-6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,0), 2)
        return overlay
