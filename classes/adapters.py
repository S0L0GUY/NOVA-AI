import logging
import warnings
from typing import Optional

from google import genai

import constants as constant
from classes.edge_tts import TextToSpeechManager
from classes.head_tracker import HeadTracker, create_head_tracker
from classes.osc import VRChatOSC
from classes.speech_to_text import SpeechToTextHandler
from classes.vision_manager import VisionManager
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
            device_index=constant.Audio.AUDIO_OUTPUT_INDEX,
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


def create_head_tracker(osc: Optional[VRChatOSC]) -> Optional[HeadTracker]:
    """Adapter to create and start the head tracker for natural avatar movement."""
    try:
        if not osc:
            warnings.warn("\033[91mHead tracker requires OSC. Continuing without head tracking (adapters).\033[0m")
            return None

        tracker = create_head_tracker(osc)

        # Configure from constants if available
        if hasattr(constant, 'NovaPlacement'):
            # Could load custom settings here
            pass

        tracker.start()
        print("\033[92mHead Tracker Initialized Successfully (adapters).\033[0m")
        return tracker
    except Exception as e:
        logging.error(f"\033[91mFailed to create HeadTracker: {e}\033[0m")
        warnings.warn("\033[91mHead tracker initialization failed. Continuing without it (adapters).\033[0m")
        return None


def create_genai_client() -> Optional[genai.Client]:
    """Adapter to construct the Google GenAI client.

    Supports multiple LLM providers via environment variables:
    - GOOGLE_GENAI_API_KEY: Use Google GenAI (default)
    - LM_STUDIO_BASE_URL: Use LM Studio (OpenAI-compatible API)
    - OPENAI_API_KEY: Use OpenAI or compatible API
    """
    import os

    # Check for LM Studio first
    lm_studio_url = os.getenv("LM_STUDIO_BASE_URL")
    if lm_studio_url:
        print(f"[LM Studio] Detected LM_STUDIO_BASE_URL: {lm_studio_url}")
        try:
            from openai import OpenAI
            # Create an OpenAI-compatible client for LM Studio
            client = OpenAI(
                base_url=lm_studio_url,
                api_key="lm-studio",  # LM Studio doesn't require a real key
            )
            print("\033[92mLM Studio Client Initialized Successfully (adapters).\033[0m")
            # Store the client type for later use
            client._nova_provider = "lm_studio"
            return client
        except Exception as e:
            logging.error(f"\033[91mFailed to initialize LM Studio client: {e}\033[0m")
            warnings.warn("\033[91mLM Studio client initialization failed. Falling back to GenAI (adapters).\033[0m")

    # Default to Google GenAI
    try:
        client = genai.Client(api_key=constant.LLM_API.API_KEY)
        return client
    except Exception as e:
        logging.error(f"\033[91mFailed to initialize GenAI client: {e}\033[0m")
        warnings.warn("\033[91mGenAI client initialization failed. LLM features disabled (adapters).\033[0m")
        return None
