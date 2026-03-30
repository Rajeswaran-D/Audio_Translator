import os

# Base directory for the backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data directories
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure directories exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Audio Settings
SAMPLE_RATE = 16000
CHANNELS = 1

# Supported Languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
    "te": "Telugu",
    "ml": "Malayalam",
    "kn": "Kannada"
}

# Default Voice Mapping (Character-based)
# Format: {Gender}_{Age}_{Tone}
VOICE_MAP = {
    "male_adult_neutral": "en-US-AndrewNeural",
    "male_adult_angry": "en-US-AndrewNeural",
    "male_adult_happy": "en-US-AndrewNeural",
    "female_adult_neutral": "en-US-AvaNeural",
    "female_adult_angry": "en-US-AvaNeural",
    "female_adult_happy": "en-US-AvaNeural",
    "child_neutral": "en-US-AnaNeural",
    "elderly_male_neutral": "en-US-AndrewNeural", # Placeholder, can refine later
}

# Target Language Voice Mapping (Example for Tamil)
TAMIL_VOICE_MAP = {
    "male_adult_neutral": "ta-IN-ValluvarNeural",
    "female_adult_neutral": "ta-IN-PallaviNeural",
}
