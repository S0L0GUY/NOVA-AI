# NOVA AI
### /ˈnōvə/ - Your VRChat AI Companion

NOVA AI is an intelligent VRChat assistant that brings conversational AI directly into your VRChat experience. Using advanced speech recognition, natural language processing, text-to-speech technology, computer vision, and VRChat API integration, NOVA can listen to your voice, understand what you're saying, see your VRChat world, manage social interactions, and respond intelligently through VRChat's chatbox. With native support for 29+ languages, NOVA can communicate naturally in your preferred language with automatic language detection and multilingual voice synthesis.

## Table of Contents
- [What is NOVA AI?](#what-is-nova-ai)
- [Features](#features)
- [Configuration System](#configuration-system)
- [Vision System](#vision-system)
- [VRChat API Integration](#vrchat-api-integration)
- [Together AI Integration](#together-ai-integration)
- [Multilingual Support](#multilingual-support)
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
- **Thinks** using powerful AI language models (Together AI)
- **Sees** your VRChat world using computer vision and screenshot analysis
- **Responds** through VRChat's chatbox using OSC (Open Sound Control)
- **Speaks** back to you using text-to-speech technology (Microsoft Edge TTS)
- **Manages** VRChat social interactions via API integration (friend requests, notifications)
- **Monitors** system performance with a real-time resource dashboard
- **Communicates** in 29+ languages with automatic language detection and multilingual TTS voices

Perfect for content creators, VRChat enthusiasts, or anyone who wants an intelligent AI companion in their virtual world!

## Features

- 🎤 **Voice Recognition**: Advanced speech-to-text using OpenAI Whisper with configurable models
- 🧠 **AI Conversation**: Powered by Together AI with access to cutting-edge open-source models
- 💬 **VRChat Integration**: Seamlessly displays responses in VRChat chatbox via OSC
- 🔊 **Text-to-Speech**: Speaks responses back using Microsoft Edge TTS with customizable voices
- 🎚️ **Voice Activity Detection**: Automatically detects when you start and stop speaking with WebRTC VAD
- ⚙️ **Customizable**: Configurable system prompts, voices, and behavior through centralized constants
- 📊 **Resource Monitoring**: Built-in performance monitoring with customizable GUI dashboard
- 🔧 **Modular Design**: Easy to extend and customize with class-based architecture
- ⚙️ **Centralized Configuration**: All tunable settings in one location (`constants.py`)
- 🎯 **Easy Tuning**: Comprehensive configuration system for all aspects of NOVA
- 👁️ **Vision System**: Advanced computer vision capabilities for VRChat world analysis
- 🤝 **VRChat API Integration**: Automatic friend request handling and notification management
- 🔒 **Secure Configuration**: Environment variable system for sensitive credentials
- 🎮 **Avatar Movement**: Automated VRChat avatar positioning and movement capabilities
- 🌐 **Multilingual Support**: Native support for 29+ languages with automatic language detection and multilingual TTS voices

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
class LLM_API:         # Together AI API settings for language models
class Vision_API:      # Together AI API settings for vision models
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

## Vision System

NOVA AI includes an advanced **Vision System** that brings computer vision capabilities to your VRChat experience. This powerful feature allows NOVA to "see" your VRChat world, analyze what's happening, and provide contextual responses based on visual information.

### 👁️ **What is the Vision System?**

The Vision System is an optional module that:
- **📸 Captures Screenshots**: Automatically takes screenshots of your VRChat window
- **🔍 Analyzes Content**: Uses AI vision models to understand what's in the image
- **👥 Identifies Players**: Recognizes avatars, usernames, and player interactions
- **🌍 Describes Environments**: Understands world themes, lighting, and atmosphere
- **💬 Provides Context**: Gives NOVA visual context for more intelligent responses

### 🎯 **Key Capabilities**

#### **Player Detection & Recognition**
- Identifies visible avatars and their appearance
- Reads usernames when visible
- Counts how many players are in view
- Describes avatar styles, outfits, and accessories

#### **Environment Analysis**
- Recognizes world themes (nightclub, forest, city, etc.)
- Describes lighting conditions and atmosphere
- Identifies notable objects and structures
- Understands the overall vibe of the space

#### **Behavioral Context**
- Observes player actions (dancing, sitting, emoting)
- Detects social interactions
- Notices movement and activities

### ⚙️ **Vision System Configuration**

The Vision System is controlled through the `VisionSystem` class in `constants.py`:

```python
class VisionSystem:
    # Enable or disable the vision system
    ENABLED = False  # Set to True to enable vision
    
    # How often to analyze screenshots (seconds)
    ANALYSIS_INTERVAL = 15
    
    # Image processing settings
    MAX_IMAGE_SIZE = 1024     # Max resolution for AI processing
    IMAGE_QUALITY = 85        # JPEG quality (1-100)
    
    # AI model settings
    VISION_MODEL = "qwen/qwen2.5-vl-7b"  # Vision model to use
    MAX_VISION_TOKENS = 150   # Response length limit
    VISION_TEMPERATURE = 0.3  # Creativity level (0.0-1.0)
    
    # File locations
    STATE_FILE = "json_files/vision_state.json"
    LOG_FILE = "json_files/vision_log.json"
    VISION_PROMPT_PATH = "prompts/vision_prompt.txt"
```

### 🚀 **Enabling the Vision System**

#### **Step 1: Enable in Configuration**
1. Open `constants.py` in a text editor
2. Find the `VisionSystem` class
3. Change `ENABLED = False` to `ENABLED = True`

#### **Step 2: Set Up Vision Model**
The Vision System supports Together AI's vision models:

- Keep the default `VISION_MODEL = "meta-llama/Llama-Vision-Free"`
- The default settings in `constants.py` are already configured for Together AI:
  ```python
  class Vision_API:
      BASE_URL = "https://api.together.xyz/v1"
  ```
- Ensure your Together AI API key is set in your `.env` file as `VISION_API_KEY`

#### **Step 3: Test the System**
Test the vision system by:
1. Ensuring VRChat is running and visible
2. Starting NOVA with vision enabled
3. Monitoring console output for vision updates
4. Checking the `json_files/vision_log.json` file for logged vision data

### 🎮 **How It Works in VRChat**

1. **Automatic Detection**: The system automatically finds your VRChat window
2. **Periodic Analysis**: Takes screenshots at regular intervals (configurable)
3. **AI Processing**: Sends images to the vision model for analysis
4. **Context Integration**: Provides visual context to NOVA for better responses
5. **Logging**: Keeps a log of recent visual observations

### 💬 **Example Vision Responses**

When the Vision System is active, NOVA can make responses like:

- *"I can see you're in a beautiful cyberpunk nightclub with neon lights everywhere!"*
- *"There are 3 other players here - someone with butterfly wings is dancing near the center."*
- *"This cozy forest world has such peaceful vibes with those cherry blossom trees."*
- *"I notice xX_Gamer_Xx just joined in that golden armor avatar - pretty cool look!"*

### 📊 **Performance & Privacy**

#### **Performance Considerations**
- Vision analysis adds processing overhead
- Adjust `ANALYSIS_INTERVAL` to balance responsiveness vs. performance
- Lower `MAX_IMAGE_SIZE` for faster processing
- Use `IMAGE_QUALITY` to balance file size vs. detail

#### **Privacy Features**
- Screenshots are processed locally (unless using cloud APIs)
- No images are permanently stored
- Vision logs can be cleared at any time
- System can be disabled instantly

### 🔧 **Advanced Configuration**

#### **Customizing Vision Behavior**
Edit `prompts/vision_prompt.txt` to change how the AI interprets images:
- Modify what details to focus on
- Change the response style
- Add specific instructions for your use case

#### **Performance Tuning**
```python
# For better accuracy (slower)
ANALYSIS_INTERVAL = 10      # More frequent analysis
MAX_IMAGE_SIZE = 1920       # Higher resolution
VISION_TEMPERATURE = 0.1    # More consistent results

# For better performance (faster)
ANALYSIS_INTERVAL = 30      # Less frequent analysis  
MAX_IMAGE_SIZE = 512        # Lower resolution
VISION_TEMPERATURE = 0.5    # More varied results
```

#### **Selective Analysis**
The Vision System can be configured to only analyze when:
- NOVA is directly spoken to
- Specific keywords are mentioned
- Manual triggers are activated

### 🛠️ **Troubleshooting Vision System**

**Vision System Not Starting:**
- Verify `ENABLED = True` in `constants.py`
- Check that VRChat window is visible and active
- Monitor console output for vision system startup messages
- Ensure your AI model supports vision capabilities

**Poor Recognition Quality:**
- Increase `MAX_IMAGE_SIZE` for better detail
- Adjust `IMAGE_QUALITY` for clearer images
- Check lighting in your VRChat world
- Try different vision models

**Performance Issues:**
- Increase `ANALYSIS_INTERVAL` for less frequent analysis
- Decrease `MAX_IMAGE_SIZE` for faster processing
- Consider using a faster vision model
- Monitor system resources during operation

**API Errors:**
- Verify your AI model supports vision capabilities
- Check API key permissions for vision access
- Ensure sufficient API credits/quota
- Monitor console output for specific error messages

### 🎯 **Best Practices**

1. **Start Conservative**: Begin with longer analysis intervals and smaller image sizes
2. **Monitor Performance**: Watch system resources when vision is enabled
3. **Customize Prompts**: Tailor the vision prompt for your specific VRChat activities
4. **Test Different Models**: Try various vision models to find the best balance
5. **Privacy Awareness**: Remember that the system can see everything in your VRChat window

The Vision System transforms NOVA from a voice-only assistant into a truly aware VRChat companion that can see and understand your virtual world!

## VRChat API Integration

NOVA AI includes comprehensive **VRChat API Integration** that enables advanced social features and automation within VRChat. This powerful system allows NOVA to interact with VRChat's official API to manage social interactions, handle notifications, and provide a more integrated VRChat experience.

### 🔌 **What is VRChat API Integration?**

The VRChat API Integration is an optional module that:
- **👥 Friend Management**: Automatically accepts friend requests based on your preferences
- **🔔 Notification Handling**: Monitors and processes VRChat notifications in real-time
- **📊 Social Analytics**: Tracks friend interactions and social metrics
- **🛡️ Rate Limiting**: Implements proper rate limiting to respect VRChat's API guidelines
- **🔐 Secure Authentication**: Uses your VRChat credentials securely via environment variables

### 🎯 **Key Capabilities**

#### **Friend Request Management**
- Automatically accept incoming friend requests
- Configurable auto-accept behavior
- Rate-limited processing to prevent API abuse
- Retry logic for failed operations

#### **Notification Monitoring**
- Real-time notification checking
- Processes various notification types
- Configurable check intervals
- Duplicate notification filtering

#### **API Rate Limiting & Safety**
- Respects VRChat's API usage policies
- Implements exponential backoff for retries
- Connection timeout handling
- Comprehensive error logging

### ⚙️ **VRChat API Configuration**

The VRChat API system is controlled through the `VRChatAPI` class in `constants.py`:

```python
class VRChatAPI:
    # Master switch to enable/disable all VRChat API functionality
    USING_API = False  # Set to True to enable API usage
    
    # VRChat account credentials (loaded from environment variables)
    USERNAME = os.getenv('VRCHAT_EMAIL')
    PASSWORD = os.getenv('VRCHAT_PASSWORD')
    
    # User agent string as per VRChat Usage Policy
    USER_AGENT = f"NOVA-AI/2025.1.1 {os.getenv('VRCHAT_EMAIL')}"
    
    # API check intervals (seconds)
    FRIEND_REQUEST_CHECK_INTERVAL = 60  # 1 minute
    NOTIFICATION_CHECK_INTERVAL = 120    # 2 minutes
    
    # Rate limiting and cooldown settings
    API_COOLDOWN = 30  # Seconds to wait between API calls
    
    # Feature toggles
    AUTO_ACCEPT_FRIEND_REQUESTS = True
    ENABLE_NOTIFICATION_CHECKS = True
    ENABLE_FRIEND_REQUEST_CHECKS = True
    
    # Connection timeout settings
    CONNECTION_TIMEOUT = 30
    REQUEST_TIMEOUT = 15
    
    # Retry settings for failed operations
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5  # Seconds between retries
    
    # Debug settings
    VERBOSE_LOGGING = False  # Set to True for detailed API logs
```

### 🚀 **Enabling VRChat API Integration**

#### **Step 1: Enable in Configuration**
1. Open `constants.py` in a text editor
2. Find the `VRChatAPI` class
3. Change `USING_API = False` to `USING_API = True`

#### **Step 2: Configure Environment Variables**
The VRChat API requires your VRChat account credentials:

1. **Ensure your `.env` file exists** (copy from `.env.example` if needed)
2. **Add your VRChat credentials**:
   ```properties
   # VRChat Login Credentials
   VRCHAT_EMAIL=your-vrchat-email@example.com
   VRCHAT_PASSWORD=your-vrchat-password
   ```

#### **Step 3: Customize API Behavior**
Adjust the settings in `constants.py` based on your preferences:

```python
# Enable/disable specific features
AUTO_ACCEPT_FRIEND_REQUESTS = True    # Automatically accept friend requests
ENABLE_NOTIFICATION_CHECKS = True     # Monitor notifications
ENABLE_FRIEND_REQUEST_CHECKS = True   # Check for new friend requests

# Adjust timing
FRIEND_REQUEST_CHECK_INTERVAL = 60    # How often to check for friend requests
NOTIFICATION_CHECK_INTERVAL = 120     # How often to check notifications
```

### 🔐 **Security & Privacy**

#### **Credential Security**
- VRChat credentials are stored in environment variables (`.env` file)
- Never hardcode credentials directly in the code
- The `.env` file is automatically ignored by Git for security

#### **API Compliance**
- Follows VRChat's API Usage Policy and Terms of Service
- Implements proper User-Agent strings as required
- Uses appropriate rate limiting to prevent API abuse
- Respects VRChat's API guidelines and best practices

#### **Privacy Features**
- API integration can be disabled completely
- Verbose logging can be turned off
- No personal data is logged or transmitted beyond VRChat's API

### 🎮 **How It Works in VRChat**

1. **Background Processing**: The API system runs in the background while NOVA operates
2. **Friend Request Handling**: Automatically processes incoming friend requests
3. **Notification Monitoring**: Checks for new notifications at regular intervals
4. **Integration with NOVA**: Can inform NOVA about VRChat events for contextual responses
5. **Rate Limiting**: Automatically manages API call frequency to stay within limits

### 💬 **Example API Integration**

When the VRChat API is active, NOVA can provide responses like:

- *"I just accepted a friend request from VRChatUser123!"*
- *"You have 3 new notifications in VRChat."*
- *"Your friend list has been updated with 2 new friends."*

### 📊 **Performance & Monitoring**

#### **API Monitoring**
- Connection status tracking
- API call success/failure rates
- Rate limiting status
- Error logging and recovery

#### **Performance Optimization**
```python
# For better responsiveness (more frequent checks)
FRIEND_REQUEST_CHECK_INTERVAL = 30    # Check every 30 seconds
NOTIFICATION_CHECK_INTERVAL = 60      # Check every minute

# For better performance (less frequent checks)
FRIEND_REQUEST_CHECK_INTERVAL = 300   # Check every 5 minutes
NOTIFICATION_CHECK_INTERVAL = 600     # Check every 10 minutes
```

### 🛠️ **Troubleshooting VRChat API**

**API Not Connecting:**
- Verify `USING_API = True` in `constants.py`
- Check VRChat credentials in `.env` file
- Ensure VRChat account has API access enabled

**Authentication Errors:**
- Verify email and password are correct in `.env`
- Check if two-factor authentication is enabled on your VRChat account
- Ensure your VRChat account is in good standing

**Rate Limiting Issues:**
- Increase `API_COOLDOWN` value for longer delays between calls
- Reduce check intervals to make fewer API requests
- Monitor console output for rate limiting warnings

**Connection Timeouts:**
- Increase `CONNECTION_TIMEOUT` and `REQUEST_TIMEOUT` values
- Check internet connection stability
- Verify VRChat API status

### 🎯 **Best Practices**

1. **Start Conservatively**: Begin with longer check intervals and increase frequency as needed
2. **Monitor Performance**: Watch console output for API errors or warnings
3. **Respect Rate Limits**: Don't set intervals too aggressively
4. **Keep Credentials Secure**: Never share your `.env` file or commit it to version control
5. **Test Thoroughly**: Verify API functionality before relying on automated features

The VRChat API Integration makes NOVA a more complete VRChat companion by bridging the gap between your AI assistant and VRChat's social features! (We are not liable if your accounts gets suspended or banned because of VRChat API usage)

## Together AI Integration

NOVA AI now includes **first-class support for Together AI**, providing access to cutting-edge open-source language models with fast inference and competitive pricing.

### 🚀 **Why Together AI?**

Together AI offers several advantages for NOVA users:

- **🔓 Open Source Models**: Access to the latest open-source language models like Llama 3.3, Qwen, and more
- **⚡ Fast Inference**: Optimized infrastructure for quick response times
- **💰 Cost Effective**: Competitive pricing compared to other cloud AI providers
- **🧠 Advanced Models**: Support for both text and vision models
- **🔄 Easy Integration**: Drop-in replacement for OpenAI API with minimal configuration changes

### 🎯 **Supported Models**

Together AI provides access to a wide range of models suitable for different use cases:

#### **Text Generation Models**
- **Llama 3.3 70B Instruct Turbo** (Default): High-quality responses with good speed
- **Qwen 2.5 72B Instruct**: Excellent for general conversation and reasoning
- **Mixtral 8x7B**: Fast responses with good quality
- **And many more**: Browse available models at [api.together.xyz](https://api.together.xyz)

#### **Vision Models**
- **Llama Vision Free**: Multimodal understanding for VRChat screenshot analysis
- **Qwen VL models**: Advanced vision-language understanding
- **Custom vision models**: Support for specialized vision tasks

### ⚙️ **Configuration**

Together AI is configured as the default API provider in NOVA AI. The configuration is handled through two main classes in `constants.py`:

```python
class LLM_API:
    API_TYPE = "together"  # Uses Together AI for text generation
    BASE_URL = "https://api.together.xyz/v1"
    API_KEY = os.getenv('LLM_API_KEY')  # Your Together AI API key

class Vision_API:
    API_TYPE = "together"  # Uses Together AI for vision tasks
    BASE_URL = "https://api.together.xyz/v1"
    API_KEY = os.getenv('VISION_API_KEY')  # Your Together AI API key
```

### 🔑 **Getting Started with Together AI**

1. **Create Account**: Sign up at [api.together.xyz](https://api.together.xyz)
2. **Get API Key**: Generate your API key from the dashboard
3. **Set Environment Variables**: Add your key to the `.env` file:
   ```properties
   LLM_API_KEY=your-together-ai-api-key-here
   VISION_API_KEY=your-together-ai-api-key-here
   ```
4. **Choose Models**: Update model names in `constants.py` if desired
5. **Start NOVA**: The system will automatically use Together AI for inference

### 💡 **Tips for Best Results**

- **Model Selection**: Choose models based on your performance vs. quality needs
- **Temperature Settings**: Lower values (0.3-0.7) for more focused responses
- **Token Limits**: Monitor usage to stay within your preferred budget
- **Rate Limits**: Together AI has generous rate limits for most use cases

## Multilingual Support

NOVA AI includes **comprehensive multilingual support**, allowing you to interact with NOVA in over 29 languages with natural conversation flow and appropriate voice responses.

### 🌍 **Supported Languages**

NOVA can understand and respond in the following languages:

**European Languages:**
- **English** (US, UK, AU, CA) - Primary language
- **Spanish** (ES, MX, AR, CO, and more)
- **French** (FR, CA, BE, CH)
- **German** (DE, AT, CH)
- **Italian** (IT, CH)
- **Portuguese** (PT, BR)
- **Dutch** (NL, BE)
- **Russian** (RU)
- **Polish** (PL)
- **Turkish** (TR)
- **Swedish** (SE)
- **Norwegian** (NO)
- **Finnish** (FI)
- **Ukrainian** (UA)
- **Romanian** (RO)
- **Hungarian** (HU)
- **Greek** (GR)
- **Czech** (CZ)
- **Hebrew** (IL)

**Asian Languages:**
- **Chinese** (Mandarin - CN, TW)
- **Japanese** (JP)
- **Korean** (KR)
- **Hindi** (IN)
- **Bengali** (IN, BD)
- **Urdu** (PK, IN)
- **Thai** (TH)
- **Vietnamese** (VN)
- **Indonesian** (ID)

**Middle Eastern & African:**
- **Arabic** (Multiple dialects: SA, AE, EG, MA, TN, and more)

### 🎤 **Speech Recognition**

NOVA uses **OpenAI Whisper** for speech recognition, which provides:
- **Automatic language detection** - Whisper can detect what language you're speaking
- **High accuracy** across all supported languages
- **Real-time processing** with configurable model sizes
- **Robust performance** with accents and dialects

### 🔊 **Text-to-Speech (TTS)**

NOVA's TTS system supports **142+ languages** through Microsoft Edge TTS:

#### **Multilingual Voices**
NOVA includes access to advanced multilingual neural voices that can speak multiple languages naturally:
- **EmmaMultilingualNeural** (Default) - English with multilingual capabilities
- **VivienneMultilingualNeural** - French with multilingual capabilities  
- **SeraphinaMultilingualNeural** - German with multilingual capabilities
- **GiuseppeMultilingualNeural** - Italian with multilingual capabilities
- **HyunsuMultilingualNeural** - Korean with multilingual capabilities
- And many more specialized voices for each language

#### **Language-Specific Features**
- **Native character support** - Displays text in original scripts (Chinese: 你好, Arabic: مرحبا, etc.)
- **Proper pronunciation** - Each language uses appropriate phonetic models
- **Cultural context** - Responses adapt to cultural norms and expressions
- **Regional variants** - Support for different regional accents and dialects

### ⚙️ **Configuration**

#### **Changing TTS Voice Language**
To change NOVA's voice to another language, modify `constants.py`:

```python
class Voice:
    # Examples of multilingual voices:
    VOICE_NAME = "en-US-EmmaMultilingualNeural"     # English (Default)
    # VOICE_NAME = "es-ES-ElviraNeural"             # Spanish
    # VOICE_NAME = "fr-FR-VivienneMultilingualNeural" # French  
    # VOICE_NAME = "de-DE-SeraphinaMultilingualNeural" # German
    # VOICE_NAME = "ja-JP-NanamiNeural"             # Japanese
    # VOICE_NAME = "ko-KR-HyunsuMultilingualNeural" # Korean
    # VOICE_NAME = "zh-CN-XiaoyiNeural"             # Chinese
```

#### **Language Detection Settings**
Whisper automatically detects languages, but you can optimize settings in `constants.py`:

```python
class WhisperSettings:
    MODEL_SIZE = "base"  # "base" for multilingual, "small" for better accuracy
    # Larger models (small, medium, large) provide better multilingual support
```

### 🗣️ **How Multilingual Conversation Works**

1. **You speak** in any supported language
2. **Whisper detects** your language automatically  
3. **NOVA understands** and processes in the detected language
4. **NOVA responds** in the same language (or English if configured)
5. **TTS speaks** the response using the appropriate voice

### 💡 **Best Practices**

#### **For Optimal Multilingual Performance:**
- **Use larger Whisper models** (`small` or `medium`) for better language detection
- **Speak clearly** - especially important for non-native languages
- **Choose appropriate TTS voices** - use multilingual voices for mixed-language conversations
- **Consider context** - NOVA maintains conversation context across languages

#### **Mixed Language Conversations:**
- NOVA can handle **code-switching** (switching between languages mid-conversation)
- **Each response** maintains the language of the input
- **Multilingual voices** can naturally handle multiple languages in one conversation

### 🎯 **Language-Specific Features**

#### **Cultural Adaptation**
- **Greetings and expressions** adapt to cultural norms
- **Formality levels** adjust based on language conventions
- **Regional references** include local context when appropriate

#### **Script Support**
- **Latin scripts** (English, Spanish, French, German, etc.)
- **Cyrillic** (Russian, Ukrainian, etc.)  
- **CJK characters** (Chinese, Japanese, Korean)
- **Arabic script** (Arabic, Urdu, etc.)
- **Devanagari** (Hindi, Bengali, etc.)

### 🔧 **Advanced Configuration**

#### **Custom Voice Selection**
You can browse and select from 400+ voices across 142 languages. To see available voices:

```python
# Add this to a Python script to list available voices
import edge_tts
import asyncio

async def list_voices():
    voices = await edge_tts.list_voices()
    for voice in voices:
        if 'your_language_code' in voice['Locale']:
            print(f"{voice['ShortName']} - {voice['FriendlyName']}")

asyncio.run(list_voices())
```

#### **Performance Optimization**
- **Whisper model size** affects multilingual accuracy:
  - `tiny`: Fast but limited multilingual support
  - `base`: Good balance for most languages  
  - `small`: Better accuracy for non-English languages
  - `medium/large`: Best multilingual performance

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
- **Optional**: Virtual audio cables for advanced audio routing (VB-Audio Virtual Cable)

### 5. AI Model Access
NOVA AI uses Together AI for inference:
- Sign up at [api.together.xyz](https://api.together.xyz)
- Get your API key from the dashboard
- Add credits to your Together AI account for usage

### 6. System Requirements
- **RAM**: 8GB minimum (16GB recommended with vision system)
- **Storage**: 2GB free space (more for local AI models)
- **GPU**: Optional but recommended for better performance with local models
- **Windows**: Windows 10 or later (for compatibility with all features)

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
If PyAudio installation fails:
1. Download the appropriate .whl file from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)
2. Install it with: `pip install path\to\downloaded\file.whl`

**For Windows-specific features:**
The installation includes Windows-specific packages for:
- System resource monitoring (`psutil`, `GPUtil`)
- Window management (`pywin32`)
- Custom GUI components (`customtkinter`)

### Step 4: Verify Installation

Test that all components are properly installed:

1. **Test audio device detection:**
   ```powershell
   python list_audio_devices.py
   ```

2. **Verify Python packages:**
   ```powershell
   python -c "import openai, whisper, edge_tts, PIL, customtkinter; print('All packages installed successfully')"
   ```

### Step 5: Prepare Configuration Files

Before starting setup, NOVA AI includes example configuration files to help you get started:

1. **Environment Variables**: Copy `.env.example` to `.env` for your API keys and VRChat credentials
2. **Configuration Reference**: Review `constants.py` for all available settings
3. **System Prompts**: Check the `prompts/` folder for personality customization options

You'll configure these files in the following setup steps.

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

### Step 2: Set Up Environment Variables (.env file)

NOVA AI uses environment variables to securely store sensitive information like API keys and VRChat credentials. This keeps your login information separate from the code.

1. **Create a .env file from the example:**
   - In the NOVA-AI folder, you'll find a `.env.example` file
   - Copy this file and rename it to `.env`:
   ```powershell
   copy .env.example .env
   ```
   - Or manually create a new file called `.env` (note the dot at the beginning)

2. **Edit your .env file:**
   - Open the `.env` file in any text editor
   - Replace the example values with your actual credentials:
   ```properties
   # VRChat Login Credentials (required for VRChat API features)
   VRCHAT_EMAIL=your-actual-vrchat-email@example.com
   VRCHAT_PASSWORD=your-actual-vrchat-password
   
   # Together AI API Key for LLM
   LLM_API_KEY=your-together-ai-api-key-here
   
   # Together AI API Key for Vision (can be the same as LLM_API_KEY)
   VISION_API_KEY=your-together-ai-api-key-here
   ```

3. **Configure your Together AI API key:**
   - Get your API key from [api.together.xyz](https://api.together.xyz)
   - Add it to your `.env` file as shown above
   
4. **Important Security Notes:**
   - Never share your `.env` file or commit it to version control
   - The `.env` file is automatically ignored by Git for your security
   - NOVA will automatically load these credentials when it starts
   - The `.env.example` file shows the format but contains no real credentials

### Step 3: Configure AI Model Access

NOVA AI uses Together AI for AI processing:

1. Sign up at [api.together.xyz](https://api.together.xyz)
2. Get your API key from the dashboard
3. Update your `.env` file with your Together AI API key:
   ```properties
   LLM_API_KEY=your-together-api-key-here
   VISION_API_KEY=your-together-api-key-here
   ```
4. The default settings in `constants.py` are already configured for Together AI:
   ```python
   class LLM_API:
       BASE_URL = "https://api.together.xyz/v1"
       API_KEY = os.getenv('LLM_API_KEY')
   ```

### Step 4: Configure VRChat OSC

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
       LOCAL_IP = socket.gethostbyname(socket.gethostname())  # Auto-detected
       VRC_PORT = 9000               # Should match VRChat's OSC port
   ```

### Step 5: Test Audio Setup

1. **Find your audio device indices:**
   ```powershell
   python list_audio_devices.py
   ```
   This will show all available audio devices with their index numbers.

2. **Configure audio devices:**
   - Open `constants.py` in a text editor
   - Navigate to the `Audio` class and update the device indices:
   ```python
   class Audio:
       AUDIO_OUTPUT_INDEX = 6        # Replace with your speaker/headphone index
       AUDIO_INPUT_INDEX = 2         # Replace with your microphone index
   ```

3. **Test audio functionality:**
   - Test microphone recording and TTS playback by running NOVA
   - Adjust device indices if audio doesn't work properly

### Step 6: Configure Multilingual Support (Optional)

NOVA AI supports 29+ languages out of the box. To optimize for your preferred language:

1. **Choose a multilingual TTS voice:**
   - Edit `constants.py` and find the `Voice` class
   - The default voice `en-US-EmmaMultilingualNeural` already supports multiple languages
   - For better language-specific pronunciation, choose a native voice:
   ```python
   class Voice:
       # Multilingual voices (recommended):
       VOICE_NAME = "en-US-EmmaMultilingualNeural"    # English + multilingual
       # VOICE_NAME = "fr-FR-VivienneMultilingualNeural" # French + multilingual
       # VOICE_NAME = "de-DE-SeraphinaMultilingualNeural" # German + multilingual
       
       # Native language voices:
       # VOICE_NAME = "es-ES-ElviraNeural"           # Spanish
       # VOICE_NAME = "ja-JP-NanamiNeural"           # Japanese
       # VOICE_NAME = "ko-KR-HyunsuMultilingualNeural" # Korean
       # VOICE_NAME = "zh-CN-XiaoyiNeural"           # Chinese
   ```

2. **Optimize speech recognition for your language:**
   - For non-English languages, consider using a larger Whisper model:
   ```python
   class WhisperSettings:
       MODEL_SIZE = "small"  # Better for multilingual (was "base")
       # Options: "tiny", "base", "small", "medium", "large"
   ```

3. **Language detection is automatic:**
   - Whisper automatically detects the language you're speaking
   - No additional configuration needed for language detection
   - NOVA will respond in the language you use

## Configuration

NOVA AI uses a centralized configuration system in `constants.py` that makes tuning and customization simple. All adjustable settings are organized into logical classes with clear documentation.

### 🎯 Quick Configuration Guide

Open `constants.py` in any text editor to modify NOVA's behavior. Here are the main configuration classes:

#### **🌐 Network Settings**
Configure networking and communication:
```python
class Network:
    LOCAL_IP = socket.gethostbyname(socket.gethostname())  # Auto-detected local IP
    VRC_PORT = 9000               # VRChat OSC port
```

#### **🎤 Audio Configuration**
Set up your audio devices:
```python
class Audio:
    AUDIO_OUTPUT_INDEX = 6        # Speaker/headphone device index
    AUDIO_INPUT_INDEX = 2         # Microphone device index
```

#### **🗣️ Voice & TTS Settings**
Customize text-to-speech:
```python
class Voice:
    VOICE_NAME = "en-US-EmmaMultilingualNeural"  # Default multilingual voice
    # Other multilingual options:
    # VOICE_NAME = "es-ES-ElviraNeural"          # Spanish
    # VOICE_NAME = "fr-FR-VivienneMultilingualNeural" # French
    # VOICE_NAME = "de-DE-SeraphinaMultilingualNeural" # German
    # VOICE_NAME = "ja-JP-NanamiNeural"          # Japanese
    # VOICE_NAME = "ko-KR-HyunsuMultilingualNeural" # Korean
    # VOICE_NAME = "zh-CN-XiaoyiNeural"          # Chinese

class TTSSettings:
    ENGINE = "edge-tts"           # TTS engine (currently only edge-tts supported)
    AUDIO_CONVERSION_FACTOR = 2**15  # Audio processing factor
    QUEUE_SLEEP_INTERVAL = 0.1    # Queue processing interval
```

#### **🤖 AI Model Configuration**
Adjust AI behavior and performance:
```python
class LanguageModel:
    MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct-Turbo"  # AI model to use
    LM_TEMPERATURE = 0.7                      # Creativity (0.0-1.0)

class LLM_API:
    BASE_URL = "https://api.together.xyz/v1"  # Together AI API endpoint
    API_KEY = os.getenv('LLM_API_KEY')        # Your API key from .env file

class Vision_API:
    BASE_URL = "https://api.together.xyz/v1"  # Together AI API endpoint
    API_KEY = os.getenv('VISION_API_KEY')     # Your vision API key from .env file
```

#### **🎧 Speech Recognition (Whisper)**
Fine-tune voice detection:
```python
class WhisperSettings:
    MODEL_SIZE = "base"           # Whisper model: tiny, base, small, medium, large
    SAMPLE_RATE = 16000           # Audio sample rate
    FRAME_DURATION_MS = 30        # Frame duration for voice detection
    NUM_PADDING_FRAMES = 10       # Voice detection padding
    VOICE_THRESHOLD = 0.9         # Speech detection threshold (0.0-1.0)
    MAX_RECORDING_DURATION = 30   # Maximum recording time in seconds
    VAD_AGGRESSIVENESS = 0        # Voice detection sensitivity (0-3)
```

#### **👁️ Vision System Configuration**
Control computer vision capabilities:
```python
class VisionSystem:
    ENABLED = False               # Enable/disable vision system
    ANALYSIS_INTERVAL = 15        # Screenshot analysis frequency (seconds)
    MAX_IMAGE_SIZE = 1024         # Maximum image resolution for processing
    VISION_MODEL = "meta-llama/Llama-Vision-Free"  # Together AI vision model to use
    VISION_TEMPERATURE = 0.3      # Vision analysis creativity (0.0-1.0)
```

#### **🖥️ Resource Monitor**
Customize the performance monitor window:
```python
class ResourceMonitor:
    WINDOW_TITLE = "Nova Resource Monitor"  # Monitor window title
    WINDOW_WIDTH = 400                      # Window width
    WINDOW_HEIGHT = 745                     # Window height
    WINDOW_SIZE = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"  # Combined size
    UPDATE_INTERVAL = 1000                  # Update frequency (milliseconds)
    ALWAYS_ON_TOP = True                    # Keep window on top
    APPEARANCE_MODE = "dark"                # GUI theme
    COLOR_THEME = "dark-blue"               # Color scheme
    CORNER_RADIUS = 15                      # Window corner radius
    BORDER_WIDTH = 2                        # Border width
```

#### **🎮 VRChat Integration**
Configure VRChat-specific features:
```python
class NovaPlacement:
    STARTUP_DELAY = 15            # Initial delay before starting placement (seconds)
    DEFAULT_SPEED = 1             # Default movement speed

class VRChatAPI:
    USING_API = False             # Enable/disable VRChat API features
    USERNAME = os.getenv('VRCHAT_EMAIL')     # VRChat email from .env
    PASSWORD = os.getenv('VRCHAT_PASSWORD')  # VRChat password from .env
    AUTO_ACCEPT_FRIEND_REQUESTS = True       # Auto-accept friend requests
    FRIEND_REQUEST_CHECK_INTERVAL = 60       # Check interval (seconds)
    NOTIFICATION_CHECK_INTERVAL = 120        # Notification check interval
    API_COOLDOWN = 30                        # Cooldown between API calls
```

#### **💬 System Messages**
Configure status messages:
```python
class SystemMessages:
    INITIAL_USER_MESSAGE = "Who are you?"   # First conversation starter
    SYSTEM_STARTING = "System Starting"     # VRChat startup message
    THINKING_MESSAGE = "Thinking"           # Processing message
    LISTENING_MESSAGE = "Listening"         # Voice input message
```

#### **🎨 Console Colors**
Customize console output colors:
```python
class ConsoleColors:
    # Various ANSI color codes for different types of console output
    AI_LABEL = "\033[93m"        # AI response label color
    AI_TEXT = "\033[92m"         # AI response text color
    HUMAN_LABEL = "\033[93m"     # Human input label color
    HUMAN_TEXT = "\033[92m"      # Human input text color
    # ... and many more color options
```

### 📁 File Paths
All file locations are centralized:
```python
class FilePaths:
    HISTORY_PATH = "json_files/history.json"                    # Conversation history
    NORMAL_SYSTEM_PROMPT_PATH = "prompts/normal_system_prompt.txt"  # Main system prompt
    # Vision system files (in VisionSystem class):
    # STATE_FILE = "json_files/vision_state.json"
    # LOG_FILE = "json_files/vision_log.json"
    # VISION_PROMPT_PATH = "prompts/vision_prompt.txt"
```

### 🎨 Customizing NOVA's Personality

Edit the system prompt files in the `prompts/` folder:
- `normal_system_prompt.txt` - Default personality and behavior
- `snapchat_system_prompt.txt` - Alternative casual personality mode
- `additional_system_prompt.txt` - Extra context and instructions  
- `vision_prompt.txt` - Instructions for the vision system AI model

### 🎯 Common Configuration Scenarios

**Making NOVA More Creative:**
```python
class LanguageModel:
    LM_TEMPERATURE = 0.9  # Higher = more creative/random
```

**Improving Speech Recognition:**
```python
class WhisperSettings:
    MODEL_SIZE = "small"          # Better accuracy than "base"
    VAD_AGGRESSIVENESS = 2        # More sensitive voice detection
    VOICE_THRESHOLD = 0.8         # Lower = more sensitive to speech
    NUM_PADDING_FRAMES = 15       # More padding for better detection
```

**Reducing Response Time:**
```python
class WhisperSettings:
    MODEL_SIZE = "tiny"           # Faster but less accurate

class ResourceMonitor:
    UPDATE_INTERVAL = 2000        # Less frequent GUI updates
```

**Using OpenAI Instead of Local Models:**
```python
# NOVA AI now uses Together AI exclusively
# To change models, update the MODEL_ID in constants.py
class LanguageModel:
    MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct-Turbo"  # Change to any Together AI model
```

**Enabling VRChat API Features:**
```python
class VRChatAPI:
    USING_API = True              # Enable VRChat API integration
    AUTO_ACCEPT_FRIEND_REQUESTS = True  # Automatically accept friend requests
    FRIEND_REQUEST_CHECK_INTERVAL = 30  # Check more frequently
```

**Enabling Vision Capabilities:**
```python
class VisionSystem:
    ENABLED = True                # Enable vision system
    ANALYSIS_INTERVAL = 10        # More frequent analysis
    VISION_MODEL = "meta-llama/Llama-Vision-Free"  # Together AI vision model
```

### 🔧 Advanced Configuration

**Custom Voice Selection:**
- NOVA uses Microsoft Edge TTS voices (no separate script needed)
- Update the `VOICE_NAME` in constants.py with your preferred voice
- Common voices: "en-US-JennyNeural", "en-US-GuyNeural", "en-US-AriaNeural"

**VRChat API Configuration:**
- Set up `.env` file with VRChat credentials for API features
- Enable `USING_API = True` in the `VRChatAPI` class
- Customize friend request and notification handling intervals

**Vision System Setup:**
- Enable `ENABLED = True` in the `VisionSystem` class
- Adjust `ANALYSIS_INTERVAL` for screenshot frequency
- Configure `VISION_MODEL` for your preferred AI vision model

**Network Troubleshooting:**
- `VRC_PORT` is auto-detected but can be manually set if needed
- `LOCAL_IP` is automatically determined using system network configuration

**Performance Optimization:**
- Adjust `UPDATE_INTERVAL` in ResourceMonitor for monitoring frequency
- Modify Whisper settings for balance between accuracy and speed
- Configure vision system intervals based on your hardware capabilities

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

**API Connection errors:**
- Verify your API keys are set correctly in the `.env` file
- **For Together AI**: Verify your API key is valid and has sufficient credits
- Check console output for specific error messages
- Ensure your internet connection is stable

**Microphone not working:**
- Check Windows microphone permissions
- Verify the microphone works in other applications
- Run `python list_audio_devices.py` and update indices in the `Audio` class
- Adjust `WhisperSettings.VAD_AGGRESSIVENESS` for better voice detection
- Try different `VOICE_THRESHOLD` values (lower = more sensitive)

**VRChat API Issues:**
- Ensure `USING_API = True` in `constants.py` if you want API features
- Verify VRChat credentials are correct in the `.env` file
- Check if your VRChat account has two-factor authentication enabled
- Monitor console output for API-specific error messages
- Disable API features by setting `USING_API = False` if not needed

**Vision System Issues:**
- Ensure `ENABLED = True` in the `VisionSystem` class to use vision features
- Verify VRChat window is visible and active during operation
- Check that your Together AI API key is valid
- Monitor console output for vision-specific error messages
- Test with different `ANALYSIS_INTERVAL` values for your hardware

**Resource Monitor Issues:**
- The resource monitor runs as a separate process
- If it fails to start, check console output for error messages

**Multilingual Issues:**
- **Speech not recognized in your language**: Try using a larger Whisper model (`small`, `medium`, or `large`) in `WhisperSettings.MODEL_SIZE`
- **TTS voice not working**: Ensure the voice name is correct in `Voice.VOICE_NAME` - run the voice listing script to see available voices
- **Wrong language detection**: Whisper may detect the wrong language if audio quality is poor - try speaking more clearly or adjusting microphone settings
- **Mixed language responses**: For better multilingual support, use multilingual TTS voices (ones with "Multilingual" in the name)
- **Character encoding issues**: Ensure your terminal supports UTF-8 encoding for non-Latin scripts (Chinese, Arabic, etc.)

### Getting Help

1. Check the console output for error messages - NOVA provides detailed colored output
2. Verify all dependencies are installed correctly using `pip list`
3. Ensure your `.env` file is properly configured with valid credentials
4. Test each component individually:
   - Audio devices: `python list_audio_devices.py`
   - Basic functionality: Start with minimal configuration
5. Check that Together AI is accessible and your API key is valid
6. Review the configuration in `constants.py` for any syntax errors

## Advanced Setup

### Virtual Audio Cables (Optional)

For advanced audio routing and streaming setups:
1. Install VB-Audio Virtual Cable
2. Configure audio routing through virtual cables  
3. Update audio device indices in the `Audio` class in `constants.py`
4. This allows you to separate NOVA's audio from your main audio streams

### Custom System Prompts

Create custom personalities by editing files in the `prompts/` directory:
- **normal_system_prompt.txt**: Main personality and behavior instructions
- **snapchat_system_prompt.txt**: Alternative casual personality mode
- **additional_system_prompt.txt**: Extra context and instructions  
- **vision_prompt.txt**: Instructions for the vision AI model

### Local vs Cloud AI Models

**Using Together AI (Default - Recommended):**
- Sign up at [api.together.xyz](https://api.together.xyz)
- Get your API key from the dashboard
- Set `LLM_API_KEY=your-together-key` in your `.env` file
- Keep default `constants.py` settings (already configured for Together AI)
- Enjoy fast inference with competitive pricing and access to cutting-edge open-source models

### Multi-Instance Setup

Running multiple NOVA instances:
1. Create separate project folders
2. Use different OSC ports for each instance
3. Configure different audio devices if needed
4. Modify `VRC_PORT` in `constants.py` for each instance

### Development Environment

For developers wanting to extend NOVA:
1. Install development dependencies: `pip install flake8`
2. Follow Python PEP 8 style guidelines  
3. Use the modular class structure in the `classes/` folder
4. Test changes thoroughly before deployment



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
