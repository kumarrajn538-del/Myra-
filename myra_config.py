import os

# === CAMERA SETTINGS ===
CAMERA_IP = "192.168.1.111:8080"

# === GEMINI API ===
GEMINI_API_KEY = "AIzaSyArbnraHvbgpbA83KVqGUwddkesvh-JpE0"
PREFERRED_MODEL = "gemini-2.0-flash"

# === VOICE SETTINGS ===
VOICE_LANG = "hi-IN-SwaraNeural"
VOICE_SPEED = 1.0
VOICE_OUTPUT_FILE = "myra_voice.mp3"

# === COLORS ===
C_CYAN_BRIGHT = (50, 255, 255)
C_CYAN_DIM = (0, 180, 200)
C_ORANGE = (255, 140, 0)
C_RED = (255, 50, 50)
C_BLUE_LINE = (0, 100, 200)
C_BLUE_BG = (2, 8, 20)
WHITE = (255, 255, 255)

# === QUOTA MANAGEMENT ===
API_KEYS = [
    "AIzaSyArbnraHvbgpbA83KVqGUwddkesvh-JpE0",
]

MAX_MESSAGES_PER_KEY = 50
QUOTA_CHECK_INTERVAL = 60

# === MEMORY SETTINGS ===
CHAT_HISTORY_FILE = "myra_chat_history.json"
MAX_HISTORY_SIZE = 100

# === DIALOGUES ===
DIALOGUES = {
    "missing_1": "बॉस कहाँ गए? काम कौन करेगा?",
    "missing_2": "वापस आओ वरना स्क्रीन ऑफ कर दूंगी!",
    "shutdown": "सिस्टम शट डाउन। बाय बॉस।",
    "touch": "वार्निंग! मेरे सिस्टम को हाथ मत लगाओ।",
    "who": "स्कैनिंग... पहचान नहीं मिली। आप कौन हैं?",
    "welcome": "वेलकम बैक बॉस। चलिए पैसे कमाते हैं।",
    "cigarette": "सिगरेट पीते हो? सुधर जाओ!"
}

APP_NAME = "MYRA AI"
APP_VERSION = "V55"
DEVELOPER = "NIRAJ INDUSTRIES"
