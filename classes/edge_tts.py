import asyncio
import hashlib
import logging
import os
import queue
import shutil
import tempfile
import threading
from pathlib import Path

import edge_tts
import numpy as np
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment

import constants as constant


class TextToSpeechManager:
    def __init__(
        self,
        voice_engine=constant.TTSSettings.ENGINE,
        voice=None,
        device_index=None,
        VRChatOSC=None,
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

        # Ensure cache directory exists if caching enabled
        self.caching_enabled = bool(constant.TTSSettings.ENABLE_CACHING)
        self.cache_dir = Path(constant.TTSSettings.CACHE_DIR)
        if self.caching_enabled:
            try:
                self.cache_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logging.error(f"Failed to create TTS cache directory '{self.cache_dir}': {e}")
                self.caching_enabled = False

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
        Caches generated audio files when caching is enabled. The audio_queue
        will receive tuples of (text, filepath, is_cached).
        """
        logging.info(f"Generating audio for: {text}")

        # Prepare cache key using voice + normalized text
        normalized = " ".join(text.strip().split())  # collapse whitespace
        key_source = f"{self.voice or ''}|{normalized}".encode("utf-8")
        key = hashlib.sha256(key_source).hexdigest()
        cached_filename = f"{key}.wav"
        cached_path = self.cache_dir / cached_filename

        # If caching enabled and cached file exists, reuse it
        if self.caching_enabled and cached_path.exists():
            logging.info(f"TTS cache hit for text (hash={key})")
            self.audio_queue.put((text, str(cached_path), True))
            return

        # Otherwise generate audio to a temporary file, then move to cache (if enabled)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            output_file = tmp_file.name

        try:
            communicate = edge_tts.Communicate(text=text, voice=self.voice, boundary="WordBoundary")
            asyncio.run(communicate.save(output_file))

            if self.caching_enabled:
                try:
                    shutil.move(output_file, str(cached_path))
                    logging.info(f"Audio cached at: {cached_path}")
                    self.audio_queue.put((text, str(cached_path), True))
                except Exception as e:
                    logging.error(f"Failed to move generated audio to cache: {e}. Using temp file.")
                    self.audio_queue.put((text, output_file, False))
            else:
                self.audio_queue.put((text, output_file, False))

            logging.info(f"Audio generated for: {text}")
        except Exception as e:
            logging.error(f"Error generating audio for '{text}': {e}")
            # Clean up temp file if it exists and wasn't moved
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
            except Exception:
                pass

    def playback_loop(self) -> None:
        """
        Handles the playback loop for audio files in the queue.
        Expects audio_queue items to be (text, filepath, is_cached).
        Cached files are NOT deleted after playback.
        """
        self.is_playing = True
        try:
            while not self.audio_queue.empty() or not self.tts_queue.empty():
                self.osc.set_typing_indicator(True)
                try:
                    # Updated to unpack cached flag
                    item = self.audio_queue.get()
                    if len(item) == 3:
                        text, filepath, is_cached = item
                    else:
                        # Backwards compatibility: if older tuple present
                        text, filepath = item
                        is_cached = False

                    self.osc.send_message(text)
                    self.osc.set_typing_indicator(True)
                    self.play_audio_file(filepath)

                    # Only remove files that are not cached
                    if not is_cached:
                        try:
                            os.remove(filepath)
                        except Exception:
                            pass
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
        """
        try:
            if filepath.endswith(".wav"):
                data, samplerate = sf.read(filepath)
            elif filepath.endswith(".mp3"):
                audio = AudioSegment.from_file(filepath, format="mp3")
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
        return self.tts_queue.empty() and self.audio_queue.empty() and not self.is_playing
