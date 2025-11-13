<div align="center">

# 🌟 NOVA AI

**Your Intelligent VRChat Companion**

[![Discord](https://dcbadge.limes.pink/api/server/KbCqreWX?style=flat)](https://discord.gg/KbCqreWX)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

*Bringing AI-powered conversation and vision to your VRChat experience*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Advanced Features](#-advanced-features)
- [Troubleshooting](#-troubleshooting)
- [Development](#-development)
- [Contributing](#-contributing)
- [Contributors](#-contributors)
- [License](#-license)
- [Support](#-support)

---

## 🎯 Overview

**NOVA AI** (/ˈnōvə/) is an advanced, modular AI companion system designed specifically for VRChat. It provides real-time voice interaction, vision analysis, and intelligent conversation capabilities through seamless OSC integration.

NOVA leverages cutting-edge AI models and technologies to create an immersive, responsive virtual assistant that enhances your VRChat experience with natural language understanding, multilingual support, and context-aware responses.

---

## ✨ Key Features

### 🎤 **Voice & Speech**
- **Real-time Speech Recognition** — Powered by OpenAI Whisper (multiple model sizes available)
- **Natural Text-to-Speech** — High-quality voice synthesis via Edge TTS
- **Multilingual Support** — Communicate in multiple languages seamlessly
- **Voice Activity Detection** — Intelligent audio processing with WebRTC VAD

### 🧠 **AI Intelligence**
- **Advanced Language Model** — Gemini 2.5 Flash integration with Google GenAI SDK
- **Contextual Conversations** — Maintains conversation history and context
- **Customizable Personalities** — Define AI behavior through prompt engineering
- **Streaming Responses** — Real-time AI response generation

### 👁️ **Vision Capabilities**
- **VRChat Scene Analysis** — Optional vision system for environmental awareness
- **Continuous Monitoring** — Asynchronous screenshot analysis
- **Context-Aware Responses** — AI incorporates visual information into conversations
- **Configurable Analysis Intervals** — Balance between responsiveness and performance

### 🔗 **VRChat Integration**
- **OSC Protocol Support** — Direct communication with VRChat
- **Typing Indicators** — Visual feedback for AI thinking/listening states
- **Status Messages** — In-game status updates
- **VRChat API Integration** — Optional friend request management and notifications

### 🛠️ **Developer-Friendly**
- **Modular Architecture** — Clean separation of concerns with adapter pattern
- **Extensible Design** — Easy to add new features and integrations
- **Comprehensive Logging** — Detailed error tracking and debugging
- **Type Hints & Documentation** — Well-documented codebase

---

## 🏗️ Architecture

NOVA follows a modular, adapter-based architecture for maximum flexibility and maintainability:

```
┌─────────────────────────────────────────────────┐
│                   main.py                       │
│              (Application Entry)                │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│                  nova.py                        │
│            (Core Logic & Loop)                  │
└─┬───────┬────────┬──────────┬──────────┬───────┘
  │       │        │          │          │
  │   ┌───▼──┐ ┌──▼───┐  ┌───▼────┐ ┌──▼──────┐
  │   │ OSC  │ │ STT  │  │  LLM   │ │  TTS    │
  │   │      │ │      │  │        │ │         │
  │   └──────┘ └──────┘  └────────┘ └─────────┘
  │
┌─▼────────────────────────────────────────────┐
│          classes/adapters.py                 │
│      (Dependency Injection Layer)            │
└─┬─────────┬──────────┬──────────┬───────────┘
  │         │          │          │
┌─▼──────┐ ┌▼────────┐ ┌▼────────┐ ┌▼──────────┐
│  OSC   │ │Whisper  │ │ GenAI  │ │Vision Mgr │
│ Module │ │  STT    │ │ Client │ │  System   │
└────────┘ └─────────┘ └─────────┘ └───────────┘
```

**Key Components:**

- **`main.py`** — Application entry point, initializes OSC and VRChat API
- **`nova.py`** — Core conversation loop, manages AI interactions
- **`constants.py`** — Centralized configuration management
- **`classes/adapters.py`** — Dependency injection and component initialization
- **`classes/osc.py`** — VRChat OSC communication handler
- **`classes/speech_to_text.py`** — Whisper transcription system
- **`classes/edge_tts.py`** — Text-to-speech synthesis and audio playback
- **`classes/vision_manager.py`** — Vision system coordination
- **`classes/system_prompt.py`** — Dynamic prompt loading and management
- **`classes/json_wrapper.py`** — JSON persistence utilities

---

## 📦 Prerequisites

### System Requirements
- **Operating System:** Windows 10/11 (primary support), Linux/macOS (experimental)
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum (8GB+ recommended for larger Whisper models)
- **Storage:** 2GB+ free space for models and dependencies

### Required Software
- **Python 3.8+** — [Download](https://www.python.org/downloads/)
- **FFmpeg** — [Download](https://ffmpeg.org/download.html) (required for audio processing)
- **VRChat** — With OSC enabled
- **Virtual Audio Cable** (optional) — [VB-Audio Cable](https://vb-audio.com/Cable/) for advanced audio routing

### API Keys
- **Google GenAI API Key** — [Get API Key](https://ai.google.dev/)
- **Together AI API Key** (optional) — For alternative models or vision features

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/S0L0GUY/NOVA-AI.git
cd NOVA-AI
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install FFmpeg

**Windows:**
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your system PATH

**Linux:**
```bash
sudo apt-get install ffmpeg  # Debian/Ubuntu
sudo yum install ffmpeg      # CentOS/RHEL
```

**macOS:**
```bash
brew install ffmpeg
```

### 5. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your favorite editor
# Set your API keys:
# - LLM_API_KEY=your_google_genai_api_key
# - VISION_API_KEY=your_together_ai_key (optional)
# - VRCHAT credentials (optional, for API features)
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)

```bash
# Required: Google GenAI API Key
LLM_API_KEY=your_google_genai_api_key

# Optional: Together AI for vision (can use same as LLM_API_KEY)
VISION_API_KEY=your_together_ai_api_key

# Optional: VRChat API (for friend requests, notifications)
VRCHAT_EMAIL=your_vrchat_email@example.com
VRCHAT_PASSWORD=your_vrchat_password
```

### Core Settings (`constants.py`)

#### Language Model Configuration
```python
class LanguageModel:
    MODEL_ID = "gemini-2.5-flash"  # Default Gemini model
```

#### Audio Device Configuration
```python
class Audio:
    AUDIO_OUTPUT_INDEX = 8  # Output device index
    AUDIO_INPUT_INDEX = 4   # Input device index
```

**To find your audio device indices:**
```bash
python list_audio_devices.py
```

#### Speech Recognition Settings
```python
class SpeechRecognitionConfig:
    MODEL_SIZE = "base"           # Whisper model: tiny|base|small|medium|large
    VAD_AGGRESSIVENESS = 1        # Voice detection sensitivity (0-3)
    MAX_RECORDING_DURATION = 30   # Maximum seconds per recording
    QUEUED_MODEL = "genai"        # Transcription model: whisper|genai
```

#### Voice Configuration
```python
class Voice:
    VOICE_NAME = "en-US-EmmaMultilingualNeural"  # Edge TTS voice
```

**Available voices:** See [Microsoft Edge TTS documentation](https://speech.microsoft.com/portal/voicegallery)

#### Network Settings
```python
class Network:
    VRC_PORT = 9000  # VRChat OSC port (default: 9000)
```

#### Vision System (Optional)
```python
class VisionSystem:
    ENABLED = False              # Enable/disable vision features
    ANALYSIS_INTERVAL = 60       # Seconds between analyses
    MAX_IMAGE_SIZE = 1024        # Maximum image dimension
    VISION_MODEL = "meta-llama/Llama-Vision-Free"
```

### Personality Customization

Edit prompt files to customize NOVA's personality and behavior:

- **`prompts/normal_system_prompt.txt`** — Base personality and instructions
- **`prompts/vision_prompt.txt`** — Vision analysis instructions

---

## 🎮 Usage

### Basic Usage

1. **Enable OSC in VRChat:**
   - Launch VRChat
   - Go to Settings → OSC → Enable OSC

2. **Start NOVA:**
   ```bash
   python main.py
   ```

3. **Interact:**
   - NOVA will display "Listening" when ready for input
   - Speak into your microphone
   - NOVA processes your speech and responds
   - Status updates appear in VRChat via OSC

### Status Indicators

- 🟢 **"Listening"** — Ready for voice input
- 🟡 **"Thinking"** — Processing your request
- 🔵 **"[VISION]"** — Vision system update (if enabled)

### Command Line Tools

**List Audio Devices:**
```bash
python list_audio_devices.py
```

**Test Smoke Test:**
```bash
python smoke_test.py
```

**Commit History:**
```bash
python commit_history.py
```

---

## 🔧 Advanced Features

### Virtual Audio Routing

For advanced audio setups with virtual cables:

1. Install [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
2. Configure audio routing:
   - Set VRChat output to Virtual Cable Input
   - Set NOVA input to Virtual Cable Output
3. Update `constants.py`:
   ```python
   class Audio:
       AUDIO_OUTPUT_INDEX = <virtual_cable_input_index>
       AUDIO_INPUT_INDEX = <virtual_cable_output_index>
   ```

### Vision System Setup

Enable real-time vision analysis:

1. Set up Together AI API key in `.env`
2. Enable in `constants.py`:
   ```python
   class VisionSystem:
       ENABLED = True
       ANALYSIS_INTERVAL = 60  # Adjust as needed
   ```
3. Restart NOVA

### VRChat API Integration

Enable friend request auto-accept and notifications:

1. Configure VRChat credentials in `.env`
2. Enable in `constants.py`:
   ```python
   class VRChatAPI:
       USING_API = True
       AUTO_ACCEPT_FRIEND_REQUESTS = True
       ENABLE_NOTIFICATION_CHECKS = True
   ```

### Multi-Instance Setup

Run multiple NOVA instances simultaneously:

1. Create separate project directories
2. Assign unique OSC ports in each `constants.py`:
   ```python
   class Network:
       VRC_PORT = 9001  # Instance 1
       # VRC_PORT = 9002  # Instance 2, etc.
   ```
3. Configure VRChat to use corresponding ports

---

## 🔍 Troubleshooting

### Common Issues

#### No Module Found Error
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### API Authentication Error
- Verify `LLM_API_KEY` is correctly set in `.env`
- Check API key validity at your provider's dashboard
- Ensure no extra spaces or quotes in `.env` file

#### Microphone Not Detected
1. Run `python list_audio_devices.py`
2. Update `AUDIO_INPUT_INDEX` in `constants.py`
3. Check Windows microphone permissions (Settings → Privacy → Microphone)
4. Verify microphone is set as default recording device

#### FFmpeg Warnings/Errors
- Ensure FFmpeg is installed and in system PATH
- Test by running `ffmpeg -version` in terminal
- Reinstall FFmpeg if needed

#### VRChat OSC Not Working
- Enable OSC in VRChat settings
- Verify VRChat is running before starting NOVA
- Check `VRC_PORT` matches VRChat's OSC port (default: 9000)
- Disable firewall temporarily to test
- Check console for OSC connection messages

#### Poor Speech Recognition
- Try larger Whisper model: `MODEL_SIZE = "medium"` or `"large"`
- Adjust VAD aggressiveness: `VAD_AGGRESSIVENESS = 2`
- Reduce background noise
- Check microphone quality and position

#### TTS/Language Issues
- Verify `VOICE_NAME` is valid Edge TTS voice
- Ensure terminal supports UTF-8 encoding
- Test with different voice (e.g., `"en-US-JennyNeural"`)

#### Vision System Not Working
- Ensure `VISION_API_KEY` is set in `.env`
- Verify Together AI API key is valid
- Check `VisionSystem.ENABLED = True`
- Confirm VRChat window is visible on screen

### Debugging Tips

1. **Check Console Output:** NOVA provides detailed error messages
2. **Test Components Individually:**
   ```bash
   python list_audio_devices.py  # Test audio setup
   python smoke_test.py          # Test basic functionality
   ```
3. **Verify Configuration:**
   - Review `constants.py` for syntax errors
   - Confirm `.env` file exists and is properly formatted
4. **Enable Verbose Logging:**
   ```python
   # In main.py, change logging level
   logging.basicConfig(level=logging.DEBUG)
   ```

---

## 💻 Development

### Project Structure

```
NOVA-AI/
├── classes/              # Core modules
│   ├── adapters.py      # Dependency injection
│   ├── osc.py           # VRChat OSC
│   ├── speech_to_text.py # Whisper transcription
│   ├── edge_tts.py      # Text-to-speech
│   ├── vision_manager.py # Vision coordination
│   ├── system_prompt.py  # Prompt management
│   └── ...
├── prompts/             # AI personality prompts
├── json_files/          # Runtime data storage
├── main.py              # Application entry
├── nova.py              # Core logic loop
├── constants.py         # Configuration
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

### Code Style

NOVA follows **PEP 8** Python style guidelines:

- Line length: 127 characters (configured in `pyproject.toml`)
- Format code with **Black** and **isort**
- Lint with **Flake8** and **Pylint**

**Run linters:**
```bash
flake8 .
pylint *.py classes/*.py
```

### Adding New Features

1. **Create feature module** in `classes/`
2. **Add adapter method** in `classes/adapters.py`
3. **Update constants** if configuration needed
4. **Integrate into** `nova.py` main loop
5. **Document changes** in code and README
6. **Test thoroughly** before committing

### Testing

```bash
# Run smoke tests
python smoke_test.py

# Test audio devices
python list_audio_devices.py
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### Contribution Workflow

1. **Fork the Repository**
   ```bash
   # Click "Fork" on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/NOVA-AI.git
   cd NOVA-AI
   ```

2. **Create a Feature Branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make Your Changes**
   - Write clean, documented code
   - Follow PEP 8 style guidelines
   - Add tests if applicable

4. **Test Your Changes**
   ```bash
   python smoke_test.py
   flake8 .
   ```

5. **Commit and Push**
   ```bash
   git add .
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**
   - Describe your changes clearly
   - Reference any related issues
   - Wait for review and feedback

### Contribution Guidelines

- **Code Quality:** Follow PEP 8, add type hints, document functions
- **Testing:** Test your changes thoroughly before submitting
- **Documentation:** Update README and docstrings as needed
- **Commit Messages:** Use clear, descriptive commit messages
- **Issue First:** For major changes, open an issue first to discuss

### Areas for Contribution

- 🐛 Bug fixes and stability improvements
- ✨ New features and integrations
- 📚 Documentation enhancements
- 🧪 Test coverage expansion
- 🌍 Internationalization support
- 🎨 UI/UX improvements for tools

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 👥 Contributors

We're grateful to our amazing contributors:

- **Evan Grinnell** — Project Lead & Core Developer
- **Duck Song** — Core Contributor
- **Viscrimson** — Core Contributor

*Want to see your name here? [Contribute](#-contributing) to NOVA!*

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

**TL;DR:** You're free to use, modify, and distribute this software. Just include the original license and copyright notice.

---

## 💬 Support

### Get Help

- 💬 **Discord:** Join our community at [discord.gg/KbCqreWX](https://discord.gg/KbCqreWX)
- 🐛 **Issues:** Report bugs on [GitHub Issues](https://github.com/S0L0GUY/NOVA-AI/issues)
- 💡 **Feature Requests:** Suggest improvements via GitHub Issues
- 📖 **Documentation:** Read this README and inline code documentation

### Show Your Support

If you find NOVA helpful:

- ⭐ **Star the repository** on GitHub
- 🐦 **Share** your experience on social media
- 🤝 **Contribute** code, documentation, or ideas
- 💬 **Help others** in our Discord community

---

<div align="center">

**Built with ❤️ by the NOVA AI team**

[Discord](https://discord.gg/KbCqreWX) • [GitHub](https://github.com/S0L0GUY/NOVA-AI) • [Issues](https://github.com/S0L0GUY/NOVA-AI/issues)

</div>
