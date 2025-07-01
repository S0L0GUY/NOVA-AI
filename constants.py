import socket


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
    AUDIO_OUTPUT_INDEX = 6
    AUDIO_INPUT_INDEX = 2  # 12 25 36


class Voice:
    """
    A class that defines constants for voice-related configurations in
    Text-to-Speech (TTS) operations.
    Attributes:
        VOICE_NAME (str): The default voice name used for text-to-speech
        synthesis. Currently set to "Zira".
    """
    VOICE_NAME = "en-US-JennyNeural"


class LanguageModel:
    """
    A class representing configuration settings for a language model.
    This class contains constant values that define the behavior and identity
    of the language model being used.
    Attributes:
        MODEL_ID (str): The identifier for the specific language model being
        used. Currently set to Meta-Llama 3.1 8B Instruct GGUF model.
        LM_TEMPERATURE (float): The temperature parameter for the language
        model's output. Controls randomness in text generation (0.0 to 1.0,
        where higher means more random).
    """
    MODEL_ID = "meta-llama-3.1-8b-instruct"
    LM_TEMPERATURE = 0.7


class FilePaths:
    """
    A class containing file path constants used in the application.
    Attributes:
        HISTORY_PATH (str): The path to the JSON file storing history data.
                           Default is "json_files/history.json"
    """
    HISTORY_PATH = "json_files/history.json"

    NORMAL_SYSTEM_PROMPT_PATH = "prompts/normal_system_prompt.txt"


class OpenAI:
    """
    OpenAI API configuration settings.
    """
    # Base URL for OpenAI API (change for local LM Studio)
    BASE_URL = "http://localhost:1234/v1"
    # API key for OpenAI (use "lm-studio" for local)
    API_KEY = "lm-studio"
    # Whether to use streaming responses
    STREAM_RESPONSES = True


class WhisperSettings:
    """
    Configuration for Whisper speech recognition.
    """
    # Whisper model size ("tiny", "base", "small", "medium", "large")
    MODEL_SIZE = "base"
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
    VAD_AGGRESSIVENESS = 0


class TTSSettings:
    """
    Text-to-Speech configuration settings.
    """
    # Default TTS engine ("edge-tts")
    ENGINE = "edge-tts"
    # Audio bit depth conversion factor for pydub
    AUDIO_CONVERSION_FACTOR = 2**15
    # Sleep interval for queue processing (seconds)
    QUEUE_SLEEP_INTERVAL = 0.1


class InterruptionSettings:
    """
    Configuration settings for voice interruption detection during TTS
    playback.

    Attributes:
        ENABLED (bool): Whether interruption detection is enabled
        SENSITIVITY (float): Detection sensitivity (1.0 = normal,
                           higher = more sensitive)
        DETECTION_DELAY (float): Seconds to wait before starting detection
        SPEECH_THRESHOLD (int): Consecutive speech frames needed to trigger
                              interruption
        AUDIO_LEVEL_MULTIPLIER (float): Multiplier for baseline audio level
                                      detection
    """
    ENABLED = True
    # Adjust this: 0.5 = less sensitive, 2.0 = more sensitive
    SENSITIVITY = 1.0
    DETECTION_DELAY = 1.0  # Wait 1 second before starting detection
    SPEECH_THRESHOLD = 8  # Number of consecutive speech frames needed
    # Audio must be 2.5x baseline to trigger
    AUDIO_LEVEL_MULTIPLIER = 2.5
    # Sample rate for interruption detection
    SAMPLE_RATE = 16000
    # Frame duration for interruption detection (ms)
    FRAME_DURATION_MS = 30
    # Frames of silence needed to reset speech counter
    SILENCE_THRESHOLD = 5
    # Initial calibration frames to establish baseline
    CALIBRATION_FRAMES = 30
    # Maximum audio level buffer size
    MAX_AUDIO_LEVEL_BUFFER = 50
    # Fallback audio level multiplier when VAD fails
    FALLBACK_AUDIO_MULTIPLIER = 4.0
    # Final threshold multiplier for interruption trigger
    FINAL_THRESHOLD_MULTIPLIER = 3.0
    # Sleep interval for detection loop (seconds)
    DETECTION_SLEEP_INTERVAL = 0.1
    # Delay before starting detection (seconds)
    STARTUP_DELAY = 0.5


