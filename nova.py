import asyncio
from google import genai
import classes.config as config
import sounddevice as sd
import numpy as np
import mss
import io
from PIL import Image
import base64
import threading
import queue
from datetime import datetime


def print_startup_logo() -> None:
    colors = ["\033[91m", "\033[93m", "\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    lines = [
        "===========================================",
        "|                NOVA-AI                  |",
        "|          Developed by N O M A           |",
        "===========================================",
    ]

    for line in lines:
        colored_line = "".join(f"{colors[i % len(colors)]}{char}\033[0m" for i, char in enumerate(line))
        print(colored_line)


class AudioProcessor:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_queue = queue.Queue()

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}")
        # Convert float32 to int16 PCM format
        audio_data = (indata[:, 0] * 32767).astype(np.int16)
        self.audio_queue.put(audio_data.tobytes())

    def start_recording(self):
        self.is_recording = True
        self.stream = sd.InputStream(
            channels=1,
            samplerate=self.sample_rate,
            callback=self.audio_callback,
            blocksize=1024,
            dtype=np.float32
        )
        self.stream.start()
        print("🎤 Recording started...")

    def stop_recording(self):
        self.is_recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        print("🎤 Recording stopped")

    def get_audio_chunk(self, timeout=0.1):
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None


def capture_screenshot():
    """Capture the current screen and return as JPEG bytes."""
    with mss.mss() as sct:
        # Capture the primary monitor
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        # Convert to PIL Image
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

        # Convert to JPEG bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG', quality=80)
        return img_bytes.getvalue()


async def play_audio_response(audio_data):
    """Play audio response from the model."""
    try:
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32767
        sd.play(audio_array, samplerate=16000, blocking=True)
    except Exception as e:
        print(f"Error playing audio: {e}")


async def main() -> None:
    print_startup_logo()

    cfg = config.Config()
    GEMINI_API_KEY = cfg.get_gemini_api_key
    MODEL = cfg.get_gemini_model

    if not GEMINI_API_KEY or not MODEL:
        print("Error: Missing GEMINI_API_KEY or MODEL in config.yaml")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    config_dict = {
        "response_modalities": ["AUDIO"],
        "system_instruction": "You are NOVA, a helpful AI assistant that can see the user's screen and hear their voice. Be concise and helpful."
    }

    print(f"Connecting to {MODEL}...")

    audio_processor = AudioProcessor()

    async with client.aio.live.connect(model=MODEL, config=config_dict) as session:
        print("✅ Session started")
        print("\n📋 Commands:")
        print("  'screenshot' - Send current screen")
        print("  'start' - Start recording audio")
        print("  'stop' - Stop recording and send")
        print("  'quit' - Exit\n")

        try:
            while True:
                command = input("Enter command > ").strip().lower()

                if command == "quit":
                    print("Goodbye!")
                    break

                elif command == "screenshot":
                    print("📸 Capturing screenshot...")
                    screenshot_bytes = capture_screenshot()
                    screenshot_b64 = base64.standard_b64encode(screenshot_bytes).decode()

                    await session.send({
                        "mime_type": "image/jpeg",
                        "data": screenshot_b64
                    })
                    print("📸 Screenshot sent")

                    # Get and play response
                    response = await session.receive()
                    if "data" in response:
                        audio_frame = response["data"]
                        await play_audio_response(base64.standard_b64decode(audio_frame))

                elif command == "start":
                    audio_processor.start_recording()

                elif command == "stop":
                    audio_processor.stop_recording()
                    print("⏳ Processing audio...")

                    # Send accumulated audio to API
                    while not audio_processor.audio_queue.empty():
                        audio_chunk = audio_processor.get_audio_chunk()
                        if audio_chunk:
                            await session.send({
                                "mime_type": "audio/pcm",
                                "data": base64.standard_b64encode(audio_chunk).decode()
                            })

                    # Get response
                    response = await session.receive()
                    if "data" in response:
                        audio_frame = response["data"]
                        await play_audio_response(base64.standard_b64decode(audio_frame))
                    print("✅ Response complete")

                else:
                    print("Unknown command")

        except KeyboardInterrupt:
            print("\n\nSession ended")
            audio_processor.stop_recording()


if __name__ == "__main__":
    asyncio.run(main())
