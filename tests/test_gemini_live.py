"""Tests for classes/gemini_live.py: constructor wiring and tool registry.

Mocks `google.genai.Client` so no real API calls are made. If google-genai
or websockets aren't installed, we stub them so the module can be imported.
"""

import sys
import types
from unittest.mock import MagicMock, patch

# Stub google.genai + websockets if they're not installed (e.g. minimal CI env).
if "google" not in sys.modules or not hasattr(sys.modules.get("google"), "genai"):
    google_mod = types.ModuleType("google")
    genai_mod = types.ModuleType("google.genai")
    genai_mod.Client = MagicMock()
    types_submod = types.ModuleType("google.genai.types")

    # Module __getattr__ (PEP 562) returns a MagicMock for any attribute access,
    # so types.FunctionResponse / Blob / LiveConnectConfig / etc. all work.
    def _types_getattr(name):
        return MagicMock(name=f"google.genai.types.{name}")

    types_submod.__getattr__ = _types_getattr
    errors_submod = types.ModuleType("google.genai.errors")
    errors_submod.APIError = type("APIError", (Exception,), {})
    genai_mod.types = types_submod
    genai_mod.errors = errors_submod
    google_mod.genai = genai_mod
    sys.modules["google"] = google_mod
    sys.modules["google.genai"] = genai_mod
    sys.modules["google.genai.types"] = types_submod
    sys.modules["google.genai.errors"] = errors_submod

if "websockets" not in sys.modules:
    ws_mod = types.ModuleType("websockets")
    ws_exc = types.ModuleType("websockets.exceptions")
    ws_exc.ConnectionClosedOK = type("ConnectionClosedOK", (Exception,), {})
    ws_mod.exceptions = ws_exc
    sys.modules["websockets"] = ws_mod
    sys.modules["websockets.exceptions"] = ws_exc

from classes.config import DEFAULT_SYSTEM_PROMPT  # noqa: E402


def _import_gemini_live():
    from classes.gemini_live import GeminiLive

    return GeminiLive


def test_constructor_creates_client_with_api_key():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client") as MockClient:
        gl = GeminiLive(
            api_key="test-key",
            model="gemini-test",
            input_sample_rate=16000,
        )
        MockClient.assert_called_once_with(api_key="test-key")
        assert gl.api_key == "test-key"
        assert gl.model == "gemini-test"
        assert gl.input_sample_rate == 16000


def test_default_system_instruction_when_none():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)
        assert gl.system_instruction == DEFAULT_SYSTEM_PROMPT


def test_custom_system_instruction_used():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(
            api_key="k", model="m", input_sample_rate=16000,
            system_instruction="custom prompt",
        )
        assert gl.system_instruction == "custom prompt"


def test_default_voice_is_puck():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)
        assert gl.voice_name == "Puck"


def test_custom_voice_used():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(
            api_key="k", model="m", input_sample_rate=16000, voice_name="Charon"
        )
        assert gl.voice_name == "Charon"


def test_voice_falls_back_to_puck_when_falsy():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(
            api_key="k", model="m", input_sample_rate=16000, voice_name=""
        )
        assert gl.voice_name == "Puck"


def test_tools_and_mapping_stored():
    GeminiLive = _import_gemini_live()
    fake_tool = MagicMock(__name__="fake_tool")
    mapping = {"fake_tool": lambda: "ok"}
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(
            api_key="k",
            model="m",
            input_sample_rate=16000,
            tools=[fake_tool],
            tool_mapping=mapping,
        )
        assert gl.tools == [fake_tool]
        assert gl.tool_mapping == mapping


def test_empty_tools_default_to_lists():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)
        assert gl.tools == []
        assert gl.tool_mapping == {}


def test_normalize_chunk_handles_types():
    GeminiLive = _import_gemini_live()
    assert GeminiLive._normalize_chunk(b"raw") == b"raw"
    assert GeminiLive._normalize_chunk(bytearray(b"ba")) == b"ba"
    assert GeminiLive._normalize_chunk(memoryview(b"mv")) == b"mv"
    assert GeminiLive._normalize_chunk(None) is None
    assert GeminiLive._normalize_chunk("string") is None


def test_normalize_text_passthrough_and_coerce():
    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)
        assert gl._normalize_text("hello") == "hello"
        assert gl._normalize_text(42) == "42"
        assert gl._normalize_text(None) is None


def test_invoke_callback_sync_and_async():
    import asyncio

    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)

    sync_cb = MagicMock()
    asyncio.run(gl._invoke_callback(sync_cb, "arg1", "arg2"))
    sync_cb.assert_called_once_with("arg1", "arg2")

    called = []

    async def async_cb(*args):
        called.append(args)

    asyncio.run(gl._invoke_callback(async_cb, "x"))
    assert called == [("x",)]


def test_invoke_callback_none_is_noop():
    import asyncio

    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)
    # Should return without error
    asyncio.run(gl._invoke_callback(None, "x"))


