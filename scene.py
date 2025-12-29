# RollingScene class (latest frame only) — unchanged logic except isolated to its own file
from collections import deque

class RollingScene:
    def __init__(self, window_sec):
        self.window_sec = window_sec
        self.buf = deque(maxlen=200)   # optional; kept for dev
        self.last_warning_t = 0.0
        self.last_objects = []         # latest frame only

    def set_last(self, objects):
        self.last_objects = list(objects)

    # kept for reference/dev — not used by LLM
    def add(self, ts, objects):
        self.buf.append((ts, objects))
        tcut = ts - self.window_sec
        while self.buf and self.buf[0][0] < tcut:
            self.buf.pop()

    def aggregate(self):
        # unchanged from original (not used in main flow)
        import numpy as np
        by_label = {}
        centers_by_label = {}
        for ts, objs in list(self.buf):
            for o in objs:
                lab = o['label']
                d = o.get('distance_m', 9.0)
                if (lab not in by_label) or (d < by_label[lab].get('distance_m', 9.0)):
                    by_label[lab] = {k: o[k] for k in o}
                centers_by_label.setdefault(lab, []).append(o.get('center', (0, 0)))
        for lab, centers in centers_by_label.items():
            if len(centers) >= 2:
                diffs = [np.hypot(centers[i+1][0]-centers[i][0], centers[i+1][1]-centers[i][1]) for i in range(len(centers)-1)]
                moving = np.mean(diffs) > 5.0
                if lab in by_label:
                    by_label[lab]['motion'] = 'moving' if moving else 'static'
        return by_label
