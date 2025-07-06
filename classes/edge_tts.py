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
import constants as constant


class TextToSpeechManager:
    def __init__(self,
                 voice_engine=constant.TTSSettings.ENGINE,
                 voice=None,
                 device_index=None,
                 VRChatOSC=None
                 ) -> None:

        self.voice_engine = voice_engine
        self.voice = voice
        self.tts_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.device_index = device_index
        self.initialize_tts_engine()
        self.osc = VRChatOSC
        self.lock = threading.Lock()

    def initialize_tts_engine(self) -> None:
        """
        Initializes the Text-to-Speech (TTS) engine based on the specified
        voice engine. This method checks the value of `self.voice_engine` and
        performs initialization for the "edge-tts" engine. If the specified
        voice engine is not recognized, an error is logged.
        Raises:
            logging.error: If the `self.voice_engine` is not "edge-tts".
        """

        if self.voice_engine == constant.TTSSettings.ENGINE:
            pass
        else:
            logging.error(f"Unknown voice engine: {self.voice_engine}")

    def add_to_queue(self, text: str) -> None:
        """
        Adds a text string to the TTS (Text-to-Speech) processing queue and
        starts the necessary threads for processing and playback.
        Args:
            text (str): The text string to be added to the TTS queue.
        Behavior:
            - The method places the provided text into the `tts_queue`.
            - It starts a thread to process the queue using the `process_queue`
            method.
            - If playback is not currently active (`is_playing` is False), it
            starts another thread to handle audio playback using the
            `playback_loop` method.
        """

        self.tts_queue.put(text)
        threading.Thread(target=self.process_queue, daemon=True).start()

        if not self.is_playing:
            threading.Thread(target=self.playback_loop, daemon=True).start()

    def process_queue(self) -> None:
        """
        Processes the text-to-speech (TTS) queue by generating audio for each
        text item in the queue. This method ensures that only one thread
        processes the queue at a time by using a lock. It retrieves text items
        from the queue and calls the `generate_audio` method to generate the
        corresponding audio.
        Returns:
            None
        """

        while not self.tts_queue.empty():
            with self.lock:
                text = self.tts_queue.get()
                self.generate_audio(text)

    def generate_audio(self, text: str) -> None:
        """
        Generate an audio file from the given text using the edge_tts library.
        This method processes the input text, filters out emojis and
        non-printable characters, and generates a .wav audio file using the
        specified voice. The generated audio file is then added to the audio
        queue.
        Args:
            text (str): The input text to convert into audio.
        Raises:
            Exception: If an error occurs during the audio generation process.
        Logs:
            - Logs an info message when audio generation starts and completes.
            - Logs an error message if audio generation fails.
        Notes:
            - The generated audio file is stored in a temporary file with a
            .wav suffix.
            - The method uses asyncio to run the edge_tts.Communicate.save()
            function.
        """

        logging.info(f"Generating audio for: {text}")
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='.wav'
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            communicate = edge_tts.Communicate(text=text, voice=self.voice)
            asyncio.run(communicate.save(output_file))
            self.audio_queue.put((text, output_file))
            logging.info(f"Audio generated for: {text}")
        except Exception as e:
            logging.error(f"Error generating audio for '{text}': {e}")

    def playback_loop(self) -> None:
        """
        Handles the playback loop for audio files in the queue.
        This method continuously processes audio and text from the
        `audio_queue` and `tts_queue` until both are empty. It sets the typing
        indicator, sends messages, plays audio files, and removes the files
        after playback. If an error occurs during playback, it logs the error.
        Attributes:
            self.is_playing (bool): Indicates whether playback is currently
            active.
        Exceptions:
            Logs any exceptions that occur during playback.
        Note:
            Ensures `self.is_playing` is set to False when the playback loop
            ends.
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
            self.is_playing = False

    def play_audio_file(self, filepath: str) -> None:
        """
        Plays an audio file using the specified audio device.
        Args:
            filepath (str): The path to the audio file to be played. Supported
            formats are '.wav' and '.mp3'.
        Raises:
            Exception: Logs an error message if there is an issue reading or
            playing the audio file.
        Notes:
            - For '.wav' files, the file is read using the `soundfile` library.
            - For '.mp3' files, the file is read using the `pydub` library and
            converted to a NumPy array.
            - Unsupported audio formats will log an error and the function
            will return without playing audio.
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
        Check if the TTS (Text-to-Speech) system is idle.
        Returns:
            bool: True if the TTS queue and audio queue are both empty,
                  and no audio is currently playing. False otherwise.
        """

        return (
            self.tts_queue.empty() and
            self.audio_queue.empty() and
            not self.is_playing
        )
