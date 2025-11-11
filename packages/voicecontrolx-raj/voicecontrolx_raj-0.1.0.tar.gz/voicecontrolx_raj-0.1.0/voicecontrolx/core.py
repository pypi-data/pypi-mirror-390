import speech_recognition as sr
import pyttsx3
from voicecontrolx.actions import open_application, tell_time, take_screenshot, lock_pc
from vosk import Model, KaldiRecognizer
import sounddevice as sd
import json

def listen_offline():
    """Offline speech recognition using Vosk model."""
    model_path = "vosk-model-small-en-us-0.15"
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    print("🎤 [Offline] Listening... speak now!")

    # Record from mic for 5 seconds
    duration = 5  # seconds
    audio = sd.rec(int(duration * 16000), samplerate=16000, channels=1, dtype='int16')
    sd.wait()

    if recognizer.AcceptWaveform(audio.tobytes()):
        result = json.loads(recognizer.Result())
        text = result.get("text", "")
        print(f"✅ You said (offline): {text}")
        return text.lower()
    else:
        print("❌ Could not recognize speech.")
        return None


def speak(text):
    """Convert text to speech using pyttsx3 (offline)."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def listen_once():
    """Listen to the microphone and return recognized text."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Listening... please speak now!")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"✅ You said: {text}")
        return text.lower()
    except sr.UnknownValueError:
        print("❌ Sorry, I couldn't understand that.")
        speak("Sorry, I couldn't understand that.")
        return None
    except sr.RequestError:
        print("⚠️ Network error.")
        speak("Network error occurred.")
        return None

def handle_command(command):
    """Understand what the user said and take action."""
    if not command:
        return

    if "open" in command:
        response = open_application(command)
    elif "time" in command:
        response = tell_time()
    elif "screenshot" in command:
        response = take_screenshot()
    elif "lock" in command:
        response = lock_pc()
    elif "exit" in command or "stop" in command:
        response = "Goodbye!"
        speak(response)
        exit()
    else:
        response = "I didn’t understand that command."

    print(f"🤖 {response}")
    speak(response)
