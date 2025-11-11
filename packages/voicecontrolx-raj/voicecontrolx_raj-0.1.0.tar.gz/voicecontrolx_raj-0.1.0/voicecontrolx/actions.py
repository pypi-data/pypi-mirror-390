import os
import datetime
import pyautogui
import subprocess
import json
import os

def load_custom_commands():
    """Load custom commands from commands.json file."""
    try:
        with open("commands.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def open_application(app_name):
    """Open apps using predefined or custom commands."""
    app_name = app_name.lower()
    custom_cmds = load_custom_commands()

    # Check custom commands first
    for trigger, cmd in custom_cmds.items():
        if trigger in app_name:
            os.system(cmd)
            return f"Executing custom command: {trigger}"

    # Default known apps
    if "chrome" in app_name:
        os.system("start chrome")
        return "Opening Google Chrome"
    elif "notepad" in app_name:
        os.system("start notepad")
        return "Opening Notepad"
    elif "explorer" in app_name or "folder" in app_name:
        os.system("explorer")
        return "Opening File Explorer"
    else:
        return f"Sorry, I don't know how to open {app_name}"


def tell_time():
    """Return the current system time."""
    now = datetime.datetime.now().strftime("%I:%M %p")
    return f"The time is {now}"

def take_screenshot():
    """Take a screenshot and save to Desktop."""
    path = os.path.expanduser("~/Desktop/screenshot.png")
    pyautogui.screenshot(path)
    return f"Screenshot saved to Desktop"

def lock_pc():
    """Lock the Windows system."""
    subprocess.run("rundll32.exe user32.dll,LockWorkStation")
    return "Locking the system"
