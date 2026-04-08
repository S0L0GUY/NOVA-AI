import asyncio
import os
import sys

import classes.config as config
from classes.audio import AudioManager
from classes.gemini_live import GeminiLive
from classes.input_handler import InputHandler
from classes.osc import VRChatOSC
from classes.ui import print_startup_logo, handle_event, log
from classes.tool_definitions import get_tool_definitions, get_tool_mapping
from classes.memory import MemoryManager

# Force unbuffered output for real-time terminal updates
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout = type(sys.stdout)(sys.stdout.buffer, encoding=sys.stdout.encoding, errors="replace", newline=None, write_through=True)


async def _banner_resend_loop(vrchat_osc: "VRChatOSC", is_talking: dict) -> None:
    """Periodically resend banner every 5 seconds when not talking (VRChat OSC compliance)."""
    banner_text = "-----------------------\nCome talk to me!\n-----------------------\nVRChat AI Assistant\n-----------------------"

    while True:
        try:
            if not is_talking["active"]:
                vrchat_osc.set_banner(banner_text)
            await asyncio.sleep(5.0)
        except Exception as e:
            log(f"Banner resend error: {e}", "error")
            await asyncio.sleep(5.0)


async def main() -> None:
    """
    Main entry point for NOVA-AI.

    Orchestrates the initialization of all components:
    - Config loading from YAML files
    - Audio input/output management
    - Gemini Live session for multimodal AI interaction
    - VRChat OSC integration for avatar control and chatbox
    - Input handling for keyboard/microphone input

    Processes Gemini Live events and routes responses to VRChat chatbox.
    """
    print_startup_logo()

    # Load configuration
    cfg = config.Config()
    GEMINI_API_KEY = cfg.get_gemini_api_key
    MODEL = cfg.get_gemini_model
    SYSTEM_PROMPT = cfg.get_system_prompt
    VOICE_NAME = cfg.get_gemini_voice
    OSC_ENABLED = cfg.get_osc_enabled

    if not GEMINI_API_KEY or not MODEL:
        log("Missing GEMINI_API_KEY or MODEL in config.yaml", "error")
        return

    # Initialize audio
    audio_manager = AudioManager()
    audio_manager.initialize()

    # Create communication queues for different input types
    audio_input_queue = asyncio.Queue()
    text_input_queue = asyncio.Queue()
    video_input_queue = asyncio.Queue()

    # Initialize input handler
    input_handler = InputHandler(audio_manager, audio_input_queue, text_input_queue)

    # Initialize VRChat OSC integration if enabled
    vrchat_osc = VRChatOSC(cfg) if OSC_ENABLED else None

    # Initialize Memory Manager
    memory_manager = MemoryManager()

    # Prepare tools for Gemini if OSC is enabled
    tools = None
    tool_mapping = None
    if vrchat_osc:
        tools = get_tool_definitions()
        tool_mapping = get_tool_mapping(vrchat_osc, memory_manager)

    # Initialize Gemini Live for multimodal AI interaction
    gemini_live = GeminiLive(
        api_key=GEMINI_API_KEY,
        model=MODEL,
        input_sample_rate=AudioManager.SAMPLE_RATE_INPUT,
        system_instruction=SYSTEM_PROMPT,
        voice_name=VOICE_NAME,
        tools=tools,
        tool_mapping=tool_mapping,
    )
    gemini_response_chunks: list[str] = []
    last_displayed_length = 0  # Track how much response we've already paginated and displayed
    is_talking = {"active": False}  # Track if NOVA is currently speaking

    # Start banner resend loop if OSC is enabled
    banner_task = None
    if vrchat_osc:
        banner_task = asyncio.create_task(_banner_resend_loop(vrchat_osc, is_talking))

    log("Starting Gemini Live session", "info")

    try:
        loop = asyncio.get_running_loop()
        input_handler.start(loop)

        # Process Gemini Live events async
        async for event in gemini_live.start_session(
            audio_input_queue=audio_input_queue,
            video_input_queue=video_input_queue,
            text_input_queue=text_input_queue,
            audio_output_callback=audio_manager.write_audio_chunk,
            audio_interrupt_callback=audio_manager.interrupt_output,
        ):
            handle_event(event)

            # Collect Gemini response chunks and display pages as they form
            if vrchat_osc and event.get("type") == "gemini":
                text = event.get("text", "")
                if text:
                    is_talking["active"] = True
                    gemini_response_chunks.append(text)
                    vrchat_osc.clear_banner()

                    # Check if we have enough text to paginate and display new pages
                    full_response = "".join(gemini_response_chunks)
                    if len(full_response) - last_displayed_length > 100:  # Display after every ~100 new chars
                        pages = vrchat_osc.send_chatbox_paginated(full_response)
                        if pages:
                            await vrchat_osc.display_pages(pages)
                            last_displayed_length = len(full_response)
            # Send any remaining response to VRChat chatbox when turn is complete
            elif vrchat_osc and event.get("type") == "turn_complete":
                is_talking["active"] = False
                full_response = "".join(gemini_response_chunks).strip()
                gemini_response_chunks.clear()
                if full_response and len(full_response) > last_displayed_length:
                    pages = vrchat_osc.send_chatbox_paginated(full_response)
                    if pages:
                        await vrchat_osc.display_pages(pages)
                last_displayed_length = 0
    except Exception as e:
        log(f"Session error: {e}", "error")
        import traceback

        traceback.print_exc()
    finally:
        audio_manager.cleanup()
        if banner_task:
            banner_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
