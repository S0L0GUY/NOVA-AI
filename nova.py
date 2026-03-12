"""
Main module for running the application logic.

This module initialises all NOVA-AI components, starts the enhanced
Gabriel-feature subsystems (movement, SFX, personality switching, idle
gaze, session persistence), and enters the main conversation loop.
"""

import datetime
import re
import time
from typing import Iterator, List, Optional

from google import genai

import constants as constant
from classes import adapters, llm_tools
from classes.edge_tts import TextToSpeechManager
from classes.head_tracker import HeadTracker
from classes.idle_gaze import IdleGazeController
from classes.json_wrapper import JsonWrapper
from classes.movement import MovementController
from classes.osc import VRChatOSC
from classes.personality_manager import PersonalityManager
from classes.session_persistence import SessionPersistenceManager
from classes.sfx_manager import SFXManager
from classes.system_prompt import SystemPrompt
from classes.vision_manager import VisionManager


def initialize_history() -> list:
    """
    Builds the initial conversation history including recent memories and
    the system prompt.

    Returns:
        list: Initial history list ready for the LLM client.
    """
    system_prompt = SystemPrompt.get_full_prompt()
    now = datetime.datetime.now()
    history = []
    memories = JsonWrapper().read_dict(file_path=constant.FilePaths.MEMORY_FILE)

    if memories:
        recent_memories = list(memories.items())[-20:]
        for key, value in recent_memories:
            history.append({"role": "system", "content": f"{key}: {value}"})

    history.append({"role": "system", "content": system_prompt})
    history.append({"role": "system", "content": f"Today is {now.strftime('%Y-%m-%d')}"})
    history.append({"role": "user", "content": constant.SystemMessages.INITIAL_USER_MESSAGE})

    return history


def initialize_components() -> tuple:
    """
    Initialises and returns all application components.

    Returns:
        tuple: (osc, transcriber, history, client, tts, vision_manager,
                head_tracker, movement_controller, sfx_manager,
                personality_manager, idle_gaze_controller,
                session_persistence_manager)
    """
    osc = adapters.initialize_osc()
    transcriber = adapters.create_transcriber()
    history = initialize_history()

    client = adapters.create_lmstudio_client()
    if client is None:
        client = adapters.create_genai_client()

    tts = adapters.create_tts(osc)
    vision_manager = adapters.create_vision_manager()
    head_tracker = adapters.create_head_tracker(osc)

    # New Gabriel-feature components
    movement_controller = adapters.create_movement_controller(osc)
    sfx_manager = adapters.create_sfx_manager()
    personality_manager = adapters.create_personality_manager()
    idle_gaze_controller = adapters.create_idle_gaze_controller()
    session_persistence_manager = adapters.create_session_persistence_manager()

    return (
        osc,
        transcriber,
        history,
        client,
        tts,
        vision_manager,
        head_tracker,
        movement_controller,
        sfx_manager,
        personality_manager,
        idle_gaze_controller,
        session_persistence_manager,
    )


def chunk_text(text: Optional[str]) -> List[str]:
    """
    Splits text into sentence-sized chunks for streaming TTS.

    Args:
        text (str): The text to split.

    Returns:
        List[str]: List of sentence chunks.
    """
    if not isinstance(text, str):
        return []
    text = text.strip()
    if not text:
        return []
    return re.split(r"(?<=[.!?])\s+", text)


def generate_contents(history: list) -> list:
    """
    Converts chat-style history into the GenAI SDK 'contents' format.

    Args:
        history (list): List of {'role': ..., 'content': ...} dicts.

    Returns:
        list: List of genai.types.Content objects.
    """
    contents = []
    for msg in history:
        text = msg.get("content", "")
        role = msg.get("role", "user")
        if role != "user":
            role = "model"
        try:
            part = genai.types.Part.from_text(text=text)
            content = genai.types.Content(role=role, parts=[part])
            contents.append(content)
        except (AttributeError, TypeError) as exc:
            print(
                f"Warning: failed to build GenAI content for role '{role}': {exc}. "
                "Appending raw text as fallback."
            )
            contents.append(text)
    return contents


def get_current_model(client: object, vision_manager: VisionManager) -> str:
    """
    Returns the model ID to use based on the active client type.

    Args:
        client: The LLM client (GenAI or LM Studio).
        vision_manager: Unused; kept for API compatibility.

    Returns:
        str: Model identifier string from constants.
    """
    if hasattr(client, "chat"):
        return constant.LMStudioConfig.MODEL
    return constant.LanguageModel.MODEL_ID


def generate_with_client(client, contents, current_model, config=None):
    """
    Unified generation that supports both LM Studio (OpenAI) and GenAI clients.

    Args:
        client: The LLM client instance.
        contents: Conversation contents in the appropriate format.
        current_model (str): Model identifier.
        config: Optional GenAI GenerateContentConfig.

    Returns:
        Response object or streaming iterator.
    """
    if hasattr(client, "chat"):
        # LM Studio / OpenAI-style client
        messages = []
        for content in contents:
            if hasattr(content, "role") and hasattr(content, "parts"):
                role = "assistant" if content.role == "model" else content.role
                text = content.parts[0].text if content.parts else ""
                messages.append({"role": role, "content": text})
            elif isinstance(content, dict):
                role = content.get("role", "user")
                if role == "model":
                    role = "assistant"
                messages.append({"role": role, "content": content.get("content", "")})
            else:
                messages.append({"role": "user", "content": str(content)})

        return client.chat.completions.create(
            model=current_model,
            messages=messages,
            temperature=constant.LMStudioConfig.TEMPERATURE,
            max_tokens=constant.LMStudioConfig.MAX_TOKENS,
            stream=True,
        )
    else:
        if config is None:
            config = llm_tools.get_generate_config()
        return client.models.generate_content(
            model=current_model, contents=contents, config=config
        )


