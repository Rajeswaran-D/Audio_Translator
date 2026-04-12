# 🎬 Audio Translator & Dubbing Engine

A professional-grade **Multi-Language Audio Dubbing Platform** that automatically transcribes, translates, and synthesizes audio in multiple languages. Supports both speech and songs with intelligent vocal separation, emotion-aware voice synthesis, and interactive lyrics editing.

---

## ✨ Key Features

### 🌍 Multi-Language Support
- **Supported Languages**: Tamil (தமிழ்), Telugu (తెలుగు), Hindi (हिंदी), English (English)
- Automatic language detection from audio using OpenAI Whisper
- Seamless word-by-word translation with context preservation

### 🎵 Intelligent Audio Processing
- **Dual Pipeline Architecture**:
  - 🎤 **Speech Mode**: Direct transcription and translation
  - 🎵 **Song Mode**: Vocal separation → transcription → translation → vocal remixing
- **Vocal Isolation**: Uses Meta's Demucs for professional-grade instrument/vocal separation
- **Gap Filling**: Automatically detects and preserves instrumental sections

### 🎭 Emotion-Aware Voice Synthesis
- Automatic emotion detection from original audio
- **Voice Profiles** with gender and age group selection
- Azure Cognitive Services Edge TTS for natural-sounding output
- MP3 format support for maximum compatibility

### ✏️ Interactive Lyrics Editing
- View original and translated text
- Edit translated text per segment
- Change voice characteristics (gender, age group)
- Regenerate individual segments or rebuild complete audio
- Embedded editor in main web interface

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (tested on 3.9)
- FFmpeg (for audio processing)
- pip or conda

### Installation

1. **Navigate to project directory**
   ```bash
   cd Audio_Translator/dubbing_engine
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```
   Server will start at: `http://localhost:8000`

---

## 📖 Usage Guide

### Web Interface

1. **Upload Audio**
   - Drag & drop audio file or click to browse
   - Select target language from dropdown
   - Supported formats: MP3, WAV, FLAC, OGG, M4A

2. **Processing**
   - Application detects speech vs. song automatically
   - Transcription, translation, and synthesis happen automatically
   - Progress updates shown in real-time

3. **Review Results**
   - Play dubbed audio
   - Download translated audio file
   - View segment metadata

4. **Edit & Customize**
   - Click **"Edit Segments"** tab
   - Modify translated text for individual segments
   - Change voice (gender, age group)
   - **Save Text** or **Regenerate Audio** per segment
   - **Rebuild Audio** to apply all changes

---

## 🏗️ Architecture

### System Overview
- **Frontend**: HTML/CSS/JavaScript
- **Backend**: FastAPI (Python)
- **Speech-to-Text**: OpenAI Whisper
- **Translation**: Google Translate API
- **Text-to-Speech**: Azure Cognitive Services
- **Vocal Separation**: Meta Demucs
- **Audio Processing**: librosa, pydub

### Core Modules

| Module | Purpose |
|--------|---------|
| `main.py` | FastAPI application and routes |
| `manager.py` | Pipeline orchestration |
| `stt.py` | Whisper speech recognition |
| `translator.py` | Text translation |
| `tts.py` | Azure text-to-speech |
| `emotion.py` | Emotion detection |
| `vocal_separator.py` | Demucs vocal isolation |
| `audio_utils.py` | Audio utilities |

---

## 🛠️ Configuration

### Environment Variables
Create `.env` file:

```bash
AZURE_TTS_KEY=your_key
AZURE_TTS_REGION=your_region
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Supported Languages
- `ta` - Tamil (தமிழ்)
- `te` - Telugu (తెలుగు)
- `hi` - Hindi (हिंदी)
- `en` - English

---

## 📊 Performance

### Processing Speed (Approximate)
- **5-minute speech**: 2-3 minutes total
- **5-minute song**: 4-5 minutes (includes vocal separation)
- Transcription: ~1-2 seconds per audio minute
- TTS synthesis: Real-time or faster

### Audio Quality
- **Sample Rate**: 16 kHz
- **Bitrate**: 192 kbps MP3
- **Format**: MP3 (web), WAV (processing)

---

## 🐛 Troubleshooting

### Missing Dependencies
```bash
# Install specific package
pip install torchcodec  # For TorchCodec errors
pip install pyrubberband  # For audio stretching
```

### Demucs Model
First run downloads model (~500MB) automatically. Allow to complete.

### Whisper Model
```bash
python -c "import whisper; whisper.load_model('small')"
```

### Audio Quality Issues
- Audio stretching is disabled (causes degradation)
- Natural timing is used instead
- Segment boundaries may not align perfectly with original

### Half of Song Not Translated
Gap-filling preserves instrumental sections. Check console for gap info.

---

## 📦 Dependencies

Core libraries:
- **FastAPI** - Web framework
- **Whisper** - Speech recognition
- **librosa** - Audio processing
- **Demucs** - Vocal separation
- **google-cloud-translate** - Translation
- **azure-cognitiveservices-speech** - TTS
- **python-multipart** - File uploads
- **python-dotenv** - Environment variables

See `requirements.txt` for complete list and versions.

---

## 🚀 Deployment

### Local Development
```bash
python main.py
# Access at http://localhost:8000
```

### Production (Linux/Mac)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 --timeout 300 backend.main:app
```

