# Press-and-hold recorder (unchanged logic)
import time
import sounddevice as sd
import wavio
import speech_recognition as sr

from config import FS, MAX_RECORD_SEC

class Recorder:
    def __init__(self):
        self._rec = None
        self._start_t = None
        self.recording = False

    def start(self):
        if self.recording:
            return
        self.recording = True
        self._start_t = time.time()
        self._rec = sd.rec(int(MAX_RECORD_SEC * FS), samplerate=FS, channels=1)
        print("[STT] Recording… hold the button")

    def stop_and_transcribe(self):
        if not self.recording:
            return ""
        elapsed = time.time() - self._start_t
        sd.stop()
        self.recording = False
        # Trim to actual length
        frames = int(min(elapsed, MAX_RECORD_SEC) * FS)
        audio = self._rec[:frames]
        # Save WAV
        wavio.write("output.wav", audio, FS, sampwidth=2)
        print("[STT] Saved output.wav; transcribing…")
        # Transcribe using speech_recognition
        r = sr.Recognizer()
        with sr.AudioFile("output.wav") as source:
            audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data)
            print("[STT] Text:", text)
            return text
        except sr.UnknownValueError:
            print("[STT] Could not understand audio.")
            return ""
        except sr.RequestError as e:
            print(f"[STT] Request error: {e}")
            return ""
