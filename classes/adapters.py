"""
Adapters module for NOVA-AI.

Provides factory functions that safely construct every component the main
loop needs.  Each function handles its own error logging and returns None
(or a safe default) on failure so the rest of the application can continue
without the failed component.

New features ported from Project Gabriel are wired in here:
- Supervisor (process watchdog)
- SessionPersistenceManager
- MovementController
- SFXManager
- PersonalityManager
- IdleGazeController
"""

import logging
import warnings
from typing import Optional, Union

from google import genai

import constants as constant
from classes.edge_tts import TextToSpeechManager
from classes.head_tracker import HeadTracker
from classes.head_tracker import create_head_tracker as _create_head_tracker
from classes.idle_gaze import IdleGazeController, get_idle_gaze_controller
from classes.movement import MovementController, initialize_movement
from classes.osc import VRChatOSC
from classes.personality_manager import PersonalityManager, get_personality_manager
from classes.session_persistence import SessionPersistenceManager, get_persistence_manager
from classes.sfx_manager import SFXManager, get_sfx_manager
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
        print("\033[92mLM Studio client initialised successfully (adapters).\033[0m")
        return client
    except ImportError:
        logging.error(
            "\033[91mOpenAI package not installed. Install with: pip install openai\033[0m"
        )
        return None
    except Exception as exc:
        logging.error(f"\033[91mFailed to initialise LM Studio client: {exc}\033[0m")
        warnings.warn("\033[91mLM Studio init failed. Falling back to GenAI (adapters).\033[0m")
        return None


def initialize_osc() -> Optional[VRChatOSC]:
    """Adapter to initialise VRChat OSC safely."""
    print("Initialising OSC (adapters)...")
    try:
        osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)
        osc.send_message("System Starting")
        osc.set_typing_indicator(True)
        print("\033[92mOSC Initialised Successfully (adapters).\033[0m")
        return osc
    except Exception as exc:
        logging.error(f"\033[91mFailed to initialise OSC: {exc}\033[0m")
        warnings.warn("\033[91mOSC init failed. Continuing without OSC (adapters).\033[0m")
        return None


def create_vrchat_api_manager() -> None:
    """Adapter wrapper to create the VRChat API manager."""
    print("Creating VRChat API Manager (adapters)...")
    try:
        VisionManager.clear_vision_history()
        VRChatAPIManager.create_vrchat_api_manager()
        print("\033[92mVRChat API Manager Created Successfully (adapters).\033[0m")
    except Exception as exc:
        logging.error(f"\033[91mFailed to create VRChat API Manager: {exc}\033[0m")
        warnings.warn(
            "\033[91mVRChat API Manager creation failed. Continuing without it (adapters).\033[0m"
        )
        return None


def create_transcriber() -> Optional[SpeechToTextHandler]:
    """Adapter to create speech transcriber."""
    try:
        return SpeechToTextHandler()
    except Exception as exc:
        logging.error(f"\033[91mFailed to create SpeechToTextHandler: {exc}\033[0m")
        warnings.warn(
            "\033[91mSpeech transcriber creation failed. Some features may be disabled (adapters).\033[0m"
        )
        return None


def create_tts(osc: Optional[VRChatOSC]) -> Optional[TextToSpeechManager]:
    """Adapter to create and initialise TextToSpeechManager."""
    try:
        tts = TextToSpeechManager(
            voice=constant.Voice.VOICE_NAME,
            device_index=constant.Audio.AUDIO_OUTPUT_INDEX,
            VRChatOSC=osc,
        )
        tts.initialize_tts_engine()
        return tts
    except Exception as exc:
        logging.error(f"\033[91mFailed to create TTS manager: {exc}\033[0m")
        warnings.warn(
            "\033[91mTTS init failed. Continuing without TTS (adapters).\033[0m"
        )
        return None


def create_vision_manager() -> Optional[VisionManager]:
    """Adapter to create and start the vision manager."""
    try:
        vision_manager = VisionManager()
        vision_manager.start_vision_system()
        return vision_manager
    except Exception as exc:
        logging.error(f"\033[91mFailed to create VisionManager: {exc}\033[0m")
        warnings.warn(
            "\033[91mVision system failed to start. Continuing without vision (adapters).\033[0m"
        )
        return None


def create_genai_client() -> Optional[genai.Client]:
    """Adapter to construct the Google GenAI client."""
    try:
        client = genai.Client(api_key=constant.LLM_API.API_KEY)
        return client
    except Exception as exc:
        logging.error(f"\033[91mFailed to initialise GenAI client: {exc}\033[0m")
        warnings.warn(
            "\033[91mGenAI client init failed. LLM features disabled (adapters).\033[0m"
        )
        return None


