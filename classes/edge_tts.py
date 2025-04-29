# edge_tts.py

import logging
import asyncio
import edge_tts
import queue
import tempfile
import threading
import os
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import numpy as np


class TextToSpeechManager:
    def __init__(self,
                 voice_engine="edge-tts",
                 voice=None,
                 device_index=None,
                 VRChatOSC=None
                 ):
        self.voice_engine = voice_engine
        self.voice = voice
        self.tts_queue = queue.Queue()  # Queue for text to generate audio
        self.audio_queue = queue.Queue()  # Queue for generated audio files
        self.is_playing = False
        self.device_index = device_index
        self.initialize_tts_engine()
        self.osc = VRChatOSC
        self.lock = threading.Lock()  # Lock to ensure sequential processing

    def initialize_tts_engine(self):
        if self.voice_engine == "edge-tts":
            pass
        else:
            logging.error(f"Unknown voice engine: {self.voice_engine}")

    def add_to_queue(self, text):
        """
        Add text to the queue for TTS generation and playback.
        """
        self.tts_queue.put(text)
        threading.Thread(target=self.process_queue, daemon=True).start()

        if not self.is_playing:
            threading.Thread(target=self.playback_loop, daemon=True).start()

    def process_queue(self):
        """
        Process the TTS queue sequentially to generate audio files in order.
        """
        while not self.tts_queue.empty():
            # Ensure only one thread processes the queue at a time
            with self.lock:
                text = self.tts_queue.get()
                self.generate_audio(text)

    def generate_audio(self, text):
        """
        Generate audio for the given text and store it in the audio queue.
        """
        logging.info(f"Generating audio for: {text}")
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='.wav'
        ) as tmp_file:
            output_file = tmp_file.name

        # Filter out emojis from the text
        text = ''.join(
            char for char in text
            if char.isprintable() and not (0x1F600 <= ord(char) <= 0x1F64F)
        )

        try:
            communicate = edge_tts.Communicate(text=text, voice=self.voice)
            asyncio.run(communicate.save(output_file))
            self.audio_queue.put((text, output_file))
            logging.info(f"Audio generated for: {text}")
        except Exception as e:
            logging.error(f"Error generating audio for '{text}': {e}")

    def playback_loop(self):
        """
        Continuously play audio files from the audio queue.
        """
        self.is_playing = True
        try:
            while not self.audio_queue.empty() or not self.tts_queue.empty():
                self.osc.set_typing_indicator(True)
                try:
                    text, filepath = self.audio_queue.get()
                    self.osc.send_message(text)
                    self.osc.set_typing_indicator(True)
                    self.play_audio_file(filepath)
                    os.remove(filepath)
                except Exception as e:
                    logging.error(f"Error during playback: {e}")
        finally:
            # Ensure `self.is_playing` is set to False when playback ends
            self.is_playing = False

    def play_audio_file(self, filepath):
        """
        Plays an audio file using sounddevice and soundfile on a specific
        audio device.
        """
        try:
            if filepath.endswith('.wav'):
                data, samplerate = sf.read(filepath)
            elif filepath.endswith('.mp3'):
                audio = AudioSegment.from_file(filepath, format='mp3')
                samples = audio.get_array_of_samples()
                data = np.array(samples).astype(np.float32) / 2**15
                samplerate = audio.frame_rate
            else:
                logging.error(f"Unsupported audio format: {filepath}")
                return
            sd.play(data, samplerate, device=self.device_index)
            sd.wait()
        except Exception as e:
            logging.error(f"Error playing audio file: {e}")

    def is_idle(self):
        """
        Check if the TTS manager is idle (no files in queue or playing).
        """
        return (
            self.tts_queue.empty() and
            self.audio_queue.empty() and
            not self.is_playing
        )


# Usage Examples
if __name__ == "__main__":
    # Initialize the TTS manager
    tts_manager = TextToSpeechManager(voice="en-US-AriaNeural")

    # Add text to the queue
    tts_manager.add_to_queue("Hello, this is the first sentence.")
    tts_manager.add_to_queue("This is the second sentence.")
    tts_manager.add_to_queue("And here is the third sentence.")

    # Wait until the queue is drained
    while not tts_manager.is_idle():
        print("\033[36mWaiting for TTS queue to finish...\033[0m")
        asyncio.sleep(1)

    print("\033[36mAll text has been spoken.\033[0m")
