# outputmanager.py

import logging
import asyncio
from pythonosc.udp_client import SimpleUDPClient
import edge_tts
import queue
import tempfile
import threading
import os
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
import numpy as np


class OutputManager:
    def __init__(
        self,
        chatbox_ip="127.0.0.1",
        chatbox_port=9000,
        voice_engine="edge-tts",
        voice=None, 
        device_index=None
    ):
        self.chatbox_ip = chatbox_ip
        self.chatbox_port = chatbox_port
        self.client = SimpleUDPClient(self.chatbox_ip, self.chatbox_port)
        self.voice_engine = voice_engine
        self.voice = voice
        self.tts_queue = queue.Queue()
        self.is_playing = False
        self.playback_thread = None  # For managing playback thread
        self.initialize_tts_engine()
        self.device_index = device_index

    def initialize_tts_engine(self):
        if self.voice_engine == "edge-tts":
            pass
        else:
            logging.error(f"Unknown voice engine: {self.voice_engine}")

    def update_settings(
        self, chatbox_ip, chatbox_port, voice_engine, voice, device_index
    ):
        old_engine = self.voice_engine
        self.chatbox_ip = chatbox_ip
        self.chatbox_port = int(chatbox_port)
        self.client = SimpleUDPClient(self.chatbox_ip, self.chatbox_port)
        self.voice_engine = voice_engine
        self.voice = voice
        self.device_index = device_index

        # No need to re-initialize pygame.mixer

        if old_engine != self.voice_engine:
            self.initialize_tts_engine()

    def speak_text(self, text):
        self.tts_queue.put(text)
        if not self.is_playing:
            threading.Thread(
                target=self.tts_playback_loop, daemon=True
            ).start()

    def tts_playback_loop(self):
        while not self.tts_queue.empty():
            text = self.tts_queue.get()
            if self.voice_engine == "edge-tts":
                asyncio.run(self.generate_and_play_audio_edge(text))
            elif self.voice_engine == "aws-polly":
                self.generate_and_play_audio_polly(text)
            else:
                logging.error(f"Unknown voice engine: {self.voice_engine}")

    async def generate_and_play_audio_edge(self, text):
        logging.info("Generating speech with Edge TTS...")
        with tempfile.NamedTemporaryFile(
            delete=False, suffix='.wav'
        ) as tmp_file:
            output_file = tmp_file.name

        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=self.voice
            )
            await communicate.save(output_file)
            logging.info("Playing Edge TTS audio...")
            self.play_audio_file(output_file)
            logging.info("Edge TTS audio playback finished.")
        except Exception as e:
            logging.error(f"Error during Edge TTS playback: {e}")
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)

    def play_audio_file(self, filepath):
        """
        Plays an audio file using sounddevice and soundfile on a specific
        audio device.
        """
        try:
            self.stop_audio()
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
            self.is_playing = True
            sd.play(data, samplerate, device=self.device_index)
            sd.wait()
            self.is_playing = False
        except Exception as e:
            logging.error(f"Error playing audio file: {e}")
            self.is_playing = False

    def stop_audio(self):
        """Stops audio playback."""
        if self.is_playing:
            sd.stop()
            self.is_playing = False

    def send_to_chatbox(self, text):
        logging.info(f"Sending to chatbox: {text}")
        self.client.send_message("/chatbox/input", [text, True])
