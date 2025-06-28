# NOVA AI
### /ˈnōvə/ - Your VRChat AI Companion

NOVA AI is an intelligent VRChat assistant that brings conversational AI directly into your VRChat experience. Using advanced speech recognition, natural language processing, and text-to-speech technology, NOVA can listen to your voice, understand what you're saying, and respond intelligently through VRChat's chatbox.

## Table of Contents
- [What is NOVA AI?](#what-is-nova-ai)
- [Features](#features)
- [Configuration System](#configuration-system)
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
- ⚙️ **Centralized Configuration**: All tunable settings in one location (`constants.py`)
- 🎯 **Easy Tuning**: Comprehensive configuration system for all aspects of NOVA

## Configuration System

NOVA AI features a revolutionary **centralized configuration system** that makes customization and tuning incredibly simple. Instead of hunting through multiple files to change settings, everything is organized in one place: `constants.py`.

### 🎯 **Why This Matters**

Before the constants system, changing NOVA's behavior meant:
- ❌ Searching through multiple Python files
- ❌ Finding hardcoded values scattered everywhere  
- ❌ Risk of breaking the code with incorrect edits
- ❌ No clear documentation of what each value does

Now with the constants system:
- ✅ **One file controls everything** - `constants.py`
- ✅ **Organized by purpose** - Network, Audio, AI, Voice, etc.
- ✅ **Clear documentation** - Every setting has explanatory comments
- ✅ **Safe to modify** - Designed specifically for user customization
- ✅ **Easy to backup** - Save your perfect configuration in one file

### 🏗️ **How It's Organized**

The `constants.py` file contains configuration classes grouped by functionality:

```python
class Network:          # All networking settings (IPs, ports)
class Audio:           # Audio device configuration  
class Voice:           # Text-to-speech settings
class LanguageModel:   # AI model configuration
class WhisperSettings: # Speech recognition tuning
class OpenAI:          # OpenAI/LM Studio API settings
class TTSSettings:     # Text-to-speech engine options
class FilePaths:       # All file and folder locations
# ... and more!
```

### 🔧 **Configuration Benefits**

- **🎚️ Fine-tune Performance**: Adjust speech recognition sensitivity, AI creativity, response speed
- **🎭 Customize Personality**: Modify system prompts and AI behavior  
- **🔊 Perfect Audio**: Set exact audio device indices and voice preferences
- **⚡ Optimize Speed**: Balance between accuracy and response time
- **🌐 Network Flexibility**: Easy port and IP configuration for different setups
- **📊 Monitor Control**: Customize the resource monitor appearance and behavior

### 📖 **Simple Example**

Want to make NOVA more creative? Just open `constants.py` and change:
```python
class LanguageModel:
    LM_TEMPERATURE = 0.9  # Changed from 0.7 to 0.9 for more creativity
```

Want better speech recognition? Update:
```python
class WhisperSettings:
    MODEL_SIZE = "small"  # Changed from "base" for better accuracy
```

That's it! The entire codebase automatically uses your new settings.

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
   - Open `constants.py` in a text editor (Notepad, VS Code, etc.)
   - Navigate to the `Audio` class and update the device indices:
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
   - Edit the `constants.py` file and find the `OpenAI` class
   - Update the `API_KEY` value:
   ```python
   class OpenAI:
       API_KEY = "your-api-key-here"
   ```

### Step 3: Configure VRChat OSC

1. **Enable OSC in VRChat:**
   - Launch VRChat
   - Go to Settings → OSC
   - Enable "Enabled"
   - Note the port number (usually 9000)

2. **Update network settings:**
   - The `constants.py` file should automatically detect your IP
   - Verify the `VRC_PORT` in the `Network` class matches VRChat's OSC port:
   ```python
   class Network:
       VRC_PORT = 9000  # Should match VRChat's OSC port
   ```

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

NOVA AI uses a centralized configuration system in `constants.py` that makes tuning and customization simple. All adjustable settings are organized into logical classes with clear documentation.

### 🎯 Quick Configuration Guide

Open `constants.py` in any text editor to modify NOVA's behavior. Here are the main configuration classes:

#### **🌐 Network Settings**
Configure networking and communication:
```python
class Network:
    LOCAL_IP = "127.0.0.1"        # Local IP address for OSC
    VRC_PORT = 9000               # VRChat OSC port
    HTTP_SERVER_PORT = 8080       # Internal HTTP server port
```

#### **🎤 Audio Configuration**
Set up your audio devices:
```python
class Audio:
    AUDIO_OUTPUT_INDEX = 7        # Speaker/headphone device index
    AUDIO_INPUT_INDEX = 2         # Microphone device index
```

#### **🗣️ Voice & TTS Settings**
Customize text-to-speech:
```python
class Voice:
    VOICE_NAME = "en-US-JennyNeural"  # TTS voice (run list_voices.py to see options)

class TTSSettings:
    ENGINE = "edge-tts"           # TTS engine to use
```

#### **🤖 AI Model Configuration**
Adjust AI behavior and performance:
```python
class LanguageModel:
    MODEL_ID = "meta-llama-3.1-8b-instruct"  # AI model to use
    LM_TEMPERATURE = 0.7                      # Creativity (0.0-1.0)

class OpenAI:
    BASE_URL = "http://localhost:1234/v1"     # LM Studio or OpenAI API URL
    API_KEY = "lm-studio"                     # Your API key
    MODEL_ID = "meta-llama-3.1-8b-instruct"  # Model identifier
    TEMPERATURE = 0.7                         # Response randomness
```

#### **🎧 Speech Recognition (Whisper)**
Fine-tune voice detection:
```python
class WhisperSettings:
    MODEL_SIZE = "base"           # Whisper model: tiny, base, small, medium, large
    VAD_AGGRESSIVENESS = 0        # Voice detection sensitivity (0-3)
    SAMPLE_RATE = 16000           # Audio sample rate
    VOICE_THRESHOLD = 0.9         # Speech detection threshold (0.0-1.0)
    MAX_RECORDING_DURATION = 30   # Maximum recording time in seconds
```

#### **⚡ Performance Tuning**
Optimize responsiveness:
```python
class InterruptionSettings:
    QUEUE_SLEEP_INTERVAL = 0.1    # Queue processing delay
    SENSITIVITY = 1.0             # Interruption detection sensitivity

class ErrorHandling:
    ERROR_RETRY_DELAY = 5         # Seconds to wait after errors
```

#### **🖥️ Resource Monitor**
Customize the performance monitor window:
```python
class ResourceMonitor:
    WINDOW_TITLE = "NOVA-AI"      # Monitor window title
    WINDOW_SIZE = "400x745"       # Window dimensions
    UPDATE_INTERVAL = 1000        # Update frequency (milliseconds)
```

#### **🎮 VRChat Integration**
Configure VRChat-specific features:
```python
class NovaPlacement:
    DEFAULT_WORLD = "The Black Cat"       # Default VRChat world
    DEFAULT_POSITION = "Downstairs Bar"   # Default spawn position
    INITIAL_DELAY = 15                    # Startup delay (seconds)
```

### 📁 File Paths
All file locations are centralized:
```python
class FilePaths:
    HISTORY_PATH = "json_files/history.json"
    NORMAL_SYSTEM_PROMPT_PATH = "prompts/normal_system_prompt.txt"
    # ... and more
```

### 🎨 Customizing NOVA's Personality

Edit the system prompt files in the `prompts/` folder:
- `normal_system_prompt.txt` - Default personality and behavior
- `snapchat_system_prompt.txt` - Alternative casual personality  
- `additional_system_prompt.txt` - Extra instructions and context

### 🎯 Common Configuration Scenarios

**Making NOVA More Creative:**
```python
class LanguageModel:
    LM_TEMPERATURE = 0.9  # Higher = more creative/random
```

**Improving Speech Recognition:**
```python
class WhisperSettings:
    MODEL_SIZE = "small"      # Better accuracy than "base"
    VAD_AGGRESSIVENESS = 2    # More sensitive voice detection
    VOICE_THRESHOLD = 0.8     # Lower = more sensitive to speech
```

**Reducing Response Time:**
```python
class WhisperSettings:
    MODEL_SIZE = "tiny"       # Faster but less accurate
    
class InterruptionSettings:
    QUEUE_SLEEP_INTERVAL = 0.05  # Faster processing
```

**Using OpenAI Instead of Local Models:**
```python
class OpenAI:
    BASE_URL = "https://api.openai.com/v1"  # Official OpenAI API
    API_KEY = "sk-your-real-openai-key"     # Your OpenAI API key
    MODEL_ID = "gpt-4"                      # Use GPT-4
```

### 🔧 Advanced Configuration

**Custom Voice Selection:**
1. Run `python list_voices.py` to see available voices
2. Update the `VOICE_NAME` in constants.py with your preferred voice

**Network Troubleshooting:**
- Change `VRC_PORT` if VRChat uses a different OSC port
- Modify `LOCAL_IP` if using VRChat on a different machine

**Performance Optimization:**
- Adjust `UPDATE_INTERVAL` in ResourceMonitor for faster/slower monitoring
- Modify `ERROR_RETRY_DELAY` for quicker error recovery

### 💡 Configuration Tips

1. **Start with defaults** - The included settings work well for most users
2. **Change one setting at a time** - This helps identify what each change does
3. **Test thoroughly** - Restart NOVA after making changes to see effects
4. **Keep backups** - Save a copy of working configurations
5. **Use comments** - Add your own notes in constants.py for custom settings

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
- Update the `Audio` class in `constants.py` with correct `AUDIO_INPUT_INDEX` and `AUDIO_OUTPUT_INDEX` values

**VRChat not receiving messages:**
- Ensure OSC is enabled in VRChat settings
- Check that VRChat is running and you're in a world
- Verify the `VRC_PORT` in the `Network` class matches VRChat's OSC port (default 9000)

**OpenAI API errors:**
- Verify your API key is set correctly in the `OpenAI` class in `constants.py`
- Check your OpenAI account has available credits
- Ensure you have access to the model specified in `MODEL_ID`
- For local LM Studio, verify the `BASE_URL` points to your local server

**Microphone not working:**
- Check Windows microphone permissions
- Verify the microphone works in other applications
- Try different audio device indices using `python list_audio_devices.py`
- Adjust `WhisperSettings.VAD_AGGRESSIVENESS` for better voice detection

**Configuration Issues:**
- Always restart NOVA after changing `constants.py`
- Verify syntax is correct (proper indentation, quotes, commas)
- Check that modified values are the right data type (numbers vs strings)
- Use the default values as a reference if something stops working

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
3. Update audio device indices in the `Audio` class in `constants.py`

### Custom System Prompts

Create custom personalities by editing files in the `prompts/` directory to change how NOVA behaves and responds.

### Local vs Cloud AI Models

**Using Local Models (LM Studio):**
- Keep the default `constants.py` settings
- Ensure LM Studio is running on `http://localhost:1234`

**Using OpenAI Cloud API:**
```python
class OpenAI:
    BASE_URL = "https://api.openai.com/v1"
    API_KEY = "sk-your-actual-openai-key"
    MODEL_ID = "gpt-4"  # or "gpt-3.5-turbo"
```



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
