import asyncio
import os
import sys
import time

import classes.config as config
from classes.audio import AudioManager
from classes.gemini_live import GeminiLive
from classes.input_handler import InputHandler
from classes.memory import MemoryManager
from classes.memory_supervisor import MemorySupervisor
from classes.osc import VRChatOSC
from classes.sfx import play_sound_async, wait_for_all
from classes.tool_definitions import get_tool_definitions, get_tool_mapping
from classes.ui import handle_event, log, print_startup_logo

# Force unbuffered output for real-time terminal updates
os.environ["PYTHONUNBUFFERED"] = "1"
sys.stdout = type(sys.stdout)(
    sys.stdout.buffer,  # type: ignore
    encoding=sys.stdout.encoding,
    errors="replace",
    newline=None,
    write_through=True,
)


async def _banner_resend_loop(vrchat_osc: "VRChatOSC", is_talking: dict) -> None:
    """Periodically resend banner every 5 seconds when not talking (VRChat OSC compliance)."""
    banner_text = "-----------------------"
    banner_text += "\nCome talk to me!"
    banner_text += "\n-----------------------"
    banner_text += "\nVRChat AI Assistant"
    banner_text += "\n-----------------------"

    while True:
        try:
            if not is_talking["active"]:
                vrchat_osc.send_message(banner_text)
            await asyncio.sleep(5.0)
        except Exception as e:
            log(f"Banner resend error: {e}", "error")
            await asyncio.sleep(5.0)


async def _run_gemini_session(
    gemini_live,
    audio_manager,
    input_handler,
    vrchat_osc,
    context: dict,
) -> None:
    """Run the Gemini Live event loop and route outputs to VRChat/Audio.

    This helper keeps the main entrypoint small so linting tools flag
    fewer complexity issues.
    """
    gemini_response_chunks: list[str] = []
    last_displayed_length = 0
    is_typing = False

    loop = asyncio.get_running_loop()
    input_handler.start(loop)

    queues = {
        "audio": context.get("audio_input_queue"),
        "video": context.get("video_input_queue"),
        "text": context.get("text_input_queue"),
    }

    async for event in gemini_live.start_session(
        audio_input_queue=queues["audio"],
        video_input_queue=queues["video"],
        text_input_queue=queues["text"],
        audio_output_callback=audio_manager.write_audio_chunk,
        audio_interrupt_callback=audio_manager.interrupt_output,
    ):
        handle_event(event)

        if not vrchat_osc:
            continue

        if event.get("type") == "gemini":
            text = event.get("text", "")
            if not text:
                continue

            context["is_talking"]["active"] = True
            last_displayed_length, is_typing = await _on_gemini_text(
                text,
                gemini_response_chunks,
                last_displayed_length,
                vrchat_osc,
                is_typing,
            )

        elif event.get("type") == "turn_complete":
            await _on_turn_complete(
                gemini_response_chunks,
                vrchat_osc,
                last_displayed_length,
                context,
            )
            last_displayed_length = 0


async def _idle_monitor_loop(
    context: dict,
    vrchat_osc: "VRChatOSC",
    idle_wandering_enabled: bool = True,
    check_interval: float = 1.0,
) -> None:
    """Background task that watches the idle timer and triggers actions at thresholds.

    Calls `vrchat_osc.wander()` once per idle period when the idle time reaches 120 seconds.
    """
    try:
        while True:
            try:
                running = bool(context.get("response_idle_running", False))
                start = context.get("response_idle_start")
                elapsed = 0.0
                if running and start is not None:
                    elapsed = time.monotonic() - start
                    # update the exposed elapsed field for monitors
                    context["response_idle_seconds"] = float(elapsed)
                else:
                    elapsed = float(context.get("response_idle_seconds", 0.0))

                last_trigger = context.get("response_idle_last_trigger")
                trigger_interval = 60.0
                # Trigger repeatedly every `trigger_interval` seconds while idle
                if idle_wandering_enabled and elapsed >= trigger_interval and (
                    last_trigger is None
                    or (elapsed - float(last_trigger)) >= trigger_interval
                ):
                    did_trigger = False
                    try:
                        if vrchat_osc is not None:
                            await vrchat_osc.wander(20.0)
                            did_trigger = True
                        else:
                            pass
                    except Exception:
                        did_trigger = False

                    if did_trigger:
                        # record the elapsed time at which we last triggered
                        context["response_idle_last_trigger"] = float(elapsed)

            except Exception:
                pass

            await asyncio.sleep(check_interval)
    except asyncio.CancelledError:
        return