---

## 📁 File Structure

```
dubbing_engine/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── manager.py              # Pipeline
│   ├── stt.py                  # Whisper
│   ├── translator.py           # Translation
│   ├── tts.py                  # Azure TTS
│   ├── emotion.py              # Emotion detection
│   ├── vocal_separator.py      # Demucs
│   ├── audio_utils.py          # Utilities
│   ├── config.py               # Settings
│   ├── outputs/                # Generated audio
│   └── uploads/                # Uploaded files
├── index.html                  # Web UI
├── script.js                   # Frontend logic
├── style.css                   # Styling
├── README.md                   # This file
├── .gitignore                  # Git exclusions
├── requirements.txt            # Dependencies
└── main.py                     # Entry point
```

---

## 🤝 Contributing

### Reporting Issues
- Check existing issues first
- Provide audio sample, Python version, full error message
- Include steps to reproduce

### Feature Requests
- Describe use case clearly
- Check for duplicate requests

---

## 📞 Support

- **Issues**: GitHub Issues
- **Email**: Contact project maintainer

---

## 🎯 Roadmap

### Planned Features
- [ ] Real-time streaming audio support
- [ ] Batch processing (multiple files)
- [ ] More language support (20+ languages)
- [ ] Video subtitle generation
- [ ] Performance optimizations

---

**Made with ❤️ for audio professionals and developers**
## AI-Based Multilingual Audio Translation and Dubbing System

This project presents an AI-based system designed to automatically translate spoken audio from one language to another while preserving the natural flow of speech.

The system accepts an input audio file such as a speech recording, dialogue, or movie audio and converts the spoken content into text using advanced speech recognition techniques. The extracted text is then translated into the user’s desired target language using a machine translation model. After translation, the system generates a new audio output using text-to-speech technology, producing a natural-sounding voice in the selected language.

The entire process is integrated into a web-based interface where users can upload an audio file, choose a target language, and receive the translated and synthesized audio output. The backend is implemented using Python and FastAPI, while AI models such as speech recognition and neural translation are used to process and convert the audio.

This system aims to simplify multilingual communication and enable automated dubbing for various types of audio content, including educational materials, podcasts, and entertainment media. By combining speech recognition, language translation, and voice synthesis, the project demonstrates how artificial intelligence can be used to create efficient and accessible multilingual audio conversion systems.

### Features

- **Automatic speech recognition (ASR)**: Convert spoken audio into source-language text.
- **Neural machine translation (NMT)**: Translate extracted text into a target language.
- **Text-to-speech (TTS)**: Generate natural-sounding speech in the translated language.
- **Web-based interface**: Upload audio, select target language, and download translated audio.
- **Scalable backend**: Python + FastAPI architecture suitable for deployment.

### Tech Stack

- **Backend**: Python, FastAPI
- **AI/ML**: Speech recognition, neural machine translation, text-to-speech
- **Audio processing**: Libraries like `pydub` and others as needed

### Project Structure (initial)

- `Audio_translator_model/` – Core audio processing and model-related utilities (e.g., `audio_splitter.py`).
- `README.md` – Project overview and usage.
- `requirements.txt` – Python dependencies (to be expanded as the project grows).

### Getting Started

1. **Create and activate a virtual environment (recommended)**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the FastAPI app (once created)**:

   ```bash
   uvicorn main:app --reload
   ```

### Future Work

- Integrate end-to-end pipeline: ASR → Translation → TTS.
- Build the FastAPI endpoints for uploading audio and returning translated audio.
- Add a frontend for easy interaction.
- Optimize performance for long-form content (lectures, movies, podcasts).

