# Tkinter GUI and LLM integration (logic kept intact)
import time, threading
import tkinter as tk
from tkinter import ttk

from stt_recorder import Recorder
from proximity import proximity_band, path_clear_ahead
from audio_tts import speak

try:
    from ask_groq import ask, humor_allowed  # user's file
except Exception:
    ask = None
    humor_allowed = None

# ---- Color tokens pulled from your image ----
BG = "#ecf3f3"       # app background (mint)
PRIMARY = "#06ba71"  # main green
ACCENT = "#e5c70f"   # yellow highlight
PAPER = "#fdfefe"    # panels / text areas
MUTED = "#abad9b"    # subtle borders
INK = "#1a1a1a"      # text


class AppGUI:
    def __init__(self, root, scene):
        self.root = root
        self.scene = scene
        self.rec = Recorder()
        self.kb = {"rules": [
            # Safety
            "Warn the user if a car, bus, or truck is within 6 meters.",
            "If vehicles are moving nearby, advise waiting until they pass.",
            "If a red traffic light is detected, instruct to wait before crossing.",
            "Always approach stairs or slopes slowly and use caution.",

            # Navigation
            "Encourage using pedestrian crossings when available.",
            "Large vehicles can block visibility; warn the user to be cautious.",
            "Mention obstacles like benches or poles if they are in the path.",

            # Guidance style
            "Keep answers under 2 sentences.",
            "Do not invent objects not detected in the scene.",
            "If unsure, ask for clarification or suggest caution.",
            "Prefer saying 'go straight / turn left / turn right' instead of giving distances."
        ]}
        self._build()

    
    def _build(self):
        self.root.title("Visual Assistant — Laptop")
        self.root.geometry("560x340")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Frame style
        style.configure("App.TFrame", background=BG)

        # Primary button
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 14, "bold"),
            foreground="white",
            background=PRIMARY,
            bordercolor=PRIMARY,
            focusthickness=2,
            focuscolor=ACCENT,
            padding=10
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#05a763"), ("disabled", MUTED)],
            foreground=[("disabled", "#e6e6e6")]
        )

        # Entry style
        style.configure(
            "App.TEntry",
            foreground=INK,
            fieldbackground=PAPER,
            bordercolor=PRIMARY,
            lightcolor=ACCENT,
            darkcolor=PRIMARY,
            insertcolor=INK,
            padding=6
        )

        container = ttk.Frame(self.root, style="App.TFrame")
        container.pack(fill="both", expand=True)

        self.btn = ttk.Button(container, text="🎙️HOLD TO TALK", style="Primary.TButton")
        self.btn.pack(pady=16, padx=20, fill='x')
        self.btn.bind('<ButtonPress-1>', self._on_press)
        self.btn.bind('<ButtonRelease-1>', self._on_release)

        self.entry = ttk.Entry(container, font=("Segoe UI", 12), style="App.TEntry")
        self.entry.pack(pady=8, padx=20, fill='x')
        self.entry.insert(0, "(Optional) Type a question and press Enter…")
        self.entry.bind('<Return>', self._on_enter)

        # Text log uses tk widget, style directly
        self.log = tk.Text(
            container, height=8, font=("Consolas", 11),
            bg=PAPER, fg=INK, insertbackground=INK,
            bd=0, highlightthickness=1, highlightbackground=MUTED
        )
        self.log.pack(pady=8, padx=20, fill='both', expand=True)

        # thin accent bar
        hdr = tk.Frame(container, height=2, bg=ACCENT)
        hdr.pack(fill="x", side="top")

        self._log("Ready. Camera is detecting. Hold the button to ask.")


    def _log(self, s: str):
        self.log.insert('end', s + "\n")
        self.log.see('end')

    def _on_press(self, *_):
        threading.Thread(target=self.rec.start, daemon=True).start()
        self._log("[You] (recording…)")

    def _on_release(self, *_):
        def worker():
            text = self.rec.stop_and_transcribe()
            if text:
                self._log(f"[You] {text}")
                self.ask_and_speak(text)
            else:
                self._log("[STT] Sorry, I didn't catch that.")
        threading.Thread(target=worker, daemon=True).start()

    def _on_enter(self, *_):
        q = self.entry.get().strip()
        if not q or q.startswith("(Optional)"):
            return
        self._log(f"[You] {q}")
        self.entry.delete(0, 'end')
        threading.Thread(target=lambda: self.ask_and_speak(q), daemon=True).start()

    def ask_and_speak(self, question: str):
        latest = self.scene.last_objects
        scene = {
            "timestamp": int(time.time()),
            "environment": "unknown",
            "objects": [
                {
                    "label": o["label"],
                    "proximity": proximity_band(o["distance_m"]),
                    "direction": o.get("direction", "ahead"),
                } for o in latest
            ],
            "path_clear_ahead": path_clear_ahead(latest)
        }

        try:
            if ask is None:
                answer = "Keep a safe distance and move carefully."
            else:
                answer = ask(scene, question, self.kb)
            self._log(f"[Assistant] {answer}")
            speak(answer)
        except Exception as e:
            self._log(f"[LLM error] {e}")
