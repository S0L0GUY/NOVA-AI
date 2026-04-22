"""
audio.py: Audio device I/O management.

Handles microphone input (16kHz) and speaker output (24kHz) using PyAudio.
Uses a background thread for playback to avoid blocking on write operations.
"""

import queue
import threading

import pyaudio


class AudioManager:
    """Manages microphone input and speaker output with background playback thread."""

    # Audio configuration constants
    SAMPLE_RATE_INPUT = 16000   # Microphone sample rate for Gemini Live
    SAMPLE_RATE_OUTPUT = 24000  # Speaker sample rate for Gemini Live output
    CHUNK_SIZE = 1024           # Frames per buffer

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self._playback_queue: queue.Queue[bytes] = queue.Queue()
        self._playback_stop = threading.Event()
        self._playback_thread: threading.Thread | None = None

    def initialize(self) -> None:
        """Open microphone and speaker streams, start playback thread."""
        self.input_stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.SAMPLE_RATE_INPUT,
            input=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )

        self.output_stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.SAMPLE_RATE_OUTPUT,
            output=True,
            frames_per_buffer=self.CHUNK_SIZE,
        )

        self._playback_stop.clear()
        self._playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self._playback_thread.start()

        print("Microphone and speaker initialized")

    def _playback_loop(self) -> None:
        """Continuously dequeue and play audio chunks from the playback queue."""
        while not self._playback_stop.is_set():
            try:
                chunk = self._playback_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                if chunk and self.output_stream:
                    self.output_stream.write(chunk)
            finally:
                self._playback_queue.task_done()

    def read_audio_chunk(self) -> bytes:
        """Read a audio frame from the microphone (blocking)."""
        if self.input_stream is None:
            raise RuntimeError("Input stream not initialized. Call initialize() first.")

        return self.input_stream.read(self.CHUNK_SIZE, exception_on_overflow=False)

    def write_audio_chunk(self, data: bytes) -> None:
        """Queue audio data for playback (non-blocking, processed by playback thread)."""
        if not data or self._playback_stop.is_set():
            return
        self._playback_queue.put(data)

    def interrupt_output(self) -> None:
        """Stop any currently queued audio playback immediately."""
        while True:
            try:
                self._playback_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self._playback_queue.task_done()

    def cleanup(self) -> None:
        """Close audio streams and shut down playback thread."""
        self._playback_stop.set()
        self.interrupt_output()

        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1)

        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        if self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
        self.p.terminate()
        print("Audio streams closed")