class SystemMessages:
    """
    System status messages and startup text.
    """
    # Initial conversation starter
    INITIAL_USER_MESSAGE = "hi"
    # VRChat status messages
    SYSTEM_STARTING = "System Starting"
    THINKING_MESSAGE = "Thinking"
    LISTENING_MESSAGE = "Listening"
    # Console status messages
    PROGRAM_STARTING = "Program Starting..."
    RESOURCE_MONITOR_STARTING = "Starting resource monitor..."


class ErrorHandling:
    """
    Error handling and recovery settings.
    """
    # Sleep time after error before retry (seconds)
    ERROR_RETRY_DELAY = 5
    # Exit code when no models are available
    NO_MODELS_EXIT_CODE = 1


class ResourceMonitor:
    """
    Resource monitor GUI configuration.
    """
    WINDOW_TITLE = "Nova Resource Monitor"
    # Window geometry
    WINDOW_WIDTH = 400
    WINDOW_HEIGHT = 745
    WINDOW_SIZE = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
    # GUI update interval (milliseconds)
    UPDATE_INTERVAL = 1000
    # Window always on top
    ALWAYS_ON_TOP = True
    # GUI theme settings
    APPEARANCE_MODE = "dark"
    COLOR_THEME = "dark-blue"
    # Frame styling
    CORNER_RADIUS = 15
    BORDER_WIDTH = 2
    PADDING_Y = 10
    PADDING_X = 20
    # Font settings
    TITLE_FONT_SIZE = 18
    VALUE_FONT_SIZE = 24
    FONT_FAMILY = "Segoe UI"
    # Label padding
    TITLE_PADDING = (10, 5)
    VALUE_PADDING = (0, 10)
    # Color scheme for different stats
    CPU_COLOR = "dark blue"
    RAM_COLOR = "dark violet"
    DISK_COLOR = "dark red"
    GPU_COLOR = "dark cyan"
    GPU_MEM_COLOR = "purple4"
    NETWORK_COLOR = "dark green"
    UPTIME_COLOR = "dark gray"


class NovaPlacement:
    """
    VRChat avatar movement and placement configuration.
    """
    # Initial delay before starting placement (seconds)
    STARTUP_DELAY = 15
    # Default movement speed
    DEFAULT_SPEED = 1
    # Movement sequence timings (seconds)
    MOVE_FORWARD_1 = 3
    LOOK_RIGHT_1 = 0.4
    MOVE_FORWARD_2 = 5.5
    LOOK_LEFT_1 = 0.4
    MOVE_FORWARD_3 = 4.5
    LOOK_LEFT_2 = 0.3
    MOVE_FORWARD_4 = 2.9
    LOOK_RIGHT_2 = 0.2
    MOVE_FORWARD_5 = 0.5
    LOOK_RIGHT_3 = 0.3
    MOVE_FORWARD_6 = 1.2
    LOOK_RIGHT_4 = 0.33
    MOVE_FORWARD_7 = 0.3


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


class VisionSystem:
    """
    Configuration settings for the VRChat vision system.
    """
    # Whether vision system is enabled
    ENABLED = False
    # How often to analyze screenshots continuously (seconds)
    ANALYSIS_INTERVAL = 15
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
    VISION_MODEL = "qwen/qwen2.5-vl-7b"
    # Maximum tokens for vision API response
    MAX_VISION_TOKENS = 150
    # Temperature for vision analysis
    VISION_TEMPERATURE = 0.3
