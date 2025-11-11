# VoiceControlX-Raj

**A local, offline voice assistant for Windows. Control your PC using Python and voice commands.**

---

## Overview

`VoiceControlX-Raj` helps **developers, office users, hobbyists, and accessibility users** automate common tasks on Windows using natural voice commands.  

With just your microphone and a few commands, you can:
- Open **applications** like Chrome, Notepad, Spotify, Calculator, YouTube  
- Take **screenshots**  
- Check **current system time**  
- **Lock your PC**  
- Create **custom commands** via a JSON configuration  
- Run **offline** or online voice recognition

---

## Why This Project?

I built this library to demonstrate a **real-world voice automation scenario** — controlling Windows PCs hands-free using Python.  

This project demonstrates:
- Python **packaging and CLI development**  
- **Speech recognition** and **text-to-speech** (online & offline)  
- Windows **system automation** using Python  
- Open-source best practices (README, tests, PyPI readiness)  

Great to showcase on a **fresher Python developer or data engineer resume**!

---

## Features

| Category | Feature | Description |
|-----------|----------|-------------|
| **Voice Recognition** | Online Mode | Uses Google Speech API for real-time voice-to-text conversion |
|  | Offline Mode | Uses Vosk to recognize speech fully offline |
| **System Automation** | Open Applications | Launch apps like Chrome, Notepad, Spotify, Calculator, Explorer |
|  | Take Screenshot | Capture your screen and save to Desktop |
|  | Lock PC | Lock Windows machine instantly |
| **Custom Commands** | commands.json | Add personalized commands like "Open YouTube" |
| **CLI Tool** | `voicecontrolx` | Run full voice assistant from the terminal |

---

## Installation

pip install -r requirements.txt