def create_head_tracker(osc: Optional[VRChatOSC]) -> Optional[HeadTracker]:
    """Adapter to create and initialise the head tracker."""
    if not osc:
        logging.warning("\033[93mOSC not available. Head tracker disabled (adapters).\033[0m")
        return None

    try:
        head_tracker = _create_head_tracker(osc)
        print("\033[92mHead Tracker initialised successfully (adapters).\033[0m")
        return head_tracker
    except Exception as exc:
        logging.error(f"\033[91mFailed to create Head Tracker: {exc}\033[0m")
        warnings.warn(
            "\033[91mHead Tracker init failed. Continuing without head tracking (adapters).\033[0m"
        )
        return None


def create_movement_controller(osc: Optional[VRChatOSC]) -> Optional[MovementController]:
    """
    Adapter to create and initialise the MovementController.

    Args:
        osc (Optional[VRChatOSC]): The OSC client for sending movement inputs.

    Returns:
        Optional[MovementController]: Initialised controller, or None on failure.
    """
    if not osc:
        logging.warning(
            "\033[93mOSC not available – MovementController disabled (adapters).\033[0m"
        )
        return None

    try:
        # Pass the underlying pythonosc client stored inside VRChatOSC
        udp_client = getattr(osc, "client", None)
        controller = initialize_movement(udp_client)
        print("\033[92mMovementController initialised successfully (adapters).\033[0m")
        return controller
    except Exception as exc:
        logging.error(f"\033[91mFailed to create MovementController: {exc}\033[0m")
        warnings.warn(
            "\033[91mMovementController init failed. Movement features disabled (adapters).\033[0m"
        )
        return None


def create_sfx_manager() -> Optional[SFXManager]:
    """
    Adapter to create and initialise the SFXManager.

    Returns:
        Optional[SFXManager]: Initialised manager, or None on failure.
    """
    if not constant.SFXConfig.ENABLED:
        print("\033[93mSFXManager disabled via config (adapters).\033[0m")
        return None

    try:
        manager = get_sfx_manager()
        print(
            f"\033[92mSFXManager initialised successfully "
            f"({len(manager.audio_cache)} files indexed) (adapters).\033[0m"
        )
        return manager
    except Exception as exc:
        logging.error(f"\033[91mFailed to create SFXManager: {exc}\033[0m")
        warnings.warn(
            "\033[91mSFXManager init failed. SFX features disabled (adapters).\033[0m"
        )
        return None


def create_personality_manager() -> Optional[PersonalityManager]:
    """
    Adapter to create and initialise the PersonalityManager.

    Returns:
        Optional[PersonalityManager]: Initialised manager, or None on failure.
    """
    if not constant.PersonalityConfig.ENABLED:
        print("\033[93mPersonalityManager disabled via config (adapters).\033[0m")
        return None

    try:
        manager = get_personality_manager()

        # Activate default personality if configured
        default = constant.PersonalityConfig.DEFAULT_PERSONALITY
        if default and default in manager.personalities:
            result = manager.switch_personality(default)
            if result.get("success"):
                print(
                    f"\033[92mPersonalityManager: default personality "
                    f"'{default}' activated (adapters).\033[0m"
                )

        print(
            f"\033[92mPersonalityManager initialised successfully "
            f"({len(manager.personalities)} personalities loaded) (adapters).\033[0m"
        )
        return manager
    except Exception as exc:
        logging.error(f"\033[91mFailed to create PersonalityManager: {exc}\033[0m")
        warnings.warn(
            "\033[91mPersonalityManager init failed. Personality features disabled (adapters).\033[0m"
        )
        return None


def create_idle_gaze_controller() -> Optional[IdleGazeController]:
    """
    Adapter to create and start the IdleGazeController.

    Returns:
        Optional[IdleGazeController]: Started controller, or None on failure.
    """
    if not constant.IdleGazeConfig.ENABLED:
        print("\033[93mIdleGazeController disabled via config (adapters).\033[0m")
        return None

    try:
        controller = get_idle_gaze_controller()
        started = controller.start()
        if started:
            print("\033[92mIdleGazeController started successfully (adapters).\033[0m")
        else:
            print("\033[93mIdleGazeController could not start (deps missing or disabled).\033[0m")
        return controller
    except Exception as exc:
        logging.error(f"\033[91mFailed to create IdleGazeController: {exc}\033[0m")
        warnings.warn(
            "\033[91mIdleGazeController init failed. Idle gaze disabled (adapters).\033[0m"
        )
        return None


def create_session_persistence_manager() -> Optional[SessionPersistenceManager]:
    """
    Adapter to create the SessionPersistenceManager.

    Returns:
        Optional[SessionPersistenceManager]: Manager, or None if disabled/failed.
    """
    if not constant.SessionPersistenceConfig.ENABLED:
        print("\033[93mSessionPersistenceManager disabled via config (adapters).\033[0m")
        return None

    try:
        manager = get_persistence_manager(constant.SessionPersistenceConfig.SAVE_INTERVAL)
        print("\033[92mSessionPersistenceManager initialised successfully (adapters).\033[0m")
        return manager
    except Exception as exc:
        logging.error(f"\033[91mFailed to create SessionPersistenceManager: {exc}\033[0m")
        warnings.warn(
            "\033[91mSessionPersistenceManager init failed (adapters).\033[0m"
        )
        return None
