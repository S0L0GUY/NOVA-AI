'''
set VRC mic to cable B
set default playback to cable a
set default output to cable a
'''

# TODO: Look for more TODO's in the code
# TODO: Do stuff with the controll panel class
# TODO: Make Nova sing national anthem
# TODO: Add multilingual support
# TODO: Add face recognition so the AI can look at people thrugh OSC

# Character name is "〜NOVA〜"

# Import necessary libraries and initialize debugging
from debugFunctionLibrary import Debug as debug
debug.clear()
debug.write("SYSTEM", "Program started")
debug.write("IMPORT", "Debug imported")

# Import all necesarry library's
try:
    from openai import OpenAI
    import os
    import pyttsx3
    import time
    import pyaudio
    from pythonosc import udp_client
    import re
    import wave
    import sys
    import whisper
    import numpy as np
    from pydub import AudioSegment
    from pydub.silence import split_on_silence
    debug.write("IMPORT", "Successfully imported openai, pyttsx3, os, time, pyaudio, pythonosc, re, wave, sys, whisper, numpy, pydub")
except ImportError as e:
    # Prints an error message if a library cannot be imported
    debug.write("ERROR", str(e))

# Set up OSC for chat and movement
local_ip = "192.168.0.19" # Your computers local IP
port = 9000 # VR Chat port, 9000 is the default
osc_client = udp_client.SimpleUDPClient(local_ip, port)

audio_device_index = 6 # The index of the audio output device

try:
    with open('var/mood.txt', 'r') as file:
        # Get the current mood
        mood = file.read()
except FileNotFoundError:
    debug.write("ERROR", "The file 'var/mood.txt' was not found.")
except IOError:
    debug.write("ERROR", "An I/O error occurred while trying to read the file.")
except Exception as e:
    debug.write("ERROR", f"An exception error has occured: {e}")

if not mood:
    mood = "normal"

def debug_write(log_type, message):
    if mood != "therapy":
        debug.write(log_type, message)
    else:
        debug.write(log_type, "Therapy Mode Block")

# Initialize pyttsx3 and set properties
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
voices = engine.getProperty('voices')

for voice in voices:
    # Set the voice to Zira for pyttsx3
    if "Zira" in voice.name:
        engine.setProperty('voice', voice.id)
        break

# Whisper models include: tiny, base, small, medium, large
model = whisper.load_model("base") # Load Whisper model

# Point to the local LM Studio server
openai_client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Load the system prompts based on mode
mood_prompts = {
    "normal": 'text_files/prompts/normal_system_prompt.txt',
    "argument": 'text_files/prompts/argument_system_prompt.txt',
    "misinformation": 'text_files/prompts/misinformation_system_prompt.txt',
    "drunk": 'text_files/prompts/drunk_system_prompt.txt',
    "depressed": 'text_files/prompts/depressed_system_prompt.txt',
    "therapy": 'text_files/prompts/therapy_system_prompt.txt',
    "anxious": 'text_files/prompts/anxious_system_prompt.txt',
    "sarcasm": 'text_files/prompts/sarcasm_system_prompt.txt',
    "pleasing": 'text_files/prompts/pleasing_system_prompt.txt'
}

system_prompt_file = mood_prompts.get(mood, 'text_files/prompts/normal_system_prompt.txt')

with open(system_prompt_file, 'r') as file:
    system_prompt = file.read()

with open('text_files/prompts/additional_system_prompt.txt', 'r') as file:
    # Load additional system prompt
    additional_system_prompt = file.read()                      

system_prompt = f"{system_prompt} \n {additional_system_prompt}" # Put system prompt together

# Create a variadable to store the chat history in
history = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Hello, can you introduce yourself?"},
]

