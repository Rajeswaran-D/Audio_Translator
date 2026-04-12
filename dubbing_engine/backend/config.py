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

# Translation Method Configuration
# Options:
#   "seamless" - SeamlessM4T speech-to-speech (best quality, requires installation)
#   "enhanced" - TTS with prosody enhancement (good quality, no extra deps)
#   "standard" - Original TTS + time-stretching (fast but lower quality)
TRANSLATION_METHOD = "enhanced"  # Change to "seamless" if installed

# Prosody Enhancement Settings
USE_PROSODY_ENHANCEMENT = True  # Apply original audio characteristics to TTS
USE_PITCH_CONTOUR = True  # Apply original pitch characteristics
USE_ENERGY_ENVELOPE = True  # Apply original energy dynamics

# Seamless M4T Settings (if installed)
SEAMLESS_MODEL = "seamless_v2"  # or "seamless_v1"
SEAMLESS_USE_GPU = True  # Use GPU if available

# Language Code Mapping for SeamlessM4T
SEAMLESS_LANG_MAP = {
    "en": "eng",
    "ta": "tam",
    "hi": "hin",
    "te": "tel",
    "ml": "mal",
    "kn": "kan",
}

# Audio Processing Limits
MAX_FILE_SIZE_MB = 500  # Maximum file size in MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
TRANSLATION_RETRY_COUNT = 3
TRANSLATION_RETRY_DELAY = 1  # seconds between retries
TTS_RETRY_COUNT = 2
MIN_SEGMENT_DURATION = 0.3  # seconds

# Default Voice Mapping (Character-based)
# Format: {Gender}_{Age}_{Emotion}
VOICE_MAP = {
    # Male Adult
    "male_adult_neutral": "en-US-AndrewNeural",
    "male_adult_angry": "en-US-AndrewNeural",
    "male_adult_happy": "en-US-AndrewNeural",
    "male_adult_sad": "en-US-AndrewNeural",
    # Female Adult
    "female_adult_neutral": "en-US-AvaNeural",
    "female_adult_angry": "en-US-AvaNeural",
    "female_adult_happy": "en-US-AvaNeural",
    "female_adult_sad": "en-US-AvaNeural",
    # Child
    "child_neutral": "en-US-AnaNeural",
    "child_happy": "en-US-AnaNeural",
    "child_angry": "en-US-AnaNeural",
    "child_sad": "en-US-AnaNeural",
    # Elderly
    "elderly_male_neutral": "en-US-AndrewNeural",
    "elderly_female_neutral": "en-US-AvaNeural",
}

# Target Language Voice Mapping - Tamil
TAMIL_VOICE_MAP = {
    # Male Adult
    "male_adult_neutral": "ta-IN-ValluvarNeural",
    "male_adult_angry": "ta-IN-ValluvarNeural",
    "male_adult_happy": "ta-IN-ValluvarNeural",
    "male_adult_sad": "ta-IN-ValluvarNeural",
    # Female Adult
    "female_adult_neutral": "ta-IN-PallaviNeural",
    "female_adult_angry": "ta-IN-PallaviNeural",
    "female_adult_happy": "ta-IN-PallaviNeural",
    "female_adult_sad": "ta-IN-PallaviNeural",
    # Child
    "child_neutral": "ta-IN-PallaviNeural",
    "child_happy": "ta-IN-PallaviNeural",
    "child_angry": "ta-IN-PallaviNeural",
    "child_sad": "ta-IN-PallaviNeural",
}

# Voice Map Fallbacks and Routing
DEFAULT_VOICE_MAP = {
    "male_adult_neutral": "en-US-AndrewNeural",
    "female_adult_neutral": "en-US-AvaNeural",
}

# Language-specific voice map routing
LANGUAGE_VOICE_MAPS = {
    "en": VOICE_MAP,
    "ta": TAMIL_VOICE_MAP,
    "hi": TAMIL_VOICE_MAP,
    "te": TAMIL_VOICE_MAP,
    "ml": TAMIL_VOICE_MAP,
    "kn": TAMIL_VOICE_MAP,
}
