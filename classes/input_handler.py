"""Input handling for audio and text."""

import asyncio
import threading


class InputHandler:
    """Manages microphone and text input in separate threads."""

    def __init__(self, audio_manager, audio_input_queue, text_input_queue):
        self.audio_manager = audio_manager
        self.audio_input_queue = audio_input_queue
        self.text_input_queue = text_input_queue
        self.loop = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start input threads."""
        self.loop = loop

        mic_thread = threading.Thread(target=self._read_microphone, daemon=True)
        text_thread = threading.Thread(target=self._read_user_text, daemon=True)

        mic_thread.start()
        text_thread.start()

    def _read_microphone(self) -> None:
        """Read audio from microphone and put into queue."""
        try:
            while True:
                data = self.audio_manager.read_audio_chunk()
                asyncio.run_coroutine_threadsafe(self.audio_input_queue.put(data), self.loop)
        except Exception as e:
            print(f"❌ Microphone error: {e}")

    def _read_user_text(self) -> None:
        """Read user text input and put into queue."""
        try:
            while True:
                user_input = input("\n📝 You: ")
                if user_input.strip():
                    asyncio.run_coroutine_threadsafe(self.text_input_queue.put(user_input), self.loop)
        except EOFError:
            pass
        except Exception as e:
            print(f"❌ Text input error: {e}")
