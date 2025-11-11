import os
import queue
import json
import pyttsx3
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import urllib.request
import zipfile
import speech_recognition as sr

# ---------------------
# Global TTS engine
# ---------------------
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech (offline)."""
    engine.say(text)
    engine.runAndWait()

# ---------------------
# Download Vosk model if missing
# ---------------------
def download_vosk_model(model_folder="vosk-model-small-en-us-0.15"):
    if not os.path.exists(model_folder):
        print("Downloading Vosk model (~50 MB)...")
        url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
        urllib.request.urlretrieve(url, "vosk_model.zip")
        with zipfile.ZipFile("vosk_model.zip", "r") as zip_ref:
            zip_ref.extractall(".")
        os.remove("vosk_model.zip")
        print("Model downloaded successfully!")
    return model_folder

# ---------------------
# Offline listening (Vosk)
# ---------------------
def listen_offline(model_folder=None, duration=5):
    """Offline speech recognition using Vosk."""
    if model_folder is None:
        model_folder = download_vosk_model()

    if not os.path.exists(model_folder):
        raise FileNotFoundError(f"Vosk model folder not found: {model_folder}")

    model = Model(model_folder)
    recognizer = KaldiRecognizer(model, 16000)
    q = queue.Queue()

    def callback(indata, frames, time, status):
        if status:
            print(status, flush=True)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print("🎤 Listening offline...")
        data = b""
        for _ in range(int(duration * 1000 / 40)):
            data += q.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                return result.get("text", "")
        final_result = json.loads(recognizer.FinalResult())
        return final_result.get("text", "")

# ---------------------
# Online listening (Google)
# ---------------------
def listen_once():
    """Online listening using Google Speech Recognition"""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Listening (online)...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return None
    except sr.RequestError:
        print("⚠️ Network error")
        return None
