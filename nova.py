"""
Main module for running the application logic.
This module initializes various components such as the VRChat OSC,
WhisperTranscriber, and Together AI client. It sends a startup message to
VRChat, sets up the system prompt and history, and enters a loop to
continuously process user speech input and generate AI responses.

Note: The vision system now runs asynchronously in the background and
continuously monitors VRChat without waiting for the AI to stop thinking.
"""

import datetime
import re
import time
from typing import List, Optional

import lmstudio as lms
from google import genai

import constants as constant
from classes import adapters, llm_tools
from classes.edge_tts import TextToSpeechManager
from classes.json_wrapper import JsonWrapper
from classes.osc import VRChatOSC
from classes.system_prompt import SystemPrompt
from classes.vision_manager import VisionManager


def initialize_history() -> list:
    system_prompt = SystemPrompt.get_full_prompt()
    now = datetime.datetime.now()
    history = []
    memories = JsonWrapper().read_dict(file_path=constant.FilePaths.MEMORY_FILE)

    # Build a single consolidated system message
    system_content = f"{system_prompt} Today is {now.strftime('%Y-%m-%d')}."

    # Add recent memories to the system prompt if they exist
    if memories:
        recent_memories = list(memories.items())[-20:]
        memory_text = "\n\nRecent Memories:\n" + "\n".join([f"{key}: {value}" for key, value in recent_memories])
        system_content += memory_text

    # LMStudio requires exactly one system message at the start
    history.append({"role": "system", "content": system_content})
    history.append({"role": "user", "content": constant.SystemMessages.INITIAL_USER_MESSAGE})

    return history


def initialize_components() -> tuple:
    """
    Initializes and sets up the components required for the application.
    This function creates and configures the following components:
    - VRChatOSC: Handles communication with VRChat using OSC protocol.
    - WhisperTranscriber: Manages audio transcription.
    - System prompt and history: Prepares the initial system prompt and
    conversation history.
    - Together AI client: Configures the Together AI API client for generating responses.
    - TextToSpeechManager: Manages text-to-speech functionality.
    Returns:
        tuple: A tuple containing the initialized components in the following
        order:
            - osc (VRChatOSC): The OSC communication handler.
            - transcriber (WhisperTranscriber): The audio transcriber.
            - history (list): The initial conversation history.
            - client (Together): The Together AI API client.
            - tts (TextToSpeechManager): The text-to-speech manager.
            - vision_manager (VisionManager): The vision system manager.
    """

    # Use adapters to construct components so each feature is module-adapter backed.
    osc = adapters.initialize_osc()

    transcriber = adapters.create_transcriber()

    history: List[dict] = initialize_history()

    client = adapters.create_genai_client()

    tts = adapters.create_tts(osc)

    # Initialize vision system via adapter
    vision_manager = adapters.create_vision_manager()

    return osc, transcriber, history, client, tts, vision_manager


def chunk_text(text: Optional[str]) -> List[str]:
    """
    Args:
        text (string): The text to break down.

    Returns:
        string: Text chunk.

    Split the text by sentence-ending punctuation
    """
    # Guard against None or non-string inputs
    if not isinstance(text, str):
        return []

    text = text.strip()
    if not text:
        return []

    # Split on sentence-ending punctuation followed by whitespace (robust to newlines/tabs)
    chunks = re.split(r"(?<=[.!?])\s+", text)

    return chunks


