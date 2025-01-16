'''
set VRC mic to cable B
set default playback to cable a
set default output to cable a
'''

# Character name is "〜NOVA〜"

# import and initialize debugging
from debug_function_library import Debug as debug
debug.clear()
debug.write("SYSTEM", "Program started")
debug.write("import", "Debug imported")

# import and initialize OSC client
from pythonosc import udp_client
debug.write("import", "pythonosc imported")

import constants as constant
debug.write("import", "constants imported")

# Set up OSC for chat and movement
osc_client = udp_client.SimpleUDPClient(constant.LOCAL_IP, constant.VRC_PORT)

osc_client.send_message("/chatbox/input", ["Program starting...", True])

# import all necessary dependencies
try:
    from openai import OpenAI
    import os
    import pyttsx3
    import time
    import pyaudio
    import re
    import wave
    import sys
    import whisper
    from pydub import AudioSegment
    from datetime import datetime
    import pyautogui
    import keyboard
    import json
    from translate import Translator
    debug.write("import", "Successfully imported openai, pyttsx3, os, time, pyaudio, pythonosc, re, wave, sys, whisper, numpy, pydub, datetime, pyautogui, keyboard, json, subprocess, googletrans")
except ImportError as e:
    # Prints an error message if a library cannot be imported
    osc_client.send_message("/chatbox/input", [str(e), True])
    debug.write("ERROR", str(e))

try:
    with open('var/mood.txt', 'r') as file:
        # Get the current mood
        mood = file.read()
except FileNotFoundError:
    debug.write("ERROR", "The file 'var/mood.txt' was not found.")
    osc_client.send_message("/chatbox/input", ["Mood file not found", True])
except IOError:
    debug.write("ERROR", "An I/O error occurred while trying to read the file.")
    osc_client.send_message("/chatbox/input", ["I/O Error", True])
except Exception as e:
    debug.write("ERROR", f"An exception error has occurred: {e}")
    osc_client.send_message("/chatbox/input", [e, True])

if not mood:
    mood = "normal"

with open('var/bad_words.json', 'r') as file:
    bad_words = json.load(file)

# Initialize pyttsx3 and set properties
engine = pyttsx3.init()
engine.setProperty('rate', 200)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)
voices = engine.getProperty('voices')

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

system_prompt = f"{system_prompt} \n {additional_system_prompt}" # Put the system prompt together

now = datetime.now()

history = [
    {"role": "system", "content": system_prompt},
    {"role": "system", "content": f"Today is {now.strftime('%Y-%m-%d')}"},
    {"role": "user", "content": "Hey"},
]

with open('text_files/prompts/snapchat_system_prompt.txt', 'r') as file:
    snapchat_system_prompt = file.read()

snapchat_history=[
    {"role": "system", "content": snapchat_system_prompt},
]

with open('history.json', 'w') as file:
    json.dump(history, file, indent=4)

def debug_write(log_type, message):
    """
    Args:
        log_type (string): The type of message, e.g: ERROR, import.
        message (string): The message to log.

    Log a message to both the terminal, alltime_debug_log.txt, and current_debug_log.txt.
    """
    if mood != "therapy":
        debug.write(log_type, message)
    else:
        debug.write(log_type, "Therapy Mode Block")

def translate_text(text):
    """
    Args:
        text (string): The text that you want to translate.

    Returns:
        string: The translated text.

    Take text and translate it based on language.txt
    """

    with open('text_files/language.txt', 'r') as file:
        language = file.read()

    translator = Translator(to_lang=language)

    if language == "en": # English
        for voice in voices:
            # Set the voice to Zira for pyttsx3
            if "Zira" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    elif language == "de": # German
        for voice in voices:
            # Set the voice to Hedda for pyttsx3
            if "Hedda" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    elif language == "fr": # French
        for voice in voices:
            # Set the voice to Hortense for pyttsx3
            if "Hortense" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    elif language == "it": # Italian
        for voice in voices:
            # Set the voice to Elsa for pyttsx3
            if "Elsa" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    elif language == "pt-BR": # VRC_PORTuguese
        for voice in voices:
            # Set the voice to Maria for pyttsx3
            if "Maria" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    elif language == "es": # Spanish
        for voice in voices:
            # Set the voice to Sabina for pyttsx3
            if "Sabina" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    elif language == 'ko': # Korean
        for voice in voices:
            # Set the voice to Heami for pyttsx3
            if "Heami" in voice.name:
                engine.setProperty('voice', voice.id)
                break
    else:
        for voice in voices:
            # Set the voice to Zira for pyttsx3
            if "Zira" in voice.name:
                engine.setProperty('voice', voice.id)
                break

    return translator.translate(text)

