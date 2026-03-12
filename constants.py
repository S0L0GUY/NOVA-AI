import os
import socket

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLM_API:
    """LLM API configuration settings for Together AI / GenAI."""

    BASE_URL = "https://api.together.xyz/v1"
    API_KEY = os.getenv("LLM_API_KEY")


class LMStudioConfig:
    """LM Studio local LLM configuration."""

    ENABLED = os.getenv("LM_STUDIO_ENABLED", "false").lower() == "true"
    BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
    MODEL = os.getenv("LM_STUDIO_MODEL", "local-model")
    API_KEY = os.getenv("LM_STUDIO_API_KEY", "not-needed")
    TEMPERATURE = float(os.getenv("LM_STUDIO_TEMPERATURE", "0.8"))
    MAX_TOKENS = int(os.getenv("LM_STUDIO_MAX_TOKENS", "10000"))


class Vision_API:
    """Vision API configuration settings."""

    BASE_URL = "https://api.together.xyz/v1"
    API_KEY = os.getenv("VISION_API_KEY")


class VRChatAPI:
    """Configuration settings for VRChat API integration."""

    USING_API = False
    USERNAME = os.getenv("VRCHAT_EMAIL")
    PASSWORD = os.getenv("VRCHAT_PASSWORD")
    USER_AGENT = f"NOVA-AI/2025.7.1 {os.getenv('VRCHAT_EMAIL')}"
    FRIEND_REQUEST_CHECK_INTERVAL = 60
    NOTIFICATION_CHECK_INTERVAL = 120
    API_COOLDOWN = 30
    AUTO_ACCEPT_FRIEND_REQUESTS = True
    ENABLE_NOTIFICATION_CHECKS = True
    ENABLE_FRIEND_REQUEST_CHECKS = True
    CONNECTION_TIMEOUT = 30
    REQUEST_TIMEOUT = 15
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 5
    VERBOSE_LOGGING = False


class LanguageModel:
    """Language model configuration."""

    MODEL_ID = "gemini-2.5-flash"


class VisionSystem:
    """Configuration settings for the VRChat vision system."""

    ENABLED = False
    ANALYSIS_INTERVAL = 60
    MAX_IMAGE_SIZE = 1024
    IMAGE_QUALITY = 85
    STATE_FILE = "json_files/vision_state.json"
    LOG_FILE = "json_files/vision_log.json"
    VISION_PROMPT_PATH = "prompts/vision_prompt.txt"
    MAX_LOG_ENTRIES = 5
    WINDOW_KEYWORDS = ["VRChat", "vrchat"]
    VISION_MODEL = "gemini-2.5-flash"
    MAX_VISION_TOKENS = 90
    VISION_TEMPERATURE = 0.3


class Network:
    """Network configuration parameters."""

    LOCAL_IP = socket.gethostbyname(socket.gethostname())
    VRC_PORT = 9000


class Audio:
    """Audio device configuration constants."""

    AUDIO_OUTPUT_INDEX = 9
    AUDIO_INPUT_INDEX = 18


class Voice:
    """Voice configuration for edge-tts."""

    VOICE_NAME = "en-US-EmmaMultilingualNeural"


class FilePaths:
    """File path constants used throughout the application."""

    HISTORY_PATH = "json_files/history.json"
    NORMAL_SYSTEM_PROMPT_PATH = "prompts/normal_system_prompt.txt"
    MEMORY_FILE = "json_files/memory.json"
    PERSONALITIES_FILE = "personalities.json"
    SESSION_FILE = "json_files/last_session.json"
    SFX_DIR = "sfx"


class SpeechRecognitionConfig:
    """Configuration for speech recognition (Whisper and GenAI)."""

    MODEL_SIZE = "base"
    SAMPLE_RATE = 16000
    FRAME_DURATION_MS = 30
    NUM_PADDING_FRAMES = 10
    VOICE_THRESHOLD = 0.9
    MAX_RECORDING_DURATION = 30
    VAD_AGGRESSIVENESS = 1
    QUEUED_MODEL = "whisper"


class TTSSettings:
    """Text-to-Speech configuration settings."""

    ENGINE = "edge-tts"
    AUDIO_CONVERSION_FACTOR = 2**15
    QUEUE_SLEEP_INTERVAL = 0.1
    ENABLE_CACHING = True
    CACHE_DIR = "tts_cache"