def process_completion(completion, osc: VRChatOSC, tts: TextToSpeechManager) -> str:
    """
    Processes a streaming completion response, extracts text chunks, and
    handles output and text-to-speech functionality.
    handles output and text-to-speech functionality.
    Args:
        completion: Either a streaming iterator of chunks, a PredictionResult object,
                    or a response object containing `.text`.
        osc (object): An object responsible for managing the typing indicator.
                      It should have a `set_typing_indicator` method.
        tts (object): An object responsible for text-to-speech functionality.
                      It should have `add_to_queue` and `is_idle` methods.
    Returns:
        str: The full response text generated from the completion.

    Handles different completion types:
    - LMStudio PredictionResult: Extracts .text directly
    - Google GenAI streaming chunks: Iterates with chunk.text
    - OpenAI-style chunks: Iterates with choices[0].delta.content
    """

    if osc:
        osc.set_typing_indicator(True)

    # Helper to consume a plain text string and queue TTS
    def handle_text(text: str) -> str:
        full = ""
        for sentence in chunk_text(text):
            full += f" {sentence}"
            print(f"\033[93mAI:\033[0m \033[92m{sentence}\033[0m")
            tts.add_to_queue(sentence)
        return full

    def extract_text_from_response(resp) -> Optional[str]:
        """
        Try to pull a text payload from common response shapes (GenAI, LMStudio).
        Returns a stripped string or None if nothing usable is found.
        """

        text_value = getattr(resp, "text", None)
        if isinstance(text_value, str) and text_value.strip():
            return text_value.strip()

        # LMStudio PredictionResult may expose output text via custom fields
        alt_fields = ["output_text", "response_text", "content"]
        for field in alt_fields:
            val = getattr(resp, field, None)
            if isinstance(val, str) and val.strip():
                return val.strip()

        # GenAI non-streaming responses may expose content via candidates/parts
        candidates = getattr(resp, "candidates", None)
        if candidates:
            try:
                content = getattr(candidates[0], "content", None)
                parts = getattr(content, "parts", None) if content else None
                if parts:
                    text_parts = [getattr(p, "text", "") for p in parts]
                    joined = " ".join([p for p in text_parts if p]).strip()
                    if joined:
                        return joined
            except Exception:
                # Best-effort fallback; if it fails we will log later
                pass

        # As a last resort, some response objects stringify to the text
        try:
            str_val = str(resp).strip()
            if str_val:
                return str_val
        except Exception:
            pass

        return None

    def preview_obj(obj) -> str:
        """Return a short preview of the completion object for debugging."""
        try:
            return f"type={type(obj)}, dir={list(dir(obj))[:20]}"
        except Exception:
            return "<uninspectable>"

    full_response = ""

    # If the completion is a single response object with .text (LMStudio or Google response), handle it
    direct_text = extract_text_from_response(completion)
    if direct_text:
        full_response = handle_text(direct_text)
    else:
        # Otherwise attempt to iterate streaming-like chunks. Support both
        # Google GenAI streaming chunks (chunk.text) and fallback to OpenAI
        # style chunks (choices[0].delta.content) if present.
        buffer = ""
        try:
            for chunk in completion:
                text_piece = None
                # google-genai streaming chunk
                if hasattr(chunk, "text") and chunk.text:
                    text_piece = chunk.text
                else:
                    # try OpenAI-like delta access (backwards-compat)
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
        except TypeError:
            # If completion is not iterable (e.g., non-streaming response without .text),
            # treat as empty response
            pass

    if not full_response:
        print("Warning: completion returned no text. Raw payload was not consumable.")
        print(f"Completion preview: {preview_obj(completion)}")

        # Best-effort verbose dump to help identify missing text paths
        try:
            if hasattr(completion, "candidates"):
                for idx, cand in enumerate(getattr(completion, "candidates", []) or []):
                    content = getattr(cand, "content", None)
                    parts = getattr(content, "parts", None) if content else None
                    print(f"Candidate[{idx}] content: {content}")
                    if parts:
                        for p_idx, part in enumerate(parts):
                            print(f"  Part[{p_idx}] type={type(part)}, attrs={list(dir(part))[:15]}, value={getattr(part, 'text', None)}")
            else:
                # As a last resort, show a stringified version to see structure
                print(f"Completion str(): {str(completion)}")
        except Exception as dump_err:
            print(f"Debug dump failed: {dump_err}")

    # Wait until TTS finished speaking
    while not tts.is_idle():
        time.sleep(0.1)

    return full_response


def add_vision_updates_to_history(history: list, vision_manager: VisionManager) -> list:
    """
    Add any new vision updates to the conversation history.

    Args:
        history (list): Current conversation history
        vision_manager (VisionManager): The vision manager instance

    Returns:
        list: Updated history with vision updates added as system messages
    """
    vision_updates = vision_manager.get_new_vision_updates()

    for update in vision_updates:
        # Use 'user' role instead of 'system' to avoid LMStudio's multi-part system prompt error
        vision_message = {"role": "user", "content": f"[VISION UPDATE]: {update}"}
        history.append(vision_message)

        print(f"\033[96m[VISION]\033[0m \033[94m{update}\033[0m")

    return history


