"""
Main module for running the application logic.
This module initializes various components such as the VRChat OSC,
WhisperTranscriber, and OpenAI client. It sends a startup message to
VRChat, sets up the system prompt and history, and enters a loop to
continuously process user speech input and generate AI responses.
"""

import datetime
import re
from openai import OpenAI
from classes.osc import VRChatOSC
from classes.edge_tts import TextToSpeechManager
from classes.whisper import WhisperTranscriber
from classes.system_prompt import SystemPrompt
from classes.json_wrapper import JsonWrapper
import constants as constant


def initialize_components():
    """
    Initializes and returns the components required for the application.
    This function performs the following tasks:
    - Imports necessary modules and classes.
    - Creates an instance of VRChatOSC with local IP and VRC port from
    constants.
    - Creates an instance of WhisperTranscriber.
    - Retrieves the full system prompt for the "normal" mode.
    - Gets the current date and time.
    - Initializes a history list with system prompts and a user greeting.
    - Creates an instance of OpenAI client with specified base URL and API key.
    Returns:
        tuple: A tuple containing the following components:
            - osc (VRChatOSC): An instance of the VRChatOSC class.
            - transcriber (WhisperTranscriber): An instance of the
            WhisperTranscriber class.
            - history (list): A list of dictionaries representing the initial
            conversation history.
            - openai_client (OpenAI): An instance of the OpenAI client.
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
        {"role": "user", "content": "hi"},
    ]
    openai_client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )

    tts = TextToSpeechManager(
        voice=constant.Voice.VOICE_NAME,
        device_index=constant.Audio.AUDIO_OUTPUT_INDEX,
        VRChatOSC=osc
    )
    tts.initialize_tts_engine()
    return osc, transcriber, history, openai_client, tts


def chunk_text(text):
    """
    Args:
        text (string): The text to break down.

    Returns:
        string: Text chunk.

    Split the text by sentence-ending punctuation
    """
    chunks = re.split(r'(?<=[.!?]) +', text)
    return chunks


def process_completion(completion, osc, tts):
    """
    Processes the completion chunks from an AI model and sends the processed
    sentences to an output system controller (OSC).
    Args:
        completion (iterable): An iterable of completion chunks from the AI
        model. osc (object): An output system controller that handles sending
        messages, setting typing indicators, and playing text-to-speech (TTS).
    Returns:
        str: The full response generated from the completion chunks.
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
                print(f"AI: {sentence}")
                tts.add_to_queue(sentence)

            buffer = sentence_chunks[0]

    if buffer:
        full_response += f" {buffer}"
        print(f"AI: {buffer}")
        tts.add_to_queue(buffer)

    while not tts.is_idle():
        time.sleep(0.1)
    return full_response


def run_code():
    """
    Initializes and runs the main loop for the system.
    This function performs the following steps:
    1. Imports necessary constants and classes.
    2. Initializes components such as OSC, transcriber, history, and OpenAI
    client.
    3. Sends a message to VRChat indicating that the system is starting and
    sets the typing indicator.
    4. Enters an infinite loop where it:
        a. Creates model parameters for the OpenAI client.
        b. Sends a "Thinking" message to VRChat and sets the typing indicator.
        c. Processes the completion response from the OpenAI client.
        d. Writes the assistant's response to the history JSON file.
        e. Continuously listens for user speech input.
        f. Prints the user's speech input and writes it to the history JSON
        file.
    """

    osc, transcriber, history, openai_client, tts = initialize_components()

    # Send message to VRChat to indicate that the system is starting
    JsonWrapper.whipe_json(constant.FilePaths.HISTORY_PATH)

    while True:
        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        # Creates model parameters
        completion = openai_client.chat.completions.create(
            model=constant.LanguageModel.MODEL_ID,
            messages=history,
            temperature=constant.LanguageModel.LM_TEMPERATURE,
            stream=True,
        )

        new_message = {"role": "assistant", "content": ""}

        full_response = process_completion(completion, osc, tts)
        new_message["content"] = full_response

        # Get user speech input
        user_speech = ""
        while not user_speech:
            osc.send_message("Listening")
            osc.set_typing_indicator(False)
            user_speech = transcriber.get_voice_input()

        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        print(f"HUMAN: {user_speech}")

        user_speech = {"role": "user", "content": user_speech}
        history.append(new_message)
        history.append(user_speech)

        JsonWrapper.write(constant.FilePaths.HISTORY_PATH, history)

        history = JsonWrapper.read_json(constant.FilePaths.HISTORY_PATH)


if __name__ == "__main__":
    run_code()
