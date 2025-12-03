import logging
import warnings
from typing import Optional

from google import genai

from classes.vision_system import VRChatWindowCapture
import constants as constant
from classes.edge_tts import TextToSpeechManager
from classes.osc import VRChatOSC
from classes.speech_to_text import SpeechToTextHandler
from classes.vrchat_api import VRChatAPIManager


def initialize_osc() -> Optional[VRChatOSC]:
    """Adapter to initialize VRChat OSC safely."""
    print("Initializing OSC (adapters)...")
    try:
        osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)
        osc.send_message("System Starting")
        osc.set_typing_indicator(True)
        print("\033[92mOSC Initialized Successfully (adapters).\033[0m")
        return osc
    except Exception as e:
        logging.error(f"\033[91mFailed to initialize OSC: {e}\033[0m")
        warnings.warn("\033[91mOSC initialization failed. Continuing without OSC (adapters).\033[0m")
        return None


def create_vrchat_api_manager() -> None:
    """Adapter wrapper to create the VRChat API manager."""
    print("Creating VRChat API Manager (adapters)...")
    try:
        VRChatAPIManager.create_vrchat_api_manager()
        print("\033[92mVRChat API Manager Created Successfully (adapters).\033[0m")
    except Exception as e:
        logging.error(f"\033[91mFailed to create VRChat API Manager: {e}\033[0m")
        warnings.warn("\033[91mVRChat API Manager creation failed. Continuing without it (adapters).\033[0m")
        return None


def create_transcriber() -> Optional[SpeechToTextHandler]:
    """Adapter to create speech transcriber."""
    try:
        return SpeechToTextHandler()
    except Exception as e:
        logging.error(f"\033[91mFailed to create SpeechToTextHandler: {e}\033[0m")
        warnings.warn("\033[91mSpeech transcriber creation failed. Some features may be disabled (adapters).\033[0m")
        return None


def create_tts(osc: Optional[VRChatOSC]) -> Optional[TextToSpeechManager]:
    """Adapter to create and initialize TextToSpeechManager."""
    try:
        tts = TextToSpeechManager(
            voice=constant.Voice.VOICE_NAME,
            device_index=constant.Audio.AUDIO_OUTPUT_INDEX,
            VRChatOSC=osc,
        )
        tts.initialize_tts_engine()
        return tts
    except Exception as e:
        logging.error(f"\033[91mFailed to create TTS manager: {e}\033[0m")
        warnings.warn("\033[91mTTS initialization failed. Continuing without TTS (adapters).\033[0m")
        return None


def create_vision_manager() -> Optional[VRChatWindowCapture]:
    """Adapter to create and start the vision manager."""
    # Only create and start the vision manager when the feature is enabled
    if not constant.VisionSystem.ENABLED:
        print("\033[96m[VISION]\033[0m \033[91mVision system disabled in configuration. Skipping startup.\033[0m")
        return None

    try:
        vision_manager = VRChatWindowCapture()
        return vision_manager
    except Exception as e:
        logging.error(f"\033[91mFailed to create VisionManager: {e}\033[0m")
        warnings.warn("\033[91mVision system failed to start. Continuing without vision (adapters).\033[0m")
        return None


def create_genai_client() -> Optional[genai.Client]:
    """Adapter to construct the Google GenAI client."""
    try:
        client = genai.Client(api_key=constant.LLM_API.API_KEY)
        return client
    except Exception as e:
        logging.error(f"\033[91mFailed to initialize GenAI client: {e}\033[0m")
        warnings.warn("\033[91mGenAI client initialization failed. LLM features disabled (adapters).\033[0m")
        return None
