import asyncio

import classes.config as config
from classes.audio import AudioManager
from classes.gemini_live import GeminiLive
from classes.input_handler import InputHandler
from classes.ui import print_startup_logo, handle_event


async def main() -> None:
    print_startup_logo()

    cfg = config.Config()
    GEMINI_API_KEY = cfg.get_gemini_api_key
    MODEL = cfg.get_gemini_model
    SYSTEM_PROMPT = cfg.get_system_prompt
    VOICE_NAME = cfg.get_gemini_voice

    if not GEMINI_API_KEY or not MODEL:
        print("Error: Missing GEMINI_API_KEY or MODEL in config.yaml")
        return

    # Initialize audio
    audio_manager = AudioManager()
    audio_manager.initialize()

    # Create communication queues
    audio_input_queue = asyncio.Queue()
    text_input_queue = asyncio.Queue()
    video_input_queue = asyncio.Queue()

    # Initialize input handler
    input_handler = InputHandler(audio_manager, audio_input_queue, text_input_queue)

    # Initialize Gemini Live
    gemini_live = GeminiLive(
        api_key=GEMINI_API_KEY,
        model=MODEL,
        input_sample_rate=AudioManager.SAMPLE_RATE_INPUT,
        system_instruction=SYSTEM_PROMPT,
        voice_name=VOICE_NAME,
    )

    print("🚀 Starting Gemini Live session...")

    try:
        loop = asyncio.get_running_loop()
        input_handler.start(loop)

        # Process Gemini Live events
        async for event in gemini_live.start_session(
            audio_input_queue=audio_input_queue,
            video_input_queue=video_input_queue,
            text_input_queue=text_input_queue,
            audio_output_callback=audio_manager.write_audio_chunk,
            audio_interrupt_callback=audio_manager.interrupt_output,
        ):
            handle_event(event)
            if event.get("type") == "error":
                break
    except Exception as e:
        print(f"❌ Session error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        audio_manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