def get_current_model():
    """
    Returns the current language model to use from the Together AI client.

    Args:
        client (object): The Together AI client instance.
        vision_manager (object): The vision manager instance (for cleanup if needed).

    Returns:
        str: The ID of the selected language model from constants.
    """
    if constant.LLM_API.IS_USING_TOGETHER:
        return lms.llm(constant.LanguageModel.MODEL_ID)
    else:
        return constant.LanguageModel.MODEL_ID


def generate_contents(history: list) -> list:
    """
    Converts the chat-style conversation history into the GenAI SDK `contents` format,
    mapping roles appropriately for GenAI ('user' or 'model').

    Args:
        history (list): List of message dictionaries, each with 'role' and 'content' keys.

    Returns:
        list: List of GenAI Content objects (or raw text strings if construction fails),
              with roles mapped to 'user' or 'model' as required by the SDK.
    """
    # Convert the existing chat-style `history` into the GenAI SDK
    # `contents` format. Each history entry becomes a Content with a
    # text Part so the SDK receives role-aware inputs.
    contents = []
    for msg in history:
        text = msg.get("content", "")
        # Map roles from chat format to GenAI allowed roles ('user' or 'model')
        role = msg.get("role", "user")
        if role != "user":
            # GenAI accepts 'user' and 'model' for content.role; map everything
            # that's not 'user' to 'model' (assistant/system -> model).
            role = "model"

        try:
            part = genai.types.Part.from_text(text=text)
            content = genai.types.Content(role=role, parts=[part])
            contents.append(content)
        except (AttributeError, TypeError) as e:
            # Fallback: if types are unavailable or construction fails, log a warning and pass raw text
            print(f"Warning: Failed to construct GenAI content object for role '{role}': {e}. Appending raw text as fallback.")
            contents.append(text)

    return contents


def run_main_loop(osc, history, vision_manager, client, tts, current_model, transcriber) -> None:

    while True:
        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        if not history:
            history = initialize_history()

        # Check for vision updates before generating response
        history = add_vision_updates_to_history(history, vision_manager)

        contents = generate_contents(history)

        # Call the Google GenAI SDK. Use the synchronous non-streaming
        # `generate_content` method and then handle the returned `.text`.
        # Attach function-calling tools/config with minimal changes: functions are defined
        # in `classes/llm_tools.py` and the Python SDK will handle automatic calls.
        if not constant.LLM_API.IS_USING_TOGETHER:
            config = llm_tools.get_generate_config()
            response = client.models.generate_content(model=current_model, contents=contents, config=config)
        else:
            # LMStudio: Wrap chat history in the expected message envelope
            # {"messages": [...]} before calling respond() for chat-style models.
            chat_payload = {"messages": history}
            response = current_model.respond(chat_payload)

        # Create the new message and add it to the history
        new_message = {"role": "assistant", "content": ""}
        full_response = process_completion(response, osc, tts)
        new_message["content"] = full_response
        history.append(new_message)

        # Get user speech input
        user_speech = ""
        while not user_speech:
            osc.send_message("Listening")
            osc.set_typing_indicator(False)
            user_speech = transcriber.get_user_input(osc)

        # Add user speech to history
        print(f"\033[93mHUMAN:\033[0m \033[92m{user_speech}\033[0m")
        user_speech = {"role": "user", "content": user_speech}
        history.append(user_speech)

        # Update history
        JsonWrapper.write(constant.FilePaths.HISTORY_PATH, history)
        history = JsonWrapper.read_json(constant.FilePaths.HISTORY_PATH)

        osc.send_message("Thinking")
        osc.set_typing_indicator(True)


def main() -> None:
    # Initialise the components
    components = initialize_components()
    osc, transcriber, history, client, tts, vision_manager = components

    # Whip the old history file
    JsonWrapper.wipe_json(constant.FilePaths.HISTORY_PATH)

    current_model = get_current_model()

    run_main_loop(osc, history, vision_manager, client, tts, current_model, transcriber)


if __name__ == "__main__":
    main()
