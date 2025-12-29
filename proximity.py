# Proximity and direction utilities (unchanged logic)

def proximity_band(d):
    if d <= 2.0:     # very close
        return "near"
    elif d <= 6.0:   # caution range
        return "medium"
    else:
        return "far"


def direction_from_bbox(bbox, frame_w):
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2.0
    left_edge = frame_w * (1/3)
    right_edge = frame_w * (2/3)
    if cx < left_edge:
        return "left"
    elif cx > right_edge:
        return "right"
    else:
        return "ahead"


# Which objects block walking straight?
BLOCKING_CLASSES = {
    # indoors
    "person","chair","couch","bed","dining table","tv","laptop","monitor","keyboard","mouse","bench","table",
    # outdoor or general obstacles:
    "car","truck","bus","bicycle","motorcycle","stroller","potted plant","trash can","suitcase","backpack","dog"
}


def path_clear_ahead(latest_objects):
    """
    Returns True if no blocking object is 'near' or 'medium' in the AHEAD corridor.
    """
    for o in latest_objects:
        lab = o.get("label","")
        d = float(o.get("distance_m", 99))
        if lab in BLOCKING_CLASSES:
            band = proximity_band(d)
            # Only count things in the center corridor as blocking forward motion
            if o.get("direction") == "ahead" and band in {"near","medium"}:
                return False
    return True
