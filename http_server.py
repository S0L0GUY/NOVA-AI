# Split the long comment line
# from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
import json
import urllib.parse
import wave
import pyaudio
import os


# The index of the audio output device (VB-Audio Cable B)
AUDIO_OUTPUT_INDEX = 7  # VB-Audio Cable B


def play_audio_file(output_device_index=AUDIO_OUTPUT_INDEX):
    """
    Args:
        file_path (string): The path to the audio file.
        output_device_index (integer, optional): The index of the audio device
            to play to. Defaults to None (default device).

    Plays the specified audio file directly to the output device.
    """
    # TODO: Make a list of playable sounds
    directory = 'audio_files'
    file_list = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))

    file_path = ""  # TODO: Assign the file path to what the user selects

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


def add_message(message):
    """
    Args:
        message (string): The message to add to the history.

    Returns:
        string: Success message.

    Add a message as "user" to history.json.
    """
    with open('history.json', 'r') as file:
        history = json.load(file)

    history.append({"role": "user", "content": message})

    with open('var/history.json', 'w') as file:
        json.dump(history, file, indent=4)

    return f"Added '{message}' to history."


def mood():
    """
    Returns:
        string: The current mood.

    Look in var/mood.txt and return the value as a string.
    """
    with open('var/mood.txt', 'r') as file:
        # Get the current mood
        mood = file.read()

    return f"mood: {mood}"


def logs():
    """
    Returns:
        string: The content of history.json as a string.

    Look at history.json, format it as a string, and return it.
    """
    with open('history.json', 'r') as file:
        loaded_data = json.load(file)
    return json.dumps(loaded_data, indent=4)


def status():
    """
    Returns:
        string: "Server is operational"

    Return a message indicating that the server is online and ready.
    """
    return "Server is operational"


def remove_leading_space(s):
    """
    Args:
        s (string): The inputted command.

    Returns:
        string: The inputted command without a leading space in front.

    Look to see if there is a space at the front of the command and remove it.
    """
    if s and s[0] == ' ':
        return s[1:]
    return s


def reset_logs():
    """
    Returns:
        string: Success message.

    Reset the logs in history.json to the original state and return success.
    """
    mood_prompts = {
        "normal": 'text_files/prompts/normal_system_prompt.txt',
        "argument": 'text_files/prompts/argument_system_prompt.txt',
        "misinformation": ('text_files/prompts/'
                           'misinformation_system_prompt.txt'),
        "drunk": 'text_files/prompts/drunk_system_prompt.txt',
        "depressed": 'text_files/prompts/depressed_system_prompt.txt',
        "therapy": 'text_files/prompts/therapy_system_prompt.txt',
        "anxious": 'text_files/prompts/anxious_system_prompt.txt',
        "sarcasm": 'text_files/prompts/sarcasm_system_prompt.txt',
        "pleasing": 'text_files/prompts/pleasing_system_prompt.txt'
    }

    system_prompt_file = mood_prompts.get(
        mood, 'text_files/prompts/normal_system_prompt.txt')

    with open(system_prompt_file, 'r') as file:
        system_prompt = file.read()

    with open('text_files/prompts/additional_system_prompt.txt', 'r') as file:
        additional_system_prompt = file.read()

    # Construct the final system prompt
    system_prompt = f"{system_prompt} \n {additional_system_prompt}"

    now = datetime.now()

    history = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Today is {now.strftime('%Y-%m-%d')}"},
        {"role": "user", "content": "Hey"},
        {"role": "assistant", "content": "Hi, im Nova."},
        {"role": "user", "content": "Are you a real person?"},
        {"role": "assistant", "content": "Yea"},
    ]

    with open('history.json', 'w') as file:
        json.dump(history, file, indent=4)

    return "Logs Cleared"


def change_language(language):
    supported_languages = {
        "en", "de", "fr", "it", "pt-PT", "es", "hi", "th", "ko", "tr-TR"
    }

    formatted_language = remove_leading_space(language).lower()

    if formatted_language in supported_languages:
        with open('text_files/language.txt', 'w', encoding='utf-8') as file:
            file.write(formatted_language)
        return f"Changed language to {formatted_language}."
    else:
        return (f"{formatted_language} is not supported.\n"
                f"Supported Languages:\n{supported_languages}")


def handle_command(user_command, *args):
    """
    Args:
        user_command (string): The command to be run.

    Returns:
        string: The outputting message.

    Handle a command and return the output of whatever was run.
    """
    command = remove_leading_space(user_command)

    if command == "add_message":
        return add_message(" ".join(args))
    elif command == "logs":
        return logs()
    elif command == "status":
        return status()
    elif command == "mood":
        return mood()
    elif command == "restart":
        return reset_logs()
    elif command == "change_language":
        return change_language(" ".join(args))
    else:
        return "Command Not Found."


class RequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, message):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(message.encode())

    def do_GET(self):
        path = self.path[1:]  # Remove the leading '/'
        parsed_path = urllib.parse.unquote(path)  # Decode URL encoding
        command_parts = parsed_path.split('/')
        command = command_parts[0]
        args = command_parts[1:]

        try:
            result = handle_command(command, *args)
            self._send_response(result)
        except Exception as e:
            self._send_response(f"Error: {str(e)}")


def run(
    server_class=ThreadingHTTPServer,
    handler_class=RequestHandler,
    port=8080
):
    """
    Args:
        server_class: The type of server that is being run.
        handler_class: The type of request handler that is being used.
        port (integer, optional): The port that the server is hosted on.

    Create a web server on port 8080
    """
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting httpd server on port {port}...')
    httpd.serve_forever()


if __name__ == "__main__":
    run()
