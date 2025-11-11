import os
import datetime
import pyautogui

def open_application(command):
    """Open common Windows applications."""
    if "chrome" in command:
        os.system("start chrome")
        return "Opening Chrome"
    elif "notepad" in command:
        os.system("start notepad")
        return "Opening Notepad"
    elif "calculator" in command:
        os.system("start calc")
        return "Opening Calculator"
    else:
        return "Application not found"

def tell_time():
    now = datetime.datetime.now().strftime("%H:%M")
    return f"The current time is {now}"

def take_screenshot():
    screenshot = pyautogui.screenshot()
    filename = "screenshot.png"
    screenshot.save(filename)
    return f"Screenshot saved as {filename}"

def lock_pc():
    os.system("rundll32.exe user32.dll,LockWorkStation")
    return "PC locked"
