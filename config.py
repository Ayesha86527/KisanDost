import os
from pathlib import Path

# ==========================
# 🔐 API KEYS
# ==========================
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# app/config.py
from dotenv import load_dotenv
import os

# Load .env automatically
load_dotenv()

# Get API keys from environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_LANGUAGE = "en"  # optional, for voice/ocr modules
WHISPER_MODEL = "base"    # optional
TTS_PREFIX = "tts_"       # optional
OUTPUT_DIRS = "output"    # optional

# Optional: sanity check
print("Loaded API keys:")
print("TAVILY_API_KEY:", TAVILY_API_KEY)
print("GROQ_API_KEY:", GROQ_API_KEY)


if not GROQ_API_KEY:
    print("⚠️ [Warning] GROQ_API_KEY not set. Please add it to your environment variables.")

# ==========================
# 🌐 SUPPORTED LANGUAGES
# ==========================
LANGUAGES = {
    "en": "English",
    "ur": "Urdu",
    "sd": "Sindhi"
}

DEFAULT_LANGUAGE = "en"

# ==========================
# 📁 OUTPUT DIRECTORIES
# ==========================
BASE_OUTPUT = Path("outputs")

OUTPUT_DIRS = {
    "voice_outputs": BASE_OUTPUT / "voice_outputs",
    "transcripts": BASE_OUTPUT / "transcripts",
    "recordings": BASE_OUTPUT / "recordings",
    "ocr_outputs": BASE_OUTPUT / "ocr"
}

# Ensure directories exist
for path in OUTPUT_DIRS.values():
    path.mkdir(parents=True, exist_ok=True)

# ==========================
# 🧠 MODEL SETTINGS
# ==========================
OCR_LANG = "en"                 # PaddleOCR language (en, ur, multilang)
WHISPER_MODEL = "base"          # Whisper ASR model (tiny, base, small, medium, large)
GROQ_MODEL = "llama-3.1-70b-versatile"  # Chat model
MAX_TOKENS = 1500               # Max token limit for responses

# ==========================
# 🔊 VOICE / TTS SETTINGS
# ==========================
TTS_PREFIX = "response"         # Default prefix for TTS files
TTS_SPEED = False               # False = normal, True = slow voice

# ==========================
# 🧩 APP SETTINGS
# ==========================
DEBUG = True                    # Enable for verbose logs (set False in production)