async def _on_gemini_text(
    text: str,
    gemini_response_chunks: list[str],
    last_displayed_length: int,
    vrchat_osc: "VRChatOSC",
    is_typing: bool,
) -> tuple[int, bool]:
    """Handle incoming text chunks from Gemini and paginate to VRChat."""
    try:
        if not is_typing:
            try:
                vrchat_osc.set_typing_indicator(True)
                is_typing = True
            except Exception:
                pass

        gemini_response_chunks.append(text)
        full_response = "".join(gemini_response_chunks)
        if len(full_response) - last_displayed_length > 100:
            pages = vrchat_osc.send_chatbox_paginated(full_response)
            if pages:
                await vrchat_osc.display_pages(pages)
                last_displayed_length = len(full_response)
    except Exception:
        pass

    return last_displayed_length, is_typing


async def _on_turn_complete(
    gemini_response_chunks: list[str],
    vrchat_osc: "VRChatOSC",
    last_displayed_length: int,
    context: dict,
) -> None:
    """Handle end-of-turn cleanup and final pagination to VRChat."""
    try:
        try:
            vrchat_osc.set_typing_indicator(False)
            context["is_typing"] = False
        except Exception:
            pass

        full_response = "".join(gemini_response_chunks).strip()
        gemini_response_chunks.clear()
        if full_response and len(full_response) > last_displayed_length:
            pages = vrchat_osc.send_chatbox_paginated(full_response)
            if pages:
                await vrchat_osc.display_pages(pages)
    finally:
        # Start the idle timer: record monotonic start time and mark running
        try:
            context["response_idle_start"] = time.monotonic()
            context["response_idle_seconds"] = 0.0
            context["response_idle_running"] = True
            context["response_idle_last_trigger"] = None
        except Exception:
            pass

        context["is_talking"]["active"] = False


def _try_play_startup_sound() -> None:
    """Play the startup SFX if present, swallow errors."""
    try:
        startup_mp3 = os.path.join(
            os.path.dirname(__file__), "sfx", "startup_sound.mp3"
        )
        if os.path.exists(startup_mp3):
            play_sound_async(startup_mp3)
    except Exception:
        log("Startup sound error", "warning")


