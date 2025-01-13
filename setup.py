from setuptools import setup

APP = ['face_gesture.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'packages': ['cv2', 'mediapipe', 'pyautogui', 'osascript'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
