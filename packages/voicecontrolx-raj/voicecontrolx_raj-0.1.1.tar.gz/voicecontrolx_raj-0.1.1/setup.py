from setuptools import setup, find_packages

setup(
    name="voicecontrolx-raj",
    version="0.1.1",
    author="RAJALINGAMT",
    author_email="raju031001@gmail.com",
    description="Offline Windows voice assistant in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/TRajalingam/voicecontrolx-raj",
    packages=find_packages(),
    install_requires=[
        "SpeechRecognition",
        "pyttsx3",
        "pyaudio",
        "pyautogui",
        "vosk",
        "sounddevice"
    ],
    entry_points={
        "console_scripts": [
            "voicecontrolx=voicecontrolx.core:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
        "License :: OSI Approved :: MIT License",
    ],
)