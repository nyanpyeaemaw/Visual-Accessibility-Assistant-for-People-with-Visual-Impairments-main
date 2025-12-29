# Immediate hazard logic (unchanged logic)
from proximity import proximity_band
from config import HAZARD_DISTANCE_M

HAZARD_CLASSES = {"car", "truck", "bus"}

def scene_has_immediate_hazard(scene):
    for o in scene.get("objects", []):
        lab = o.get("label")
        dist = o.get("distance_m", 99)
        mot = o.get("motion")
        if lab in HAZARD_CLASSES and dist <= HAZARD_DISTANCE_M:
            band = proximity_band(dist)
            if o.get("direction") == "ahead":
                return "Warning: vehicle ahead, very close. Please wait." if band == "near" else "Warning: vehicle ahead. Please wait."
            else:
                return "Warning: vehicle nearby. Be cautious."
        if lab == "stairs" and dist <= 3:
            return "Stairs ahead. Slow down and feel for the edge."
        if lab == "traffic_light" and o.get("state") == "red":
            return "Red light. Do not cross."
    return None
