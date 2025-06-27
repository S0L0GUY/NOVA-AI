# NOVA AI
### /ˈnōvə/ - Your VRChat AI Companion

NOVA AI is an intelligent VRChat assistant that brings conversational AI directly into your VRChat experience. Using advanced speech recognition, natural language processing, and text-to-speech technology, NOVA can listen to your voice, understand what you're saying, and respond intelligently through VRChat's chatbox.

## Table of Contents
- [What is NOVA AI?](#what-is-nova-ai)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
- [Setup Instructions](#setup-instructions)
- [Configuration](#configuration)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## What is NOVA AI?

NOVA AI is a sophisticated VRChat companion that:
- **Listens** to your voice using advanced speech recognition (OpenAI Whisper)
- **Thinks** using powerful AI language models (OpenAI GPT)
- **Responds** through VRChat's chatbox using OSC (Open Sound Control)
- **Speaks** back to you using text-to-speech technology

Perfect for content creators, VRChat enthusiasts, or anyone who wants an intelligent AI companion in their virtual world!

## Features

- 🎤 **Voice Recognition**: Advanced speech-to-text using OpenAI Whisper
- 🧠 **AI Conversation**: Powered by OpenAI's language models for natural conversations
- 💬 **VRChat Integration**: Seamlessly displays responses in VRChat chatbox via OSC
- 🔊 **Text-to-Speech**: Speaks responses back to you with customizable voices
- 🎚️ **Voice Activity Detection**: Automatically detects when you start and stop speaking
- ⚙️ **Customizable**: Configurable system prompts, voices, and behavior
- 📊 **Resource Monitoring**: Built-in performance monitoring
- 🔧 **Modular Design**: Easy to extend and customize

## Prerequisites

Before installing NOVA AI, you'll need the following on your Windows machine:

### 1. Python 3.8 or Higher
- Download from [python.org](https://www.python.org/downloads/)
- **Important**: During installation, check "Add Python to PATH"
- Verify installation by opening Command Prompt and typing: `python --version`

### 2. Git (Optional but Recommended)
- Download from [git-scm.com](https://git-scm.com/download/win)
- This allows you to easily download and update NOVA AI

### 3. VRChat with OSC Enabled
- Have VRChat installed and an account
- OSC must be enabled in VRChat settings (we'll cover this in setup)

### 4. Audio Setup
- A microphone for voice input
- Audio output device (speakers/headphones)
- **Optional**: Virtual audio cables for advanced audio routing

## Installation Guide

### Step 1: Download NOVA AI

**Option A: Using Git (Recommended)**
1. Open Command Prompt or PowerShell
2. Navigate to where you want to install NOVA AI:
   ```powershell
   cd C:\Users\%USERNAME%\Documents
   ```
3. Clone the repository:
   ```powershell
   git clone https://github.com/S0L0GUY/NOVA-AI.git
   cd NOVA-AI
   ```

**Option B: Manual Download**
1. Go to the [NOVA AI GitHub page](https://github.com/S0L0GUY/NOVA-AI)
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to a folder like `C:\Users\%USERNAME%\Documents\NOVA-AI`

### Step 2: Install Python Dependencies

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the NOVA-AI folder:
   ```powershell
   cd C:\Users\%USERNAME%\Documents\NOVA-AI
   ```
3. Install required packages:
   ```powershell
   pip install -r requirements.txt
   ```

**If you encounter errors**, try:
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Install Additional Dependencies

Some packages may require additional setup:

**For Audio Processing:**
```powershell
pip install pyaudio
```

If PyAudio fails to install:
1. Download the appropriate .whl file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. Install it with: `pip install path\to\downloaded\file.whl`

## Setup Instructions

### Step 1: Configure Audio Devices

1. **Find your audio device indices:**
   ```powershell
   python list_audio_devices.py
   ```
2. Note the index numbers for your microphone (input) and speakers (output)

3. **Edit the constants.py file:**
   - Open `constants.py` in a text editor
   - Update the `AUDIO_INPUT_INDEX` and `AUDIO_OUTPUT_INDEX` values:
   ```python
   class Audio:
       AUDIO_OUTPUT_INDEX = 7  # Replace with your speaker index
       AUDIO_INPUT_INDEX = 2   # Replace with your microphone index
   ```

### Step 2: Set Up OpenAI API

1. **Get an OpenAI API key:**
   - Go to [platform.openai.com](https://platform.openai.com)
   - Create an account or sign in
   - Navigate to API Keys section
   - Create a new API key

2. **Set up your API key:**
   
   **Method 1: Environment Variable (Recommended)**
   - Open Command Prompt as Administrator
   - Run: `setx OPENAI_API_KEY "your-api-key-here"`
   - Restart your computer

   **Method 2: Direct Configuration**
   - Edit the constants.py file and add your API key where needed

### Step 3: Configure VRChat OSC

1. **Enable OSC in VRChat:**
   - Launch VRChat
   - Go to Settings → OSC
   - Enable "Enabled"
   - Note the port number (usually 9000)

2. **Update network settings:**
   - The `constants.py` file should automatically detect your IP
   - Verify the `VRC_PORT` matches VRChat's OSC port

### Step 4: Test Audio Setup

1. **Test your microphone:**
   ```powershell
   python -c "import sounddevice as sd; print('Audio devices:'); print(sd.query_devices())"
   ```

2. **Test text-to-speech:**
   ```powershell
   python list_voices.py
   ```

## Configuration

### Customizing NOVA's Personality

Edit the system prompt files in the `prompts/` folder:
- `normal_system_prompt.txt` - Default personality
- `snapchat_system_prompt.txt` - Alternative personality
- `additional_system_prompt.txt` - Extra instructions

### Adjusting Voice Settings

In `constants.py`, modify the `Voice` class:
```python
class Voice:
    VOICE_NAME = "en-US-JennyNeural"  # Change to your preferred voice
```

### Model Configuration

Adjust AI model settings in the `LanguageModel` class in `constants.py`:
```python
class LanguageModel:
    MODEL_ID = "gpt-3.5-turbo"  # or "gpt-4" for better responses
    LM_TEMPERATURE = 0.7        # Creativity level (0.0-1.0)
```

## Usage

### Starting NOVA AI

1. **Open Command Prompt or PowerShell**
2. **Navigate to NOVA AI folder:**
   ```powershell
   cd C:\Users\%USERNAME%\Documents\NOVA-AI
   ```
3. **Launch VRChat and join a world**
4. **Start NOVA AI:**
   ```powershell
   python main.py
   ```

### Using NOVA AI

1. **Wait for startup**: You'll see colored messages indicating NOVA is loading
2. **Speak clearly**: NOVA will automatically detect when you start speaking
3. **Wait for response**: NOVA will process your speech and respond in VRChat's chatbox
4. **Continue conversation**: NOVA remembers conversation context

### Stopping NOVA AI

- Press `Ctrl+C` in the Command Prompt to stop the program

## Troubleshooting

### Common Issues

**"No module named" errors:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

**Audio device not found:**
- Run `python list_audio_devices.py` to find correct device indices
- Update `constants.py` with correct values

**VRChat not receiving messages:**
- Ensure OSC is enabled in VRChat settings
- Check that VRChat is running and you're in a world
- Verify the port number matches (default 9000)

**OpenAI API errors:**
- Verify your API key is set correctly
- Check your OpenAI account has available credits
- Ensure you have access to the model you're trying to use

**Microphone not working:**
- Check Windows microphone permissions
- Verify the microphone works in other applications
- Try different audio device indices

### Getting Help

1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure your OpenAI API key is valid and has credits
4. Test each component individually using the provided test scripts

## Advanced Setup

### Virtual Audio Cables (Optional)

For advanced audio routing:
1. Install VB-Audio Virtual Cable
2. Configure audio routing through virtual cables
3. Update audio device indices in constants.py

### Custom System Prompts

Create custom personalities by editing files in the `prompts/` directory to change how NOVA behaves and responds.



## Contributing

We welcome contributions from the community! NOVA AI is open-source and benefits from community input.

### How to Contribute

1. **Fork the repository** on GitHub
2. **Create a new branch** for your feature:
   ```powershell
   git checkout -b feature-name
   ```
3. **Make your changes** and test them thoroughly
4. **Commit your changes**:
   ```powershell
   git commit -m "Add feature: description of changes"
   ```
5. **Push to your branch**:
   ```powershell
   git push origin feature-name
   ```
6. **Create a pull request** on GitHub

### Development Guidelines

- Follow Python PEP 8 style guidelines
- Add comments and documentation for new features
- Test your changes thoroughly before submitting
- Update the README if you add new features or change setup procedures

### Areas for Contribution

- 🐛 Bug fixes and improvements
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Testing and quality assurance
- 🎨 UI/UX improvements
- 🌐 Multi-language support

## Contributors

Special thanks to all the contributors who have helped make NOVA AI better:

- [Evan Grinnell](https://github.com/S0L0GUY) - Project Lead & Core Developer
- [Duck Song](https://github.com/DuckSong510) - Core Contributor
- [Viscrimson](https://github.com/Viscrimson) - Core Contributor

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Support

If you find NOVA AI helpful, consider:
- ⭐ Starring the repository on GitHub
- 🐛 Reporting bugs and issues
- 💡 Suggesting new features
- 🤝 Contributing to the codebase

For support, questions, or feature requests, please open an issue on GitHub.

**Enjoy your AI-powered VRChat experience with NOVA AI!** 🚀
