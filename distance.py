# Distance estimation utilities (unchanged logic)
import math

CAMERA_VERTICAL_FOV_DEG = 49.0  # typical laptop webcam; adjust during calibration
MIN_DISTANCE_M, MAX_DISTANCE_M = 0.5, 30.0

# Typical real-world heights (meters)
CLASS_HEIGHT_M = {
    "person": 1.7,
    "car": 1.5,
    "truck": 3.0,
    "bus": 3.2,
    "bicycle": 1.1,
    "motorcycle": 1.2,
    "traffic_light": 3.0,   # head height, not pole total
    "stop_sign": 0.75,      # sign panel height
    "bench": 0.8,
    # add more if you need
}
DEFAULT_HEIGHT_M = 1.7  # fallback


def estimate_distance_m(bbox, frame_h, label: str, vfov_deg: float = CAMERA_VERTICAL_FOV_DEG):
    """
    Estimate distance from bbox height using pinhole model and class height priors.
    - bbox: (x1, y1, x2, y2) in pixels
    - frame_h: image height in px
    - label: normalized class label ('person', 'car', ...)
    - vfov_deg: camera vertical field of view in degrees
    """
    x1, y1, x2, y2 = bbox
    bbox_h = max(1, (y2 - y1))

    # choose a typical real-world height for the object class
    real_h_m = CLASS_HEIGHT_M.get(label, DEFAULT_HEIGHT_M)

    # focal length in pixels (vertical)
    vfov_rad = math.radians(vfov_deg)
    focal_pixels_v = (frame_h / 2.0) / math.tan(vfov_rad / 2.0)

    # pinhole distance estimate
    d = (real_h_m * focal_pixels_v) / float(bbox_h)

    # clamp to a sane range to avoid wild values from tiny boxes
    d = max(MIN_DISTANCE_M, min(MAX_DISTANCE_M, d))
    return d