class SystemMessages:
    """System status messages and startup text."""

    INITIAL_USER_MESSAGE = "Hi"
    SYSTEM_STARTING = "System Starting"
    THINKING_MESSAGE = "Thinking"
    LISTENING_MESSAGE = "Listening"
    PROGRAM_STARTING = "Program Starting..."


class NovaPlacement:
    """VRChat avatar movement and placement configuration."""

    STARTUP_DELAY = 15
    DEFAULT_SPEED = 1


class ConsoleColors:
    """ANSI color codes for console output."""

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    PURPLE = "\033[38;5;55m"
    GRAY = "\033[38;5;92m"
    RESET = "\033[0m"

    AI_LABEL = "\033[93m"
    AI_TEXT = "\033[92m"
    HUMAN_LABEL = "\033[93m"
    HUMAN_TEXT = "\033[92m"

    TTS_INFO = "\033[93m"
    TTS_WARNING = "\033[91m"

    SYSTEM_INFO = "\033[36m"
    ERROR = "\033[91m"


class SupervisorConfig:
    """
    Configuration for the process supervisor that keeps NOVA alive on crashes.
    """

    # Seconds to wait before restarting a crashed process
    RESTART_DELAY = 5
    # Maximum restart attempts – None means unlimited
    MAX_RESTART_ATTEMPTS = None
    # Path to the supervisor log file
    LOG_FILE = "supervisor.log"


class SessionPersistenceConfig:
    """
    Configuration for persisting session handles across restarts so the
    conversation context is not lost after an unexpected shutdown.
    """

    # Enable session persistence
    ENABLED = True
    # Seconds between periodic saves
    SAVE_INTERVAL = 30


class IdleGazeConfig:
    """
    Configuration for the idle-gaze behaviour – NOVA subtly tracks nearby
    players when not actively speaking, using YOLO-based player detection.
    """

    # Enable idle gaze (requires a compatible vision back-end)
    ENABLED = True
    # Fraction of screen width treated as a no-turn deadzone
    DEADZONE_FRACTION = 0.03
    # Polling interval in seconds between frame checks
    POLL_INTERVAL = 0.06
    # Seconds after speech ends before idle gaze resumes
    COOLDOWN_AFTER_SPEECH = 30.0


class MovementConfig:
    """
    Configuration for full avatar movement via OSC inputs (ported from Gabriel).
    Supports turning, walking, jumping, crouching, and crawling.
    """

    # Use axis-based turning instead of discrete left/right buttons
    USE_AXIS = False
    # Axis value intensity when turning (only used if USE_AXIS is True)
    AXIS_TURN_VALUE = 1.0
    # Default duration for a single look-turn (seconds)
    TURN_DURATION_DEFAULT = 1.0
    # Duration range for look-behind randomisation
    LOOK_BEHIND_MIN = 0.3
    LOOK_BEHIND_MAX = 0.3
    # Randomise left/right direction on look-behind
    RANDOMIZE_BACK_TURN = True
    # Default movement duration in seconds
    MOVE_DURATION_DEFAULT = 1.0
    # Allow holding Run during moves
    ALLOW_RUN = True
    # Hold run by default when move_direction() is called without explicit run=
    RUN_BY_DEFAULT = False
    # Duration for keyboard tap actions such as crouch (C) and crawl (Z)
    KEY_TAP_DURATION = 0.05


class SFXConfig:
    """
    Configuration for the sound-effects subsystem.
    NOVA scans the sfx/ directory and can play files on request.
    """

    # Enable SFX playback
    ENABLED = True
    # Default volume level (0.0 – 1.0)
    DEFAULT_VOLUME = 0.7
    # Supported audio file extensions
    SUPPORTED_FORMATS = {".mp3", ".wav", ".ogg", ".m4a", ".aac", ".flac", ".wma"}
    # Name of the on-disk cache index inside the SFX directory
    CACHE_FILENAME = "sfx_cache.json"


class PersonalityConfig:
    """
    Configuration for the dynamic personality switching system.
    Personalities are stored in personalities.json and can be switched at runtime.
    """

    # Enable personality switching
    ENABLED = True
    # Default personality ID loaded on startup – empty string means none
    DEFAULT_PERSONALITY = ""