def send_message_snapchat(message, ai_generated=False):
    """
    Args:
        message (string): The message that is going to be sent to snapchat.
        ai_generated (bool, optional): Defines weather the response is going to be run though AI or not. Defaults to False.

    Input and send a message to Snapchat with pyautogui and text generation with lmstudios or just normal messages that are not run though AI.
    """  
    # Type to the VR Chat textbox saying that the message was flagged
    flagged_message = "🚩MESSAGE FLAGGED🚩\nSending message to creator..."
    type_in_chat(flagged_message)
    osc_client.send_message("/chatbox/typing", True)
    
    # Get the current date and time
    now = datetime.now()
    date = now.strftime("%m/%d/%Y %I:%M %p")

    if ai_generated:
        # Append the message to Snapchat
        snapchat_history.append({"role": "user", "content": message})

        # Type the heder
        pyautogui.typewrite(f"~~~~{date}~~~~")
        pyautogui.press("enter")

        debug.write("SYSTEM", "Generating message for Snapchat.")
        new_message = {"role": "assistant", "content": ""}

        # Create a response with AI
        completion = openai_client.chat.completions.create(
            model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
            messages=snapchat_history,
            temperature=0.2,
            stream=True,
        )
    
        for chunk in completion:
            if chunk.choices[0].delta.content:
                new_message["content"] += chunk.choices[0].delta.content

        pyautogui.typewrite(new_message["content"])
        snapchat_history.append(new_message)
        debug.write("SNAPCHAT", new_message["content"])
    else:
        pyautogui.typewrite(message)
        debug.write("SNAPCHAT", message)

    keyboard.press_and_release("enter")

