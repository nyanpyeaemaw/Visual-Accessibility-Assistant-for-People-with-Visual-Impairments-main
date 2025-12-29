# gTTS-based speak function (unchanged logic)
import time, sys, os, subprocess
from gtts import gTTS
try:
    from playsound import playsound
except Exception:
    playsound = None


def speak(text: str):
    try:
        audio_path = f"tts_{int(time.time())}.mp3"
        tts = gTTS(text=text, lang='en', tld='com', slow=False)
        tts.save(audio_path)

        # Prefer playsound if available (works on Windows without ffmpeg)
        if playsound is not None:
            playsound(audio_path)
            return

        # Windows fallback: open with default player
        if sys.platform.startswith("win"):
            os.startfile(os.path.abspath(audio_path))
            return

        # macOS fallback: use 'afplay'
        if sys.platform == "darwin":
            subprocess.Popen(["afplay", audio_path])
            return

        # Linux fallback: try 'xdg-open' (opens default player)
        subprocess.Popen(["xdg-open", audio_path])
    except Exception as e:
        print("[TTS error]", e)
