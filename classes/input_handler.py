"""
input_handler.py: Bridges blocking I/O operations with async event loop.

Runs microphone, text input, and screenshot capture on separate threads and safely queues
data for async processing via asyncio.run_coroutine_threadsafe().
"""

import asyncio
import threading
import time
 
from classes.screenshot import ScreenshotManager


class InputHandler:
    """
    Manages microphone, text input, and screenshot capture in separate threads.

    Reads from blocking sources (microphone, stdin, screenshots) on dedicated threads and
    thread-safely queues data into the async event loop for processing.
    """

    def __init__(
        self,
        audio_manager,
        audio_input_queue,
        text_input_queue,
        video_input_queue=None,
        screenshot_interval=1.5,
    ):
        self.audio_manager = audio_manager
        self.audio_input_queue = audio_input_queue
        self.text_input_queue = text_input_queue
        self.video_input_queue = video_input_queue
        self.screenshot_interval = screenshot_interval
        self.screenshot_manager = (
            ScreenshotManager(target_window_name="VRChat")
            if video_input_queue
            else None
        )
        self.loop: asyncio.AbstractEventLoop | None = None

    def start(self, loop: asyncio.AbstractEventLoop) -> None:
        """Start input threads and provide them with the async event loop reference."""
        self.loop = loop

        mic_thread = threading.Thread(target=self._read_microphone, daemon=True)
        text_thread = threading.Thread(target=self._read_user_text, daemon=True)

        mic_thread.start()
        text_thread.start()

        if self.screenshot_manager and self.video_input_queue:
            screenshot_thread = threading.Thread(target=self._capture_screenshots, daemon=True)
            screenshot_thread.start()

    def _read_microphone(self) -> None:
        """Read audio from microphone in a loop and queue it for async processing."""
        try:
            while True:
                data = self.audio_manager.read_audio_chunk()
                if self.loop:
                    asyncio.run_coroutine_threadsafe(self.audio_input_queue.put(data), self.loop)
        except Exception as e:
            print(f"Microphone error: {e}")

    def _read_user_text(self) -> None:
        """Read user text input in a loop and queue it for async processing."""
        try:
            while True:
                user_input = input()
                if user_input.strip() and self.loop:
                    asyncio.run_coroutine_threadsafe(self.text_input_queue.put(user_input), self.loop)
        except EOFError:
            pass
        except Exception as e:
            print(f"Text input error: {e}")

    def _capture_screenshots(self) -> None:
        """Capture screenshots periodically and queue them for async processing."""
        if self.screenshot_manager is None or self.video_input_queue is None:
            return

        screenshot_manager = self.screenshot_manager
        video_input_queue = self.video_input_queue

        try:
            while True:
                jpeg_data = screenshot_manager.capture_screenshot()
                if jpeg_data and self.loop:
                    asyncio.run_coroutine_threadsafe(video_input_queue.put(jpeg_data), self.loop)
                time.sleep(self.screenshot_interval)
        except Exception as e:
            print(f"Screenshot error: {e}")
