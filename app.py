# Entry point that wires all modules — behavior equivalent to desktop_app.py
import time
import tkinter as tk

from config import ROLLING_WINDOW_SEC
from scene import RollingScene
from camera_loop import CameraLoop
from gui import AppGUI

def main():
    scene = RollingScene(window_sec=ROLLING_WINDOW_SEC)
    cam = CameraLoop(scene)
    cam.start()

    root = tk.Tk()
    gui = AppGUI(root, scene)

    try:
        root.mainloop()
    finally:
        cam.running = False
        cam.join(timeout=1.0)

if __name__ == '__main__':
    main()