def test_handle_tool_call_dispatches_sync_function():
    import asyncio

    GeminiLive = _import_gemini_live()
    fc = MagicMock()
    fc.name = "my_tool"
    fc.args = {"x": 1}
    fc.id = "call-1"

    tool_call = MagicMock()
    tool_call.function_calls = [fc]

    session = MagicMock()
    session.send_tool_response = MagicMock()

    async def run():
        # send_tool_response is async in real code; make it an async mock here
        async def _send(**kwargs):
            session.tool_response_kwargs = kwargs
        session.send_tool_response = _send

        with patch("classes.gemini_live.genai.Client"):
            gl = GeminiLive(
                api_key="k", model="m", input_sample_rate=16000,
                tool_mapping={"my_tool": lambda x: f"got-{x}"},
            )
        q = asyncio.Queue()
        await gl._handle_tool_call(session, tool_call, q)
        event = q.get_nowait()
        assert event["type"] == "tool_call"
        assert event["name"] == "my_tool"
        assert event["result"] == "got-1"
        assert "function_responses" in session.tool_response_kwargs

    asyncio.run(run())


def test_handle_tool_call_dispatches_async_function():
    import asyncio

    GeminiLive = _import_gemini_live()
    fc = MagicMock()
    fc.name = "async_tool"
    fc.args = {"v": 5}
    fc.id = "call-2"
    tool_call = MagicMock()
    tool_call.function_calls = [fc]

    async def async_tool(v):
        return f"async-{v}"

    async def run():
        session = MagicMock()

        async def _send(**kwargs):
            pass
        session.send_tool_response = _send

        with patch("classes.gemini_live.genai.Client"):
            gl = GeminiLive(
                api_key="k", model="m", input_sample_rate=16000,
                tool_mapping={"async_tool": async_tool},
            )
        q = asyncio.Queue()
        await gl._handle_tool_call(session, tool_call, q)
        event = q.get_nowait()
        assert event["result"] == "async-5"

    asyncio.run(run())


def test_handle_tool_call_unknown_skipped():
    import asyncio

    GeminiLive = _import_gemini_live()
    fc = MagicMock()
    fc.name = "missing"
    fc.args = {}
    fc.id = "x"
    tool_call = MagicMock()
    tool_call.function_calls = [fc]

    async def run():
        session = MagicMock()
        sent = []

        async def _send(**kwargs):
            sent.append(kwargs)
        session.send_tool_response = _send

        with patch("classes.gemini_live.genai.Client"):
            gl = GeminiLive(
                api_key="k", model="m", input_sample_rate=16000,
                tool_mapping={"other": lambda: None},
            )
        q = asyncio.Queue()
        await gl._handle_tool_call(session, tool_call, q)
        # No event emitted, send_tool_response called with empty list
        assert q.empty()
        assert sent[0]["function_responses"] == []

    asyncio.run(run())


def test_handle_tool_call_captures_exception_as_error_result():
    import asyncio

    GeminiLive = _import_gemini_live()
    fc = MagicMock()
    fc.name = "bad"
    fc.args = {}
    fc.id = "x"
    tool_call = MagicMock()
    tool_call.function_calls = [fc]

    def bad():
        raise ValueError("boom")

    async def run():
        session = MagicMock()

        async def _send(**kwargs):
            pass
        session.send_tool_response = _send

        with patch("classes.gemini_live.genai.Client"):
            gl = GeminiLive(
                api_key="k", model="m", input_sample_rate=16000,
                tool_mapping={"bad": bad},
            )
        q = asyncio.Queue()
        await gl._handle_tool_call(session, tool_call, q)
        event = q.get_nowait()
        assert "Error" in event["result"]
        assert "boom" in event["result"]

    asyncio.run(run())


def test_handle_receive_error_swallows_code_1000():
    import asyncio

    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)

    class FakeErr(Exception):
        code = 1000

    async def run():
        q = asyncio.Queue()
        await gl._handle_receive_error(q, FakeErr("normal close"))
        assert q.empty()  # no event queued for code 1000

    asyncio.run(run())


def test_handle_receive_error_queues_event_for_other_codes():
    import asyncio

    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)

    async def run():
        q = asyncio.Queue()
        await gl._handle_receive_error(q, RuntimeError("oops"))
        event = q.get_nowait()
        assert event["type"] == "error"
        assert "oops" in event["error"]

    asyncio.run(run())


def test_emit_server_content_emits_transcription_events():
    import asyncio

    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)

    sc = MagicMock()
    sc.model_turn = None
    sc.input_transcription = MagicMock(text="user said")
    sc.output_transcription = MagicMock(text="gemini said")
    sc.turn_complete = True
    sc.interrupted = False

    async def run():
        q = asyncio.Queue()
        await gl._emit_server_content_events(sc, None, None, q)
        events = []
        while not q.empty():
            events.append(q.get_nowait())
        types_seen = {e["type"] for e in events}
        assert "user" in types_seen
        assert "gemini" in types_seen
        assert "turn_complete" in types_seen

    asyncio.run(run())


def test_emit_server_content_interrupted_invokes_callback():
    import asyncio

    GeminiLive = _import_gemini_live()
    with patch("classes.gemini_live.genai.Client"):
        gl = GeminiLive(api_key="k", model="m", input_sample_rate=16000)

    sc = MagicMock()
    sc.model_turn = None
    sc.input_transcription = None
    sc.output_transcription = None
    sc.turn_complete = False
    sc.interrupted = True

    interrupt_cb = MagicMock()

    async def run():
        q = asyncio.Queue()
        await gl._emit_server_content_events(sc, None, interrupt_cb, q)
        event = q.get_nowait()
        assert event["type"] == "interrupted"
        interrupt_cb.assert_called_once()

    asyncio.run(run())