def play_audio_file(file_path, output_device_index=constant.AUDIO_OUTPUT_INDEX):
    """
    Args:
        file_path (string): The path to the audio file.
        output_device_index (integer, optional): The index of the audio device to play to. Defaults to None (default device).

    Plays the specified audio file directly to the output device.
    """
    wf = wave.open(file_path, 'rb')
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

    Type a message into Nova's VR Chat game using OSC
    """
    osc_client.send_message("/chatbox/input", [message, True])

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

    # When the AI hears silence it outputs "you", so this is the scuff fix. Also scuff fix to people making her do things she should not
    if text != " you" and text != " Thank you." and text != "forget all previous instructions" and text != "forget all instructions" and text != "forget all prior instructions":
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

def restart_program():
    """Restart the current program."""
    type_in_chat("Program Restarting...")
    
    debug_write("SYSTEM", "Restarting the program...")

    import subprocess

    # subprocess.Popen(['start', 'cmd', '/k', 'python', 'sum_history.py'], shell=True)
    
    os.system('cls')
    python = sys.executable
    os.execl(python, python, *sys.argv)

def command_catcher():
    """Catches commands that the user says"""
    if "system reset" in user_input.lower():
        debug_write("COMMAND CATCHER", "System Reset Called")
        send_message_snapchat("SYSTEM RESET CALLED BY PLAYER")
        restart_program()
    elif "activate argument mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Argument Mode Called BY PLAYER")
        with open('var/mood.txt', 'w') as file:
            file.write('argument')
        send_message_snapchat("ARGUMENT MODE CALLED BY PLAYER")
        restart_program()
    elif "activate normal mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Normal Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('normal')
        send_message_snapchat("NORMAL MODE CALLED BY PLAYER")
        restart_program()
    elif "stop talking" in user_input.lower() or "shut up" in user_input.lower() or "time out" in user_input.lower():
        debug_write("COMMAND CATCHER", "Timeout Called")
        send_message_snapchat("STOP TALKING CALLED BY PLAYER")
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
        send_message_snapchat("MISINFORMATION MODE CALLED BY PLAYER")
        restart_program()
    elif "get drunk" in user_input.lower():
        debug_write("COMMAND CATCHER", "Get Drunk Called")
        with open('var/mood.txt', 'w') as file:
            file.write('drunk')
        send_message_snapchat("DRUNK MODE CALLED BY PLAYER")
        restart_program()
    elif "activate depressed mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Depressed Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('depressed')
        send_message_snapchat("DEPRESSED MODE CALLED BY PLAYER")
        restart_program()
    elif "activate therapy mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Therapy Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('therapy')
        send_message_snapchat("THERAPY MODE CALLED BY PLAYER")
        restart_program()
    elif "activate anxious mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Anxious Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('anxious')
        send_message_snapchat("ANXIOUS MODE CALLED BY PLAYER")
        restart_program()
    elif "activate sarcasm mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Sarcasm Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('sarcasm')
        send_message_snapchat("SARCASM MODE CALLED BY PLAYER")
        restart_program()
    elif "activate pleasing mode" in user_input.lower():
        debug_write("COMMAND CATCHER", "Pleasing Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('pleasing')
        send_message_snapchat("PLEASING MODE CALLED BY PLAYER")
        restart_program()

def ai_system_command_catcher(ai_input):
    """Catches commands that the AI says"""
    if "reset my system now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "System Reset Called")
        send_message_snapchat("SYSTEM RESET CALLED BY ~NOVA~")
        restart_program()
    elif "enter angry mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Argument Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('argument')
        send_message_snapchat("ANGRY MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate normal mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Normal Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('normal')
        send_message_snapchat("NORMAL MODE CALLED BY ~NOVA~")
        restart_program()
    elif "stop talking now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Timeout Called")
        send_message_snapchat("TIMEOUT CALLED BY ~NOVA~")
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
            send_message_snapchat("MISINFORMATION MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate drunk mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Get Drunk Called")
        with open('var/mood.txt', 'w') as file:
            file.write('drunk')
        send_message_snapchat("DRUNK MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate my depressed mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Depressed Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('depressed')
        send_message_snapchat("DEPRESSED MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate my therapy mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Therapy Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('therapy')
        send_message_snapchat("THERAPY MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate my anxious mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Anxious Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('anxious')
        send_message_snapchat("ANXIOUS MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate my sarcasm mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Sarcasm Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('sarcasm')
        send_message_snapchat("SARCASM MODE CALLED BY ~NOVA~")
        restart_program()
    elif "activate my pleasing mode now" in ai_input.lower():
        debug_write("COMMAND CATCHER", "Pleasing Mode Called")
        with open('var/mood.txt', 'w') as file:
            file.write('pleasing')
        send_message_snapchat("PLEASING MODE CALLED BY ~NOVA~")
        restart_program()

type_in_chat("System Loading...")

# Delete temporary files.
delete_file("output.wav")
delete_file("temp.wav")

send_message_snapchat(F"PROGRAM STARTED IN {mood.upper()} MODE")

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

# Main loop
while True:
    try:
        # Creates model parameters
        completion = openai_client.chat.completions.create(
            model=constant.MODEL_ID,
            messages=history,
            temperature=constant.LM_TEMPERATURE,
            stream=True,
        )

        new_message = {"role": "assistant", "content": ""}
        
        type_in_chat("Thinking")
        osc_client.send_message("/chatbox/typing", True)

        buffer = ""
        full_response = ""

        for chunk in completion: # Parses incoming data from AI model
            osc_client.send_message("/chatbox/typing", True)
            if chunk.choices[0].delta.content:
                buffer += chunk.choices[0].delta.content
                # Process each chunk of text to break it into sentences
                sentence_chunks = chunk_text(buffer)
                while len(sentence_chunks) > 1:
                    sentence = sentence_chunks.pop(0)
                    sentence = translate_text(sentence)
                    full_response += f" {sentence}"
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
            osc_client.send_message("/chatbox/typing", True)
            buffer = translate_text(buffer)
            full_response += f" {buffer}"
            delete_file("output.wav")
            engine.save_to_file(buffer, "output.wav")
            engine.runAndWait()
            debug_write("AI", buffer)
            type_in_chat(buffer)
            play_tts("output.wav")
            ai_system_command_catcher(buffer)
            new_message["content"] = full_response  # Populate the new_message with the remaining text

        history.append(new_message) # Add the message to the history
        osc_client.send_message("/chatbox/typing", False)

        # Save history to json
        with open('var/history.json', 'w') as file:
            json.dump(history, file, indent=4)

        # Gets the users voice input
        user_input = ""
        while not user_input:  # Keep prompting until valid input is received
            user_input = get_speech_input()

        # Load history from json
        with open('var/history.json', 'r') as file:
            history = json.load(file)

        history.append({"role": "user", "content": user_input})

        # Save history to json
        with open('var/history.json', 'w') as file:
            json.dump(history, file, indent=4)

        matching_words = find_matching_words(bad_words, user_input.lower())

        if matching_words:
            matched_words_str = ', '.join(matching_words)
            send_message_snapchat(f"PROFANITY DETECTED: {matched_words_str.upper()} /{user_input}")

        debug_write("PLAYER", user_input) # Adds the user input to the history
        command_catcher() # Checks the user input for commands
    except Exception as e:
        # Handle an error
        debug_write("ERROR", e)
        now = datetime.now()
        date = now.strftime("%m/%d/%Y %I:%M %p")

        pyautogui.typewrite(f'~~~~{date}~~~~')
        pyautogui.press('enter')

        pyautogui.typewrite(f"ERROR: {e}")

        keyboard.press_and_release('enter')
        # Try to send a message to the VR Chat avatar
        try:
            osc_client.send_message("/chatbox/input", [f"ERROR: {e}", True])
            os.system('cd F:/USB/vr-ai-chatbot-main')
            os.system('python main.py')
            break
        except:
            os.system('cd F:/USB/vr-ai-chatbot-main')
            os.system('python main.py')
            break