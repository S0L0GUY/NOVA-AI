"""
Main module for running the application logic.
This module initializes various components such as the VRChat OSC,
WhisperTranscriber, and OpenAI client. It sends a startup message to
VRChat, sets up the system prompt and history, and enters a loop to
continuously process user speech input and generate AI responses.
"""

import datetime
import os
import re
import sounddevice as sd
import pyttsx3
import soundfile as sf
from openai import OpenAI
from classes.osc import VRChatOSC
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
    transcriber = WhisperTranscriber()
    system_prompt = SystemPrompt.get_full_prompt("normal")
    now = datetime.datetime.now()
    history = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Today is {now.strftime('%Y-%m-%d')}"},
        {"role": "user", "content": "Hey"},
    ]
    openai_client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )
    return osc, transcriber, history, openai_client


def play_tts(text, output_device_index):
    """
    Converts text to speech using the pyttsx3 library, saves the speech to a
    WAV file, and plays the audio using the sounddevice library.
    Args:
        text (str): The text to be converted to speech.
        output_device_index (int): The index of the output audio device to
        play the speech.
    Raises:
        RuntimeError: If there is an error in playing the audio file.
    """

    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'Zira' in voice.name:
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 200)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

    file_path = "tts_output.wav"

    if os.path.exists(file_path):
        os.remove("tts_output.wav")

    engine.save_to_file(text, file_path)
    engine.runAndWait()

    def play_audio(file_path, output_device_index):
        data, samplerate = sf.read(file_path, always_2d=False)
        sd.play(data, samplerate, device=output_device_index)
        sd.wait()

    play_audio(file_path, output_device_index)


def chunk_text(text):
    """
    Args:
        text (string): The text to break down.

    Returns:
        string: Text chunk.

    Split the text by sentence-ending punctuation
    """
    chunks = re.split(r'(?<=[.,;:!?]) +', text)
    return chunks


def process_completion(completion, osc):
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
    for chunk in completion:
        osc.set_typing_indicator(True)
        if chunk.choices[0].delta.content:
            buffer += chunk.choices[0].delta.content
            sentence_chunks = chunk_text(buffer)
            while len(sentence_chunks) > 1:
                sentence = sentence_chunks.pop(0)
                full_response += f" {sentence}"
                print(f"AI: {sentence}")
                osc.send_message(sentence)
                play_tts(
                    sentence,
                    output_device_index=constant.Audio.AUDIO_OUTPUT_INDEX
                )
            buffer = sentence_chunks[0]
    if buffer:
        osc.set_typing_indicator(True)
        full_response += f" {buffer}"
        print(f"AI: {buffer}")
        osc.send_message(buffer)
        play_tts(buffer, output_device_index=constant.Audio.AUDIO_OUTPUT_INDEX)
    osc.set_typing_indicator(False)
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

    osc, transcriber, history, openai_client = initialize_components()

    # Send message to VRChat to indicate that the system is starting
    osc.send_message("System Loading")
    osc.set_typing_indicator(True)

    while True:
        # Creates model parameters
        completion = openai_client.chat.completions.create(
            model=constant.LanguageModel.MODEL_ID,
            messages=history,
            temperature=constant.LanguageModel.LM_TEMPERATURE,
            stream=True,
        )

        new_message = {"role": "assistant", "content": ""}
        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        full_response = process_completion(completion, osc)
        new_message["content"] = full_response

        JsonWrapper.write(constant.FilePaths.HISTORY_PATH, new_message)

        # Get user speech input
        user_speech = ""
        while not user_speech:
            user_speech = transcriber.get_speech_input()

        print(f"HUMAN: {user_speech}")
        JsonWrapper.write(constant.FilePaths.HISTORY_PATH, user_speech)
