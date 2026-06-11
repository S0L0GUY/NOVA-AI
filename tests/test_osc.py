"""Tests for classes/osc.py: VRChatOSC message formatting (UDP client mocked)."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from classes.osc import VRChatOSC


@pytest.fixture
def osc():
    with patch("classes.osc.udp_client.SimpleUDPClient") as MockClient:
        instance = VRChatOSC("127.0.0.1", 9000)
        instance.client = MagicMock()
        yield instance


def _sent(osc, address):
    return [c for c in osc.client.send_message.call_args_list if c.args[0] == address]


def test_set_typing_indicator(osc):
    osc.set_typing_indicator(True)
    osc.set_typing_indicator(False)
    calls = _sent(osc, "/chatbox/typing")
    assert calls[0].args[1] is True
    assert calls[1].args[1] is False


def test_send_message_formats_payload(osc):
    osc.send_message("hello")
    input_calls = _sent(osc, "/chatbox/input")
    assert input_calls[0].args[1] == ["hello", True]
    # typing turned off after send
    typing_calls = _sent(osc, "/chatbox/typing")
    assert typing_calls[-1].args[1] is False


def test_paginated_splits_long_text(osc):
    text = "word " * 100  # ~500 chars
    pages = osc.send_chatbox_paginated(text, max_chars=50)
    assert len(pages) > 1
    assert all(len(p) <= 50 for p in pages)


def test_paginated_empty_returns_empty_list(osc):
    assert osc.send_chatbox_paginated("") == []
    assert osc.send_chatbox_paginated("   ") == []


def test_paginated_short_text_single_page(osc):
    pages = osc.send_chatbox_paginated("hi there", max_chars=140)
    assert pages == ["hi there"]


def test_toggle_voice_sends_pulse(osc):
    osc.toggle_voice()
    calls = _sent(osc, "/input/Voice")
    assert len(calls) == 2
    assert calls[0].args[1] == 1
    assert calls[1].args[1] == 0


def test_send_osc_passthrough(osc):
    osc.send_osc("/custom/path", 42)
    calls = _sent(osc, "/custom/path")
    assert calls[0].args[1] == 42


def test_jump_async(osc):
    asyncio.run(osc.jump())
    calls = _sent(osc, "/input/Jump")
    assert calls[0].args[1] == 1
    assert calls[1].args[1] == 0


def test_look_left_caps_duration(osc):
    # Should not block longer than the cap (3s); we pass a huge value but expect quick return
    # by mocking sleep.
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.look_left(999))
        # Confirm sleep was called with the cap of 3
        assert mock_sleep.call_args.args[0] == 3


def test_move_forward_caps_at_10(osc):
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.move_forward(999))
        assert mock_sleep.call_args.args[0] == 10


def test_look_right_caps_at_3(osc):
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.look_right(999))
        assert mock_sleep.call_args.args[0] == 3
    calls = _sent(osc, "/input/LookRight")
    assert calls[0].args[1] == 1
    assert calls[1].args[1] == 0


def test_look_left_capped_at_half_second(osc):
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.look_left_capped(999))
        assert mock_sleep.call_args.args[0] == 0.5


def test_look_right_capped_at_half_second(osc):
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.look_right_capped(999))
        assert mock_sleep.call_args.args[0] == 0.5


def test_move_backward_caps(osc):
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.move_backward(999))
        assert mock_sleep.call_args.args[0] == 10
    calls = _sent(osc, "/input/MoveBackward")
    assert calls[0].args[1] == 1
    assert calls[1].args[1] == 0


def test_move_left_right_cap_at_5(osc):
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.move_left(999))
        assert mock_sleep.call_args.args[0] == 5
        asyncio.run(osc.move_right(999))
        assert mock_sleep.call_args.args[0] == 5


def test_display_pages_sends_each(osc):
    pages = ["one", "two", "three"]
    with patch("classes.osc.asyncio.sleep") as mock_sleep:

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.display_pages(pages, delay_seconds=0))
    sent = _sent(osc, "/chatbox/input")
    sent_texts = [c.args[1][0] for c in sent]
    assert sent_texts == pages


def test_wander_runs_and_exits(osc):
    """wander() loops until time elapses; with sleep mocked it exits quickly."""
    # monotonic returns 0 first (end_time = duration), then 0 (loop), then a
    # huge value to terminate the loop. We use an itertools-style generator to
    # provide as many values as the loop asks for.
    times = iter([0.0, 0.0, 0.0, 0.0, 999.0])

    with patch("classes.osc.asyncio.sleep") as mock_sleep, patch(
        "classes.osc.time.monotonic", side_effect=lambda: next(times, 999.0)
    ):

        async def _fake_sleep(_):
            return None

        mock_sleep.side_effect = _fake_sleep
        asyncio.run(osc.wander(1.0))
    # At least one OSC message was sent during wander
    assert osc.client.send_message.call_count > 0
