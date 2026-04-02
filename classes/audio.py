"""Audio I/O handling for NOVA."""

import queue
import threading

import pyaudio


class AudioManager:
    """Manages microphone input and speaker output."""

    SAMPLE_RATE_INPUT = 16000
    SAMPLE_RATE_OUTPUT = 24000
    CHUNK_SIZE = 1024

    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_stream = None
        self.output_stream = None
        self._playback_queue: queue.Queue[bytes] = queue.Queue()
        self._playback_stop = threading.Event()
        self._playback_thread: threading.Thread | None = None

    def initialize(self) -> None:
        """Initialize audio streams."""
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

        print("🎤 Microphone and speaker initialized")

    def _playback_loop(self) -> None:
        """Continuously play queued output audio."""
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
        """Read a chunk of audio from the microphone."""
        return self.input_stream.read(self.CHUNK_SIZE, exception_on_overflow=False)

    def write_audio_chunk(self, data: bytes) -> None:
        """Queue audio data for playback on the speaker."""
        if not data or self._playback_stop.is_set():
            return
        self._playback_queue.put(data)

    def interrupt_output(self) -> None:
        """Stop any queued playback immediately."""
        while True:
            try:
                self._playback_queue.get_nowait()
            except queue.Empty:
                break
            else:
                self._playback_queue.task_done()

    def cleanup(self) -> None:
        """Close audio streams."""
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
        print("✅ Audio streams closed")
