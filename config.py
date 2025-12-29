# Central configuration constants (extracted from desktop_app.py)
MODEL_NAME = "yolov8n.pt"
MAX_FPS = 4
ROLLING_WINDOW_SEC = 4.0
ADVICE_INTERVAL = 2.0  # not auto-asking; used for hazard checks pacing
HAZARD_DISTANCE_M = 6.0

# STT settings
FS = 44100
MAX_RECORD_SEC = 8  # cap for press-hold
