from classes.whisper import WhisperTranscriber
from classes.system_prompt import SystemPrompt
from classes.json_wrapper import JsonWrapper
from classes.osc import VRChatOSC
import constants as constant
from openai import OpenAI
import datetime
import pyttsx3
import wave
import pyaudio
# import http_server
import re
import os

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

# Initialize pyttsx3 and set properties
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
voices = engine.getProperty('voices')

def play_tts(output_file, output_device_index=constant.AUDIO_OUTPUT_INDEX):
    """
    Args:
        output_file (string): The path to the output location
        output_device_index (integer, optional): The index of the audio device that pyttsx3 plays to. Defaults to AUDIO_OUTPUT_INDEX.

    Create a output based on the input and play it to an audio's index.
    """
    wf = wave.open(output_file, 'rb')
    p = pyaudio.PyAudio()

    # Open the audio stream
    try:
        sample_rate = wf.getframerate()
        if sample_rate != p.get_device_info_by_index(output_device_index)['defaultSampleRate']:
            print(f"Error: Sample rate {sample_rate} not supported by output device")
            wf.close()
            p.terminate()
            return

        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=sample_rate,
            output=True,
            output_device_index=output_device_index
        )
    except OSError as e:
        print(f"Error opening stream: {e}")
        return
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Cleanup
    stream.stop_stream()
    stream.close()
    wf.close()
    p.terminate()

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

def generate_tts(sentence):
    os.remove("tts_output.wav")
    engine.save_to_file(sentence, "tts_output.wav")
    engine.runAndWait()

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
                generate_tts(sentence)
                play_tts("tts_output.wav")
            buffer = sentence_chunks[0]

    if buffer:
        osc.set_typing_indicator(True)
        full_response += f" {buffer}"
        print(f"AI: {buffer}")
        osc.send_message(buffer)
        generate_tts(buffer)
        play_tts("tts_output.wav")
        new_message["content"] = full_response

    osc.set_typing_indicator(False)

    JsonWrapper.write(constant.HISTORY_PATH, new_message)

    # Get user speech input
    user_speech = ""

    while not user_speech:
        user_speech = transcriber.get_speech_input()

    f"HUMAN: {user_speech}"

    JsonWrapper.write(constant.HISTORY_PATH, user_speech)