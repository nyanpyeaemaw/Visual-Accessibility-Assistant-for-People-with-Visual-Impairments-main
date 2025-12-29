# COCO helpers and label normalization (unchanged logic)
COCO_NAMES = None
SAFE_LABEL_MAP = {
    'traffic light': 'traffic_light',
    'stop sign': 'stop_sign',
}

def coco_name(cls_id):
    global COCO_NAMES
    if COCO_NAMES is None:
        COCO_NAMES = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
            'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
            'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
            'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
            'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
            'hair drier', 'toothbrush']
    if 0 <= cls_id < len(COCO_NAMES):
        return COCO_NAMES[cls_id]
    return f"cls_{cls_id}"

def normalize_label(name: str) -> str:
    return SAFE_LABEL_MAP.get(name, name)