def process_completion(completion: Iterator, osc: VRChatOSC, tts: TextToSpeechManager) -> str:
    """
    Processes a streaming or single-shot completion response, queuing TTS
    sentence by sentence.

    Args:
        completion: Streaming iterator or single response object.
        osc (VRChatOSC): Used to set the typing indicator.
        tts (TextToSpeechManager): TTS queue target.

    Returns:
        str: The full response text.
    """
    osc.set_typing_indicator(True)

    def handle_text(text: str) -> str:
        full = ""
        for sentence in chunk_text(text):
            full += f" {sentence}"
            print(f"\033[93mAI:\033[0m \033[92m{sentence}\033[0m")
            tts.add_to_queue(sentence)
        return full

    full_response = ""

    if hasattr(completion, "text"):
        full_response = handle_text(completion.text)
    else:
        buffer = ""
        for chunk in completion:
            text_piece = None
            if hasattr(chunk, "text") and chunk.text:
                text_piece = chunk.text
            else:
                try:
                    text_piece = chunk.choices[0].delta.content
                except (AttributeError, IndexError):
                    text_piece = None

            if not text_piece:
                continue

            buffer += text_piece
            sentence_chunks = chunk_text(buffer)

            while len(sentence_chunks) > 1:
                sentence = sentence_chunks.pop(0)
                full_response += f" {sentence}"
                print(f"\033[93mAI:\033[0m \033[92m{sentence}\033[0m")
                tts.add_to_queue(sentence)

            buffer = sentence_chunks[0] if sentence_chunks else ""

        if buffer:
            full_response += f" {buffer}"
            print(f"\033[93mAI:\033[0m \033[92m{buffer}\033[0m")
            tts.add_to_queue(buffer)

    while not tts.is_idle():
        time.sleep(0.1)

    return full_response


def add_vision_updates_to_history(history: list, vision_manager: VisionManager) -> list:
    """
    Appends any pending vision updates to the conversation history.

    Args:
        history (list): Current history list.
        vision_manager (VisionManager): Source of vision updates.

    Returns:
        list: Updated history.
    """
    for update in vision_manager.get_new_vision_updates():
        history.append({"role": "system", "content": update})
        print(f"\033[96m[VISION]\033[0m \033[94m{update}\033[0m")
    return history


def run_main_loop(
    osc: VRChatOSC,
    history: list,
    vision_manager: VisionManager,
    client,
    tts: TextToSpeechManager,
    current_model: str,
    transcriber,
    head_tracker: Optional[HeadTracker] = None,
    session_persistence_manager: Optional[SessionPersistenceManager] = None,
) -> None:
    """
    The primary conversation loop.

    Generates an AI response, speaks it via TTS, waits for voice input,
    then repeats.  History is periodically flushed to disk so it survives
    unexpected shutdowns.

    Args:
        osc: VRChat OSC client.
        history (list): Conversation history.
        vision_manager: Vision subsystem.
        client: LLM client.
        tts: Text-to-speech manager.
        current_model (str): Model ID string.
        transcriber: Speech-to-text handler.
        head_tracker (Optional[HeadTracker]): Head-movement controller.
        session_persistence_manager: Optional session persistence manager.
    """
    if head_tracker:
        head_tracker.start()

    while True:
        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        if not history:
            history = initialize_history()

        history = add_vision_updates_to_history(history, vision_manager)

        contents = generate_contents(history)
        config = llm_tools.get_generate_config()
        response = generate_with_client(client, contents, current_model, config)

        new_message = {"role": "assistant", "content": ""}
        full_response = process_completion(response, osc, tts)
        new_message["content"] = full_response
        history.append(new_message)

        # Get voice input
        user_speech = ""
        while not user_speech:
            osc.send_message("Listening")
            osc.set_typing_indicator(False)
            user_speech = transcriber.get_user_input(osc)

        print(f"\033[93mHUMAN:\033[0m \033[92m{user_speech}\033[0m")
        history.append({"role": "user", "content": user_speech})

        # Persist history to disk
        JsonWrapper.write(constant.FilePaths.HISTORY_PATH, history)
        history = JsonWrapper.read_json(constant.FilePaths.HISTORY_PATH)

        osc.send_message("Thinking")
        osc.set_typing_indicator(True)


def main() -> None:
    """
    Initialises all components and starts the main conversation loop.
    """
    components = initialize_components()
    (
        osc,
        transcriber,
        history,
        client,
        tts,
        vision_manager,
        head_tracker,
        movement_controller,
        sfx_manager,
        personality_manager,
        idle_gaze_controller,
        session_persistence_manager,
    ) = components

    # Wipe any stale history from a previous run
    JsonWrapper.wipe_json(constant.FilePaths.HISTORY_PATH)

    current_model = get_current_model(client, vision_manager)

    run_main_loop(
        osc,
        history,
        vision_manager,
        client,
        tts,
        current_model,
        transcriber,
        head_tracker,
        session_persistence_manager,
    )


if __name__ == "__main__":
    main()
