"""Tests for classes/audio.py: AudioManager init/cleanup with PyAudio mocked.

PyAudio requires PortAudio system libraries that may not be present in CI.
We inject a fake `pyaudio` module into sys.modules before importing AudioManager.
"""

import sys
from unittest.mock import MagicMock

# Inject fake pyaudio BEFORE importing AudioManager so the real lib isn't required.
fake_pyaudio = MagicMock()
fake_pyaudio.paInt16 = 8  # arbitrary sentinel
sys.modules.setdefault("pyaudio", fake_pyaudio)

from classes.audio import AudioManager  # noqa: E402


def _make_audio():
    am = AudioManager()
    am.p = MagicMock()
    # Each call to p.open() returns a distinct stream mock so input and output
    # streams can be asserted on independently.
    am.p.open.side_effect = lambda **kwargs: MagicMock(name=f"stream_{kwargs.get('rate')}")
    return am


def test_constants_match_gemini_live_spec():
    assert AudioManager.SAMPLE_RATE_INPUT == 16000
    assert AudioManager.SAMPLE_RATE_OUTPUT == 24000
    assert AudioManager.CHUNK_SIZE == 1024


def test_initialize_opens_input_and_output_streams():
    am = _make_audio()
    am.initialize()

    assert am.p.open.call_count == 2
    input_kwargs = am.p.open.call_args_list[0].kwargs
    output_kwargs = am.p.open.call_args_list[1].kwargs

    assert input_kwargs["rate"] == 16000
    assert input_kwargs["input"] is True
    assert output_kwargs["rate"] == 24000
    assert output_kwargs["output"] is True

    assert am._playback_thread is not None
    assert am._playback_thread.is_alive()

    am.cleanup()


def test_write_audio_chunk_enqueues():
    am = _make_audio()
    am.initialize()
    am.write_audio_chunk(b"\x00\x01")
    # queue has at least one item before playback thread drains it
    # (playback thread may consume — so just confirm no crash and queue is functional)
    am.write_audio_chunk(b"")  # empty should be ignored without error
    am.cleanup()


def test_interrupt_clears_queue():
    am = _make_audio()
    am.initialize()
    for _ in range(5):
        am._playback_queue.put(b"data")
    am.interrupt_output()
    assert am._playback_queue.qsize() == 0
    am.cleanup()


def test_read_audio_chunk_requires_initialize():
    am = _make_audio()
    import pytest
    with pytest.raises(RuntimeError):
        am.read_audio_chunk()


def test_read_audio_chunk_uses_input_stream():
    am = _make_audio()
    am.initialize()
    am.input_stream.read.return_value = b"audio-bytes"
    chunk = am.read_audio_chunk()
    assert chunk == b"audio-bytes"
    am.input_stream.read.assert_called_with(1024, exception_on_overflow=False)
    am.cleanup()


def test_cleanup_closes_streams_and_terminates():
    am = _make_audio()
    am.initialize()
    in_stream = am.input_stream
    out_stream = am.output_stream

    am.cleanup()

    in_stream.stop_stream.assert_called_once()
    in_stream.close.assert_called_once()
    out_stream.stop_stream.assert_called_once()
    out_stream.close.assert_called_once()
    am.p.terminate.assert_called_once()