class controll_panel:
    """Create a simple way for an external program to manipulate this program"""
    def add_system_message(message):
        history.append({"role": "system", "content": message})


    def restart_program():
        """
        Restart this program
        """
        restart_program()


    def activate_mode(mode):
        """
        Args:
        mode (string): The mode to put the ai model into


        Activate a mode to put the LLM into
        """
        ai_system_command_catcher(f"activate {mode} mode now")


    def request_conversation_logs():
        """
        Returns:
        (list): The whole conversation between the user and the AI bot durring the current session


        Returns the whole history of the conversation with the bot
        """
        return history

def play_tts(output_file, output_device_index=audio_device_index):
    """
    Args:
        output_file (string): The path to the output location
        output_device_index (integer, optional): The index of the audio device that pyttsx3 plays to. Defaults to audio_device_index.

    Create a output based on the input and play it to an audio's index.
    """
    wf = wave.open(output_file, 'rb')
    p = pyaudio.PyAudio()

    # Open the audio stream
    stream = p.open(
        format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True,
        output_device_index=output_device_index
    )

    # Read and play audio data
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        data = wf.readframes(1024)

    # Cleanup
    stream.stop_stream()
    stream.close()
    wf.close()
    p.terminate()

def type_in_chat(message):
    """
    Args:
        message (string): The message that you want to type in chat.

    Type a message into Nova's vrchat game using OSC
    """    
    osc_client.send_message("/chatbox/input", [message, True])

type_in_chat("System Loading...")

def get_speech_input():
    """
    Returns:
        string: The detected speech input

    Use Whisper to gather speech input and return the transcription.
    """
    # Initialize PyAudio
    p = pyaudio.PyAudio()
    
    # Set audio recording parameters
    format = pyaudio.paInt16
    channels = 1
    rate = 16000
    chunk = 1024
    silence_threshold = -40  # Silence threshold in dB
    silence_duration = 1000  # Duration of silence in ms (1 second)
    
    # Open the audio stream
    stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    
    # Record audio
    frames = []
    type_in_chat("Listening...")
    silent_chunks = 0
    
    while True:
        data = stream.read(chunk)
        frames.append(data)
        
        # Convert audio chunk to Pydub's AudioSegment for silence detection
        audio_chunk = AudioSegment(data, sample_width=p.get_sample_size(format), frame_rate=rate, channels=channels)
        
        # Check if the audio chunk is silent
        if audio_chunk.dBFS < silence_threshold:
            silent_chunks += 1
        else:
            silent_chunks = 0
        
        # Stop recording after detecting sufficient silence
        if silent_chunks > silence_duration / (1000 * chunk / rate):
            break
    
    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    p.terminate()
    
    # Save the recorded data to a WAV file
    with wave.open('temp.wav', 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(pyaudio.PyAudio().get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    
    # Transcribe audio file using Whisper
    result = model.transcribe('temp.wav')
    text = result['text']

    # When the AI hears silence it outputs "you", so this is the scuff fix
    if text != " you":
        return text
    else:
        return ""

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

def delete_file(path):
    """
    Args:
        path (string): File path.

    Delete a file.
    """    
    if os.path.exists(path):
        os.remove(path)
    else:
        return

delete_file("output.wav")
delete_file("temp.wav")

def restart_program():
    """Restarts the current program."""
    type_in_chat("Program Restarting...")
    debug_write("SYSTEM", "Restarting the program...")
    os.system('cls')
    python = sys.executable
    os.execl(python, python, *sys.argv)

def send_look_direction(pitch, yaw, roll=0): # This function may not work correctly because Nova's avatar may not have OSC support
    """
    Args:
        pitch (integer): The pitch that you want to set the head to.
        yaw (integer): The yaw that you want to set the head to.
        roll (integer, optional): The roll that you want to set the head to. Defaults to 0.

    Point the head in a specified direction
    """
    osc_client.send_message("/avatar/parameters/LookDirection", [pitch, yaw, roll])

def command_catcher():
    """Catches commands that the user says"""
    if "system reset" in user_input.lower():
        debug_write("COMMAND CATCHER", "System Reset Called")
        restart_program()
    elif "activate argument mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Argument Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('argument')
        restart_program()
    elif "activate normal mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Normal Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('normal')
        restart_program()
    elif "stop talking" in user_input.lower() or "shut up" in user_input.lower() or "time out" in user_input.lower():
        debug_write("COMMAND CATCHER", "Timeout Called")
        time_left = 60
        while time_left > 0:
            type_in_chat(f"Timeout Period: {str(time_left)}")
            time_left -= 2
            time.sleep(2)
        restart_program()
    elif "activate misinformation mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "wrong Information Only Called")
        with open('var/mood.txt', 'w') as file:
            file.write('misinformation')
        restart_program()
    elif "get drunk" in user_input.lower():
        debug_write("COMMAND CATCHER", "Get Drunk Called")
        with open('var/mood.txt', 'w') as file:
            file.write('drunk')
        restart_program()
    elif "activate depressed mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Depressed Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('depressed')
        restart_program()
    elif "activate therapy mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Therapy Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('therapy')
        restart_program()
    elif "activate anxious mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Anxious Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('anxious')
        restart_program()
    elif "activate sarcasm mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Sarcasm Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('sarcasm')
        restart_program()
    elif "activate pleasing mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Pleasing Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('pleasing')
        restart_program()

def ai_system_command_catcher(ai_input):
    """Catches commands that the AI says"""
    if "reset my system now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "System Reset Called")
        restart_program()
    elif "enter angry mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Argument Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('argument')
        restart_program()
    elif "activate normal mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Normal Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('normal')
        restart_program()
    elif "stop talking now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Timeout Called")
        time_left = 60
        while time_left > 0:
            type_in_chat(f"Timeout Period: {str(time_left)}")
            time_left -= 2
            time.sleep(2)
        restart_program()
    elif "activate wrong information now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "wrong Information Only Called")
        with open('var/mood.txt', 'w') as file:
            file.write('misinformation')
        restart_program()
    elif "activate drunk mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Get Drunk Called")
        with open('var/mood.txt', 'w') as file:
            file.write('drunk')
        restart_program()
    elif "activate my depressed mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Depressed Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('depressed')
        restart_program()
    elif "activate my therapy mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Therapy Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('therapy')
        restart_program()
    elif "activate my anxious mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Anxious Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('anxious')
        restart_program()
    elif "activate my sarcasm mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Sarcasm Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('sarcasm')
        restart_program()
    elif "activate my pleasing mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Pleasing Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('pleasing')
        restart_program()

