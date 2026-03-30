import logging
import warnings
from typing import Optional, Union

from google import genai

import constants as constant
from classes.edge_tts_wrapper import TextToSpeechManager
from classes.head_tracker import HeadTracker, create_head_tracker as _create_head_tracker
from classes.osc import VRChatOSC
from classes.speech_to_text import SpeechToTextHandler
from classes.vision_manager import VisionManager
from classes.vrchat_api import VRChatAPIManager


def create_lmstudio_client():
    """Adapter to construct the LM Studio OpenAI-compatible client."""
    if not constant.LMStudioConfig.ENABLED:
        return None
    
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=constant.LMStudioConfig.BASE_URL,
            api_key=constant.LMStudioConfig.API_KEY,
        )
        print("\033[92mLM Studio client initialized successfully (adapters).\033[0m")
        return client
    except ImportError:
        logging.error("\033[91mOpenAI package not installed. Install with: pip install openai\033[0m")
        return None
    except Exception as e:
        logging.error(f"\033[91mFailed to initialize LM Studio client: {e}\033[0m")
        warnings.warn("\033[91mLM Studio initialization failed. Falling back to GenAI (adapters).\033[0m")
        return None


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
        VisionManager.clear_vision_history()
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
            VRChatOSC=osc,
        )
        tts.initialize_tts_engine()
        return tts
    except Exception as e:
        logging.error(f"\033[91mFailed to create TTS manager: {e}\033[0m")
        warnings.warn("\033[91mTTS initialization failed. Continuing without TTS (adapters).\033[0m")
        return None


def create_vision_manager() -> Optional[VisionManager]:
    """Adapter to create and start the vision manager."""
    try:
        vision_manager = VisionManager()
        vision_manager.start_vision_system()
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


def create_head_tracker(osc: Optional[VRChatOSC]) -> Optional[HeadTracker]:
    """Adapter to create and initialize the head tracker."""
    if not osc:
        logging.warning("\033[93mOSC not available. Head tracker disabled (adapters).\033[0m")
        return None

    try:
        head_tracker = _create_head_tracker(osc)
        print("\033[92mHead Tracker initialized successfully (adapters).\033[0m")
        return head_tracker
    except Exception as e:
        logging.error(f"\033[91mFailed to create Head Tracker: {e}\033[0m")
        warnings.warn("\033[91mHead Tracker initialization failed. Continuing without head tracking (adapters).\033[0m")
        return None
