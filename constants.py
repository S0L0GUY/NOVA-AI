import os
import socket

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLM_API:
    """
    LLM API configuration settings for Together AI.
    """

    # Base URL for Together AI API
    BASE_URL = "https://api.together.xyz/v1"
    # API key for Together AI
    API_KEY = os.getenv("LLM_API_KEY")


class Vision_API:
    """
    Vision API configuration settings for Together AI.
    """

    # Base URL for Together AI Vision API
    BASE_URL = "https://api.together.xyz/v1"
    # API key for Together AI Vision
    API_KEY = os.getenv("VISION_API_KEY")


class VRChatAPI:
    """
    Configuration settings for VRChat API integration.
    """

    # Master switch to enable/disable all VRChat API functionality
    USING_API = False  # Set to True to enable API usage

    # VRChat account credentials (loaded from environment variables)
    USERNAME = os.getenv("VRCHAT_EMAIL")
    PASSWORD = os.getenv("VRCHAT_PASSWORD")

    # User agent string as per VRChat Usage Policy
    USER_AGENT = f"NOVA-AI/2025.7.1 {os.getenv('VRCHAT_EMAIL')}"

    # API check intervals (seconds)
    FRIEND_REQUEST_CHECK_INTERVAL = 60  # 1 minute
    NOTIFICATION_CHECK_INTERVAL = 120  # 2 minutes

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


class LanguageModel:
    """
    A class representing configuration settings for a language model.
    This class contains constant values that define the behavior and identity
    of the language model being used.
    Attributes:
        MODEL_ID (str): The identifier for the specific language model being
        used. Default is set to Meta-Llama 3.3 70B Instruct Turbo from
        Together AI.
        LM_TEMPERATURE (float): The temperature parameter for the language
        model's output.
    """

    MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    LM_TEMPERATURE = 0.7


class VisionSystem:
    """
    Configuration settings for the VRChat vision system.
    """

    # Whether vision system is enabled
    ENABLED = False
    # How often to analyze screenshots continuously (seconds)
    ANALYSIS_INTERVAL = 60
    # Maximum image size for API calls (pixels)
    MAX_IMAGE_SIZE = 1024
    # JPEG quality for screenshots (1-100)
    IMAGE_QUALITY = 85
    # Vision state file path
    STATE_FILE = "json_files/vision_state.json"
    # Vision log file path
    LOG_FILE = "json_files/vision_log.json"
    # Vision prompt file path
    VISION_PROMPT_PATH = "prompts/vision_prompt.txt"
    # Maximum number of vision updates to keep in log
    MAX_LOG_ENTRIES = 5
    # VRChat window search keywords
    WINDOW_KEYWORDS = ["VRChat", "vrchat"]
    # Vision model to use (adjust for your local setup)
    VISION_MODEL = "meta-llama/Llama-Vision-Free"
    # Maximum tokens for vision API response
    MAX_VISION_TOKENS = 90
    # Temperature for vision analysis
    VISION_TEMPERATURE = 0.3


class Network:
    """
    Class representing network configuration parameters.
    Attributes:
        LOCAL_IP (str): The local IP address of the computer running the
        application.
        VRC_PORT (int): The port number used for VRChat communication. Default
        is 9000.
    """

    LOCAL_IP = socket.gethostbyname(socket.gethostname())
    VRC_PORT = 9000


class Audio:
    """
    A class containing audio device configuration constants.
    This class defines constants for audio input and output device indices,
    specifically for VB-Audio Cable virtual audio devices.
    Attributes:
        AUDIO_OUTPUT_INDEX (int): The device index for audio output,
            configured for VB-Audio Cable B Input
        AUDIO_INPUT_INDEX (int): The device index for audio input,
            configured for VB-Audio Cable A Output
    """

    AUDIO_OUTPUT_INDEX = 8
    AUDIO_INPUT_INDEX = 4


class Voice:
    """
    A class that defines constants for voice-related configurations in
    Text-to-Speech operations through edge-tts.
    Attributes:
        VOICE_NAME (str): The default voice name used for text-to-speech
        synthesis.
    """

    VOICE_NAME = "en-US-EmmaMultilingualNeural"


class FilePaths:
    """
    A class containing file path constants used in the application.
    Attributes:
        HISTORY_PATH (str): The path to the JSON file storing history data.
                           Default is "json_files/history.json"
    """

    HISTORY_PATH = "json_files/history.json"

    NORMAL_SYSTEM_PROMPT_PATH = "prompts/normal_system_prompt.txt"


class WhisperSettings:
    """
    Configuration for Whisper speech recognition.
    """

    # Whisper model size ("tiny", "base", "small", "medium", "large")
    MODEL_SIZE = "tiny"
    # Sample rate for audio processing
    SAMPLE_RATE = 16000
    # Frame duration in milliseconds for VAD
    FRAME_DURATION_MS = 30
    # Number of padding frames for voice detection
    NUM_PADDING_FRAMES = 10
    # Threshold ratio of voiced frames needed to start recording
    VOICE_THRESHOLD = 0.9
    # Maximum recording duration in seconds
    MAX_RECORDING_DURATION = 30
    # VAD aggressiveness level (0-3, higher = more aggressive)
    VAD_AGGRESSIVENESS = 2


class TTSSettings:
    """
    Text-to-Speech configuration settings.
    """

    # Default TTS engine (edge-tts is currently the only supported engine)
    ENGINE = "edge-tts"
    # Audio bit depth conversion factor for pydub
    AUDIO_CONVERSION_FACTOR = 2**15
    # Sleep interval for queue processing (seconds)
    QUEUE_SLEEP_INTERVAL = 0.1


class SystemMessages:
    """
    System status messages and startup text.
    """

    # Initial conversation starter
    INITIAL_USER_MESSAGE = "Who are you?"
    # VRChat status messages
    SYSTEM_STARTING = "System Starting"
    THINKING_MESSAGE = "Thinking"
    LISTENING_MESSAGE = "Listening"
    # Console status messages
    PROGRAM_STARTING = "Program Starting..."


class NovaPlacement:
    """
    VRChat avatar movement and placement configuration.
    """

    # Initial delay before starting placement (seconds)
    STARTUP_DELAY = 15
    # Default movement speed
    DEFAULT_SPEED = 1


class ConsoleColors:
    """
    ANSI color codes for console output.
    """

    # Text colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    PURPLE = "\033[38;5;55m"
    GRAY = "\033[38;5;92m"
    RESET = "\033[0m"

    # AI/Human conversation colors
    AI_LABEL = "\033[93m"
    AI_TEXT = "\033[92m"
    HUMAN_LABEL = "\033[93m"
    HUMAN_TEXT = "\033[92m"

    # TTS status colors
    TTS_INFO = "\033[93m"
    TTS_WARNING = "\033[91m"

    # System status colors
    SYSTEM_INFO = "\033[36m"
    ERROR = "\033[91m"
