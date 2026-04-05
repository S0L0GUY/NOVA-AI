"""
input_handler.py: Bridges blocking I/O operations with async event loop.

Runs microphone and text input reading on separate threads and safely queues
data for async processing via asyncio.run_coroutine_threadsafe().
"""

import asyncio
import threading


class InputHandler:
    """
    Manages microphone and text input in separate threads.

    Reads from blocking sources (microphone, stdin) on dedicated threads and
    thread-safely queues data into the async event loop for processing.
    """

    def __init__(self, audio_manager, audio_input_queue, text_input_queue):
        self.audio_manager = audio_manager
        self.audio_input_queue = audio_input_queue
        self.text_input_queue = text_input_queue
        self.loop = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start input threads and provide them with the async event loop reference."""
        self.loop = loop

        mic_thread = threading.Thread(target=self._read_microphone, daemon=True)
        text_thread = threading.Thread(target=self._read_user_text, daemon=True)

        mic_thread.start()
        text_thread.start()

    def _read_microphone(self) -> None:
        """Read audio from microphone in a loop and queue it for async processing."""
        try:
            while True:
                data = self.audio_manager.read_audio_chunk()
                asyncio.run_coroutine_threadsafe(self.audio_input_queue.put(data), self.loop)
        except Exception as e:
            print(f"Microphone error: {e}")

    def _read_user_text(self) -> None:
        """Read user text input in a loop and queue it for async processing."""
        try:
            while True:
                user_input = input("\nYou: ")
                if user_input.strip():
                    asyncio.run_coroutine_threadsafe(self.text_input_queue.put(user_input), self.loop)
        except EOFError:
            pass
        except Exception as e:
            print(f"Text input error: {e}")
