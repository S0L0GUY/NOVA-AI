from classes.whisper import WhisperTranscriber
from classes.system_prompt import SystemPrompt
from classes.json_wrapper import JsonWrapper
from classes.osc import VRChatOSC
import constants as constant
from openai import OpenAI
import datetime
import pyttsx3
import asyncio
# import http_server
import re
import os
import sounddevice as sd
import soundfile as sf

osc = VRChatOSC(constant.LOCAL_IP, constant.PORT)
transcriber = WhisperTranscriber()

# Send message to VRChat to indicate that the system is starting
osc.send_message("System Loading")
osc.set_typing_indicator(True)

# Get the system prompt
system_prompt = SystemPrompt.get_full_prompt("normal")

# Set up history
now = datetime.datetime.now()

history = [
    {"role": "system", "content": system_prompt},
    {"role": "system", "content": f"Today is {now.strftime("%Y-%m-%d")}"},
    {"role": "user", "content": "Hey"},
]

# Set up LLM
openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

def play_tts(text, output_device_index=constant.AUDIO_OUTPUT_INDEX):
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
    voices = engine.getProperty('voices')

    file_path = f"tts_output.wav"

    if os.path.exists(file_path):
        os.remove("tts_output.wav")

    engine.save_to_file(text, file_path)
    engine.runAndWait()

    def play_audio(file_path, output_device_index):
        data, samplerate = sf.read(file_path, always_2d=True)
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

def find_matching_words(word_list, string_to_check):
    """
    Args:
        word_list (list): All of the words that you want to detect.
        string_to_check (): The string that you want to parse for words.

    Returns:
        boolean: Is there a word from the list in the string to check?

    Parse the string to check for words in the list.
    """    
    return [word for word in word_list if word in string_to_check]

# Main logic
while True:
    # Creates model parameters
    completion = openai_client.chat.completions.create(
        model=constant.MODEL_ID,
        messages=history,
        temperature=constant.LM_TEMPERATURE,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}

    osc.send_message("Thinking")
    osc.set_typing_indicator(True)

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
                play_tts(sentence)
            buffer = sentence_chunks[0]

    if buffer:
        osc.set_typing_indicator(True)
        full_response += f" {buffer}"
        print(f"AI: {buffer}")
        osc.send_message(buffer)
        play_tts(buffer)
        new_message["content"] = full_response

    osc.set_typing_indicator(False)

    JsonWrapper.write(constant.HISTORY_PATH, new_message)

    # Get user speech input
    user_speech = ""

    while not user_speech:
        user_speech = transcriber.get_speech_input()

    f"HUMAN: {user_speech}"

    JsonWrapper.write(constant.HISTORY_PATH, user_speech)