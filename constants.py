"""
Constants module for Nova AI project.
This module contains all the configuration constants used throughout the
project.
Constants:
    Network Settings:
        LOCAL_IP (str): Local IP address of the computer
        VRC_PORT (int): VRChat port number, default is 9000
    Audio Settings:
        AUDIO_OUTPUT_INDEX (int): Index number for audio output device
        (VB-Audio Cable B)
    Language Model Settings:
        MODEL_ID (str): Identifier for the language model being used
        LM_TEMPERATURE (float): Temperature setting for language model output
        generation
    File Paths:
        HISTORY_PATH (str): Path to the history JSON file
Note:
    Make sure to adjust LOCAL_IP and AUDIO_OUTPUT_INDEX according to your
    system configuration.
"""


class Network:
    """
    Class representing network configuration parameters.
    Attributes:
        LOCAL_IP (str): The local IP address of the computer running the
        application.
        VRC_PORT (int): The port number used for VRChat communication. Default
        is 9000.
    """
    LOCAL_IP = "192.168.0.195"
    VRC_PORT = 9000


class Audio:
    """
    A class containing audio device configuration constants.
    This class defines constants for audio input and output device indices,
    specifically for VB-Audio Cable virtual audio devices.
    Attributes:
        AUDIO_OUTPUT_INDEX (int): The device index for audio output,
            configured for VB-Audio Cable B Input (default: 10)
        AUDIO_INPUT_INDEX (int): The device index for audio input,
            configured for VB-Audio Cable A Output (default: 16)
    """
    AUDIO_OUTPUT_INDEX = 10
    AUDIO_INPUT_INDEX = 16


class Voice:
    """
    A class that defines constants for voice-related configurations in
    Text-to-Speech (TTS) operations.
    Attributes:
        VOICE_NAME (str): The default voice name used for text-to-speech
        synthesis. Currently set to "Zira".
    """
    VOICE_NAME = "Zira"


class LanguageModel:
    """
    A class representing configuration settings for a language model.
    This class contains constant values that define the behavior and identity
    of the language model being used.
    Attributes:
        MODEL_ID (str): The identifier for the specific language model being
        used. Currently set to Meta-Llama 3.1 8B Instruct GGUF model.
        LM_TEMPERATURE (float): The temperature parameter for the language
        model's output. Controls randomness in text generation (0.0 to 1.0,
        where higher means more random).
    """
    MODEL_ID = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
    LM_TEMPERATURE = 0.5


class FilePaths:
    """
    A class containing file path constants used in the application.
    Attributes:
        HISTORY_PATH (str): The path to the JSON file storing history data.
                           Default is "json_files/history.json"
    """
    HISTORY_PATH = "json_files/history.json"
