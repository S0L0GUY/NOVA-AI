"""
gemini_live.py: Google Gemini Live API integration.

Handles bidirectional streaming with Gemini Live for real-time multimodal
interaction including audio, video, and text input/output. Manages the session
lifecycle and event processing for AI responses.
"""

import asyncio
import inspect
import logging
import traceback

from google import genai
from google.genai import types
from google.genai.errors import APIError
from websockets.exceptions import ConnectionClosedOK

from classes.config import DEFAULT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class GeminiLive:
    """
    Manages real-time interaction with the Gemini Live API.

    Establishes a bidirectional streaming session with Gemini Live for:
    - Audio input (transcription and processing)
    - Video/screenshot analysis
    - Text input and turn-based interactions
    - Real-time audio output via callback
    - Optional tool/function calling
    """
    def __init__(
        self,
        api_key,
        model,
        input_sample_rate,
        system_instruction=None,
        voice_name="Puck",
        tools=None,
        tool_mapping=None,
    ):
        """
        Initializes the GeminiLive client.

        Args:
            api_key (str): The Gemini API Key.
            model (str): The model name to use.
            input_sample_rate (int): The sample rate for audio input.
            system_instruction (str, optional): System prompt loaded from YAML.
            voice_name (str, optional): Prebuilt voice to use for native audio.
            tools (list, optional): List of tools to enable. Defaults to None.
            tool_mapping (dict, optional): Mapping of tool names to functions. Defaults to None.
        """
        self.api_key = api_key
        self.model = model
        self.input_sample_rate = input_sample_rate
        self.system_instruction = system_instruction or DEFAULT_SYSTEM_PROMPT
        self.voice_name = voice_name or "Puck"
        self.client = genai.Client(api_key=api_key)
        self.tools = tools or []
        self.tool_mapping = tool_mapping or {}

    async def start_session(self, audio_input_queue, video_input_queue, text_input_queue, audio_output_callback, audio_interrupt_callback=None):
        config = types.LiveConnectConfig(
            response_modalities=[types.Modality.AUDIO],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=self.voice_name
                    )
                )
            ),
            system_instruction=self.system_instruction,
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            tools=self.tools,
        )
        
        logger.info("Connecting to Gemini Live with model=%s", self.model)
        try:
            async with self.client.aio.live.connect(model=self.model, config=config) as session:
                logger.info("Gemini Live session opened successfully")
                
                async def send_audio():
                    try:
                        while True:
                            chunk = await audio_input_queue.get()
                            if chunk is None:
                                logger.info("send_audio: received None chunk, skipping")
                                continue
                            # Normalize memoryview/bytearray to bytes
                            if isinstance(chunk, memoryview):
                                chunk = chunk.tobytes()
                            if isinstance(chunk, bytearray):
                                chunk = bytes(chunk)

                            if not isinstance(chunk, bytes):
                                logger.info(
                                    "send_audio: unsupported chunk type %s, skipping",
                                    type(chunk),
                                )
                                continue

                            try:
                                await session.send_realtime_input(
                                    audio=types.Blob(data=chunk, mime_type=f"audio/pcm;rate={self.input_sample_rate}")
                                )
                            except Exception as e:
                                logger.info(
                                    "send_audio: failed to send chunk (len=%s type=%s): %s",
                                    len(chunk) if hasattr(chunk, '__len__') else 'n/a',
                                    type(chunk),
                                    e,
                                )
                                # Don't raise — drop the chunk and continue streaming
                                continue
                    except asyncio.CancelledError:
                        logger.info("send_audio task cancelled")
                    except ConnectionClosedOK:
                        logger.info("send_audio stopped: Gemini Live connection closed normally")
                    except Exception as e:
                        logger.info("send_audio error: %s\n%s", e, traceback.format_exc())

                async def send_video():
                    try:
                        while True:
                            chunk = await video_input_queue.get()
                            logger.info("Sending video frame to Gemini: %s bytes", len(chunk))
                            if chunk is None:
                                logger.info("send_video: received None chunk, skipping")
                                continue
                            if isinstance(chunk, memoryview):
                                chunk = chunk.tobytes()
                            if isinstance(chunk, bytearray):
                                chunk = bytes(chunk)
                            if not isinstance(chunk, (bytes,)):
                                logger.info(
                                    "send_video: unsupported chunk type %s, skipping",
                                    type(chunk),
                                )
                                continue
                            try:
                                await session.send_realtime_input(
                                    video=types.Blob(data=chunk, mime_type="image/jpeg")
                                )
                            except Exception as e:
                                logger.info(
                                    "send_video: failed to send frame (len=%s): %s",
                                    len(chunk),
                                    e,
                                )
                                continue
                    except asyncio.CancelledError:
                        logger.info("send_video task cancelled")
                    except ConnectionClosedOK:
                        logger.info("send_video stopped: Gemini Live connection closed normally")
                    except Exception as e:
                        logger.info("send_video error: %s\n%s", e, traceback.format_exc())

                async def send_text():
                    try:
                        while True:
                            text = await text_input_queue.get()
                            logger.info("Sending text to Gemini: %s", text)
                            if text is None:
                                continue
                            if not isinstance(text, str):
                                try:
                                    text = str(text)
                                except Exception:
                                    logger.info("send_text: could not coerce text to string, skipping")
                                    continue
                            try:
                                await session.send_realtime_input(text=text)
                            except Exception as e:
                                logger.info("send_text: failed to send text: %s", e)
                                continue
                    except asyncio.CancelledError:
                        logger.info("send_text task cancelled")
                    except ConnectionClosedOK:
                        logger.info("send_text stopped: Gemini Live connection closed normally")
                    except Exception as e:
                        logger.info("send_text error: %s\n%s", e, traceback.format_exc())

                event_queue = asyncio.Queue()

                async def receive_loop():
                    try:
                        while True:
                            async for response in session.receive():
                                logger.info("Received response from Gemini: %s", response)

                                # Log the raw response type for debugging
                                if response.go_away:
                                    logger.info("Received GoAway from Gemini: %s", response.go_away)
                                if response.session_resumption_update:
                                    logger.info("Session resumption update: %s", response.session_resumption_update)
                                
                                server_content = response.server_content
                                tool_call = response.tool_call
                                
                                if server_content:
                                    if server_content.model_turn:
                                        for part in server_content.model_turn.parts:
                                            if part.inline_data:
                                                if inspect.iscoroutinefunction(audio_output_callback):
                                                    await audio_output_callback(part.inline_data.data)
                                                else:
                                                    audio_output_callback(part.inline_data.data)
                                    
                                    if server_content.input_transcription and server_content.input_transcription.text:
                                        await event_queue.put({"type": "user", "text": server_content.input_transcription.text})
                                    
                                    if server_content.output_transcription and server_content.output_transcription.text:
                                        await event_queue.put({"type": "gemini", "text": server_content.output_transcription.text})
                                    
                                    if server_content.turn_complete:
                                        await event_queue.put({"type": "turn_complete"})
                                    
                                    if server_content.interrupted:
                                        if audio_interrupt_callback:
                                            if inspect.iscoroutinefunction(audio_interrupt_callback):
                                                await audio_interrupt_callback()
                                            else:
                                                audio_interrupt_callback()
                                        await event_queue.put({"type": "interrupted"})

                                if tool_call:
                                    function_responses = []
                                    for fc in tool_call.function_calls:
                                        func_name = fc.name
                                        args = fc.args or {}
                                        
                                        if func_name in self.tool_mapping:
                                            try:
                                                tool_func = self.tool_mapping[func_name]
                                                if inspect.iscoroutinefunction(tool_func):
                                                    result = await tool_func(**args)
                                                else:
                                                    loop = asyncio.get_running_loop()
                                                    result = await loop.run_in_executor(None, lambda: tool_func(**args))
                                            except Exception as e:
                                                result = f"Error: {e}"
                                            
                                            function_responses.append(types.FunctionResponse(
                                                name=func_name,
                                                id=fc.id,
                                                response={"result": result}
                                            ))
                                            await event_queue.put({"type": "tool_call", "name": func_name, "args": args, "result": result})
                                    
                                    await session.send_tool_response(function_responses=function_responses)
                            
                            # session.receive() iterator ended (e.g. after turn_complete) — re-enter to keep listening
                            logger.info("Gemini receive iterator completed, re-entering receive loop")

                    except asyncio.CancelledError:
                        logger.info("receive_loop task cancelled")
                    except APIError as e:
                        if getattr(e, "code", None) == 1000:
                            logger.info("receive_loop stopped: Gemini Live connection closed normally (1000)")
                        else:
                            logger.info("receive_loop error: %s: %s\n%s", type(e).__name__, e, traceback.format_exc())
                            await event_queue.put({"type": "error", "error": f"{type(e).__name__}: {e}"})
                    except ConnectionClosedOK:
                        logger.info("receive_loop stopped: Gemini Live connection closed normally")
                    except Exception as e:
                        logger.info("receive_loop error: %s: %s\n%s", type(e).__name__, e, traceback.format_exc())
                        await event_queue.put({"type": "error", "error": f"{type(e).__name__}: {e}"})
                    finally:
                        logger.info("receive_loop exiting")
                        await event_queue.put(None)

                send_audio_task = asyncio.create_task(send_audio())
                send_video_task = asyncio.create_task(send_video())
                send_text_task = asyncio.create_task(send_text())
                receive_task = asyncio.create_task(receive_loop())

                try:
                    while True:
                        event = await event_queue.get()
                        if event is None:
                            break
                        if isinstance(event, dict) and event.get("type") == "error":
                            # Yield the error event, then let the caller decide whether to reconnect.
                            yield event
                            break
                        yield event
                finally:
                    logger.info("Cleaning up Gemini Live session tasks")
                    # Cancel and await tasks to ensure clean shutdown
                    for t in (send_audio_task, send_video_task, send_text_task, receive_task):
                        t.cancel()
                    try:
                        await asyncio.gather(
                            send_audio_task,
                            send_video_task,
                            send_text_task,
                            receive_task,
                            return_exceptions=True,
                        )
                    except Exception:
                        logger.info("Error while awaiting cancelled tasks", exc_info=True)
        except Exception as e:
            logger.info("Gemini Live session error: %s: %s\n%s", type(e).__name__, e, traceback.format_exc())
            raise
        finally:
            logger.info("Gemini Live session closed")