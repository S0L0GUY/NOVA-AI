"""
Main module for running the application logic.
This module initializes various components such as the VRChat OSC,
WhisperTranscriber, and OpenAI client. It sends a startup message to
VRChat, sets up the system prompt and history, and enters a loop to
continuously process user speech input and generate AI responses.

Note: The vision system now runs asynchronously in the background and
continuously monitors VRChat without waiting for the AI to stop thinking.
"""

import datetime
import re
import time
from openai import OpenAI
from classes.osc import VRChatOSC
from classes.edge_tts import TextToSpeechManager
from classes.whisper import WhisperTranscriber
from classes.system_prompt import SystemPrompt
from classes.json_wrapper import JsonWrapper
from classes.vision_manager import VisionManager
from together import Together
import constants as constant
import sys


def initialize_components() -> tuple:
    """
    Initializes and sets up the components required for the application.
    This function creates and configures the following components:
    - VRChatOSC: Handles communication with VRChat using OSC protocol.
    - WhisperTranscriber: Manages audio transcription.
    - System prompt and history: Prepares the initial system prompt and
    conversation history.
    - OpenAI client: Configures the OpenAI API client for generating responses.
    - TextToSpeechManager: Manages text-to-speech functionality.
    Returns:
        tuple: A tuple containing the initialized components in the following
        order:
            - osc (VRChatOSC): The OSC communication handler.
            - transcriber (WhisperTranscriber): The audio transcriber.
            - history (list): The initial conversation history.
            - openai_client (OpenAI): The OpenAI API client.
            - tts (TextToSpeechManager): The text-to-speech manager.
            - vision_manager (VisionManager): The vision system manager.
    """

    osc = VRChatOSC(constant.Network.LOCAL_IP, constant.Network.VRC_PORT)

    osc.send_message("System Starting")
    osc.set_typing_indicator(True)

    transcriber = WhisperTranscriber()

    system_prompt = SystemPrompt.get_full_prompt()
    now = datetime.datetime.now()
    history = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Today is {now.strftime('%Y-%m-%d')}"},
        {
            "role": "user",
            "content": constant.SystemMessages.INITIAL_USER_MESSAGE
        },
    ]

    if constant.LLM_API.API_TYPE == "together":
        client = Together(
            base_url=constant.LLM_API.BASE_URL,
            api_key=constant.LLM_API.API_KEY
        )
    else:
        client = OpenAI(
            base_url=constant.LLM_API.BASE_URL,
            api_key=constant.LLM_API.API_KEY
        )

    tts = TextToSpeechManager(
        voice=constant.Voice.VOICE_NAME,
        device_index=constant.Audio.AUDIO_OUTPUT_INDEX,
        VRChatOSC=osc,
    )
    tts.initialize_tts_engine()

    # Initialize vision system
    vision_manager = VisionManager()
    vision_manager.start_vision_system()

    return osc, transcriber, history, client, tts, vision_manager


def chunk_text(text: str) -> list:
    """
    Args:
        text (string): The text to break down.

    Returns:
        string: Text chunk.

    Split the text by sentence-ending punctuation
    """
    chunks = re.split(r"(?<=[.!?]) +", text)

    return chunks


def process_completion(completion: iter, osc: object, tts: object) -> str:
    """
    Processes a streaming completion response, extracts text chunks, and
    handles output and text-to-speech functionality.
    Args:
        completion (iter): An iterable object containing streaming completion
                            data. Each chunk is expected to have a `choices`
                            attribute with a `delta.content` field containing
                            the text.
        osc (object): An object responsible for managing the typing indicator.
                      It should have a `set_typing_indicator` method.
        tts (object): An object responsible for text-to-speech functionality.
                      It should have `add_to_queue` and `is_idle` methods.
    Returns:
        str: The full response text generated from the completion.
    """

    buffer = ""
    full_response = ""
    osc.set_typing_indicator(True)

    for chunk in completion:
        if chunk.choices[0].delta.content:
            buffer += chunk.choices[0].delta.content
            sentence_chunks = chunk_text(buffer)

            while len(sentence_chunks) > 1:
                sentence = sentence_chunks.pop(0)
                full_response += f" {sentence}"
                print(f"\033[93mAI:\033[0m \033[92m{sentence}\033[0m")
                tts.add_to_queue(sentence)

            buffer = sentence_chunks[0]

    if buffer:
        full_response += f" {buffer}"
        print(f"\033[93mAI:\033[0m \033[92m{buffer}\033[0m")
        tts.add_to_queue(buffer)

    while not tts.is_idle():
        time.sleep(0.1)

    return full_response


def add_vision_updates_to_history(
        history: list,
        vision_manager: object
        ) -> list:
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
        vision_message = {
            "role": "system",
            "content": update
        }
        history.append(vision_message)

        print(f"\033[96m[VISION]\033[0m \033[94m{update}\033[0m")

    return history


def get_current_model(client: object, vision_manager: object) -> str:
    """
    Determines and returns the current language model to use from the OpenAI
    client. Checks if the model specified by `constant.LanguageModel.MODEL_ID`
    is available in the list of models provided by the `client`. If the
    specified model is not found, it selects the first available model, prints
    a warning, and switches to it. If no models are available, it prints an
    error message, performs cleanup using the `vision_manager`, and exits the
    program.
    Args:
        client (object): The OpenAI client instance used to list
        available models.
        vision_manager (object): The vision manager instance used for cleanup
        if no models are available.
    Returns:
        str: The ID of the selected language model.
    Side Effects:
        Prints messages to the console, may exit the program if no models are
        available, and may call `vision_manager.cleanup()`.
    """

    available_models = client.models.list()
    model_list = [model.id for model in available_models]

    if constant.LanguageModel.MODEL_ID not in model_list:
        print(
            f"\033[91mModel \033[33m{constant.LanguageModel.MODEL_ID}"
            f"\033[91m not found.\033[0m"
        )

        if model_list:
            current_model = model_list[0]
            print(
                (
                    f"\033[91mAuto Switching LM to: \033[33m{current_model}"
                    f"\033[91m\033[0m"
                )
            )
        else:
            print("\033[91mNo models available.\033[0m")
            vision_manager.cleanup()
            sys.exit(1)
    else:
        current_model = constant.LanguageModel.MODEL_ID

    return current_model


def run_main_loop(
        osc,
        history,
        vision_manager,
        client,
        tts,
        current_model,
        transcriber
        ) -> None:

    while True:
        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        # Check for vision updates before generating response
        history = add_vision_updates_to_history(history, vision_manager)

        # Creates model parameters
        completion = client.chat.completions.create(
            model=current_model,
            messages=history,
            temperature=constant.LanguageModel.LM_TEMPERATURE,
            stream=True,
        )

        # Create the new message and add it to the history
        new_message = {"role": "assistant", "content": ""}
        full_response = process_completion(completion, osc, tts)
        new_message["content"] = full_response
        history.append(new_message)

        # Get user speech input
        user_speech = ""
        while not user_speech:
            osc.send_message("Listening")
            osc.set_typing_indicator(False)
            user_speech = transcriber.get_voice_input()

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

    # Whipe the old history file
    JsonWrapper.wipe_json(constant.FilePaths.HISTORY_PATH)

    current_model = get_current_model(client, vision_manager)

    run_main_loop(
        osc,
        history,
        vision_manager,
        client,
        tts,
        current_model,
        transcriber
    )


if __name__ == "__main__":
    main()
