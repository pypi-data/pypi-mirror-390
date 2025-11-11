import os
import json
from voicecontrolx.core import listen_offline, speak, download_vosk_model
from voicecontrolx.actions import open_application, tell_time, take_screenshot, lock_pc

# Ensure Vosk model exists
model_path = download_vosk_model()

# Load commands.json
def load_commands():
    try:
        with open("commands.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("commands.json not found! Using default commands.")
        return {}

custom_commands = load_commands()

def handle_command(command):
    if not command:
        return

    command = command.lower()
    for trigger, system_cmd in custom_commands.items():
        if trigger in command:
            os.system(system_cmd)
            speak(f"Executing: {trigger}")
            return

    # Default actions
    if "open" in command:
        speak(open_application(command))
    elif "time" in command:
        speak(tell_time())
    elif "screenshot" in command:
        speak(take_screenshot())
    elif "lock" in command:
        speak(lock_pc())
    elif "exit" in command or "stop" in command:
        speak("Goodbye!")
        exit()
    else:
        speak("I did not understand that command.")

if __name__ == "__main__":
    speak("Hello! Testing VoiceControlX-Raj offline mode.")
    print("Listening for commands... say 'stop' or 'exit' to quit.")
    while True:
        command = listen_offline(model_path)
        if command:
            print(f"Recognized command: {command}")
            handle_command(command)

