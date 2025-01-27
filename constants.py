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

# Network Settings

LOCAL_IP = "192.168.0.195"  # Your computers local IP
VRC_PORT = 9000  # VR Chat VRC_PORT, 9000 is the default

# Audio Settings
# The index of the audio output device (VB-Audio Cable B)
AUDIO_OUTPUT_INDEX = 10

# LM Settings
# The model ID of the LM
MODEL_ID = "lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF"
LM_TEMPERATURE = 0.5  # The temperature of the LM

HISTORY_PATH = "json_files/history.json"