def _init_resources(cfg: config.Config) -> dict:
    """Initialize optional resources (OSC, memory, tools) and return as a dict.

    Returns a map with keys: `vrchat_osc`, `memory_manager`, `tools`, `tool_mapping`.
    """
    vrchat_osc = (
        VRChatOSC(cfg.get_osc_ip, cfg.get_osc_port) if cfg.get_osc_enabled else None
    )
    memory_manager = MemoryManager()
    # Run supervisor purge on startup only when explicitly enabled in config.
    try:
        purge_on_startup = cfg.get("memory", "purge_on_startup", default=False)
        if isinstance(purge_on_startup, str):
            purge_on_startup = purge_on_startup.strip().lower() in (
                "1",
                "true",
                "yes",
                "on",
            )
        else:
            purge_on_startup = bool(purge_on_startup)

        if purge_on_startup:
            supervisor = MemorySupervisor(memory_manager, logger=log)
            ttl_map = {
                "quick_note": cfg.get("memory", "quick_note_days", default=3),
                "short_term": cfg.get("memory", "short_term_days", default=7),
                "long_term": cfg.get("memory", "long_term_days", default=0),
            }
            result = supervisor.run_once(ttl_days_map=ttl_map)
            if result and result.get("deleted"):
                log(
                    f"MemorySupervisor purged {len(result['deleted'])} memories on startup",
                    "info",
                )
    except Exception as e:
        log(f"MemorySupervisor error: {e}", "error")
    tools = None
    tool_mapping = None
    if vrchat_osc:
        tools = get_tool_definitions()
        tool_mapping = get_tool_mapping(vrchat_osc, memory_manager)
    return {
        "vrchat_osc": vrchat_osc,
        "memory_manager": memory_manager,
        "tools": tools,
        "tool_mapping": tool_mapping,
    }


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
    if not cfg.get_gemini_api_key or not cfg.get_gemini_model:
        log("Missing GEMINI_API_KEY or MODEL in config.yaml", "error")
        return

    # Initialize audio
    audio_manager = AudioManager()
    audio_manager.initialize()

    # Play startup sound (non-blocking) if present in the `sfx/` folder
    _try_play_startup_sound()

    # Create communication queues for different input types
    audio_input_queue = asyncio.Queue()
    text_input_queue = asyncio.Queue()
    video_input_queue = asyncio.Queue()

    # Initialize input handler with video queue for screenshots
    input_handler = InputHandler(
        audio_manager, audio_input_queue, text_input_queue, video_input_queue
    )

    # Initialize optional resources (OSC, memory, tools)
    resources = _init_resources(cfg)
    vrchat_osc = resources["vrchat_osc"]

    # Initialize Gemini Live for multimodal AI interaction
    gemini_live = GeminiLive(
        api_key=cfg.get_gemini_api_key,
        model=cfg.get_gemini_model,
        input_sample_rate=AudioManager.SAMPLE_RATE_INPUT,
        system_instruction=cfg.get_system_prompt,
        voice_name=cfg.get_gemini_voice,
        tools=resources["tools"],
        tool_mapping=resources["tool_mapping"],
    )
    # The heavy event-processing logic is moved to a helper to reduce
    # complexity of `main` for linting and readability.

    # Shared runtime context used by helper functions
    context = {
        "audio_input_queue": audio_input_queue,
        "video_input_queue": video_input_queue,
        "text_input_queue": text_input_queue,
        "is_talking": {"active": False},
        "is_typing": False,
        # Timer: monotonic start timestamp when Nova stops speaking, None otherwise
        "response_idle_start": None,
        # Elapsed seconds since Nova stopped speaking (float)
        "response_idle_seconds": 0.0,
        # Whether the idle timer is currently running
        "response_idle_running": False,
        # Timestamp (seconds elapsed) of the last idle-trigger; None if never
        "response_idle_last_trigger": None,
    }

    # Give the input handler a reference to the shared context so it can
    # stop the idle timer whenever the user begins input (speaking/typing).
    try:
        input_handler.set_context(context)
    except Exception:
        pass

    # Start banner resend loop if OSC is enabled
    banner_task = None
    if vrchat_osc:
        banner_task = asyncio.create_task(
            _banner_resend_loop(vrchat_osc, context["is_talking"])
        )

    # Start background monitor that checks idle time and triggers actions
    idle_monitor_task = asyncio.create_task(
        _idle_monitor_loop(
            context,
            vrchat_osc,
            idle_wandering_enabled=cfg.get_osc_idle_wandering_enabled,
        )
    )

    log("Starting Gemini Live session", "info")

    try:
        await _run_gemini_session(
            gemini_live=gemini_live,
            audio_manager=audio_manager,
            input_handler=input_handler,
            vrchat_osc=vrchat_osc,
            context=context,
        )
    except Exception as e:
        log(f"Session error: {e}", "error")
        # Play error sound if available (non-blocking)
        try:
            error_mp3 = os.path.join(
                os.path.dirname(__file__), "sfx", "error_sound.mp3"
            )
            if os.path.exists(error_mp3):
                play_sound_async(error_mp3)
        except Exception:
            pass
        import traceback

        traceback.print_exc()
    finally:
        audio_manager.cleanup()
        # Wait briefly for any outstanding SFX playback to finish so
        # daemon/thread shutdown races don't trigger interpreter errors.
        try:
            wait_for_all(timeout=3.0)
        except Exception:
            pass
        if banner_task:
            banner_task.cancel()
        if idle_monitor_task:
            idle_monitor_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