# Main loop
while True:
    # Creates model parameters
    completion = openai_client.chat.completions.create(
        model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
        messages=history,
        temperature=0.9,
        stream=True,
    )

    new_message = {"role": "assistant", "content": ""}
    
    type_in_chat("Thinking...")

    buffer = ""

    for chunk in completion: # Prosesses incoming data from AI model
        if chunk.choices[0].delta.content:
            buffer += chunk.choices[0].delta.content
            # Process each chunk of text to break it into sentences
            sentence_chunks = chunk_text(buffer)
            while len(sentence_chunks) > 1:
                sentence = sentence_chunks.pop(0)
                delete_file("output.wav")
                engine.save_to_file(sentence, "output.wav")
                engine.runAndWait()
                debug_write("AI", sentence)
                type_in_chat(sentence)
                play_tts("output.wav")
                ai_system_command_catcher(sentence)
            buffer = sentence_chunks[0]  # Keep the remaining text in the buffer

    # Process any remaining text after the stream ends
    if buffer:
        delete_file("output.wav")
        engine.save_to_file(buffer, "output.wav")
        engine.runAndWait()
        debug_write("AI", buffer)
        type_in_chat(buffer)
        play_tts("output.wav")
        ai_system_command_catcher(buffer)
        new_message["content"] = buffer  # Populate the new_message with the remaining text

    history.append(new_message) # Add the message to the history

    # Gets the users voice inpyt
    user_input = ""
    while not user_input:  # Keep prompting until valid input is received
        user_input = get_speech_input()
    history.append({"role": "user", "content": user_input})

    debug_write("PLAYER", user_input) # Adds the user input to the history
    command_catcher() # Checs the user input for commands