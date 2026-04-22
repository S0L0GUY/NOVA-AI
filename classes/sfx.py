"""
sfx.py — simple startup sound playback helper.

Plays an MP3 at startup. On Windows this uses the WinMM MCI API via
`mciSendStringW` so no extra dependency is required. Playback runs in a
background thread so it won't block initialization.
"""
from __future__ import annotations

import ctypes
import logging
import threading
import time
from pathlib import Path
from typing import Optional


def _mci_send(cmd: str) -> Optional[str]:
    buf = ctypes.create_unicode_buffer(1024)
    try:
        ctypes.windll.winmm.mciSendStringW(cmd, buf, ctypes.sizeof(buf), 0)
        return buf.value
    except Exception:
        return None


def _play_mp3_win32(path: str) -> None:
    alias = f"mp3_{int(time.time() * 1000)}"
    abs_path = str(Path(path).resolve())
    # Open, play (wait) and close to ensure resources are freed
    _mci_send(f'open "{abs_path}" type MPEGVideo alias {alias}')
    _mci_send(f'play {alias} wait')
    _mci_send(f'close {alias}')


def _play_via_start(path: str) -> None:
    # Fallback: open with the default app (non-blocking). May show UI.
    try:
        import os

        os.startfile(path)  # type: ignore[attr-defined]
    except Exception:
        pass


def _play(path: str) -> None:
    if not Path(path).exists():
        return
    if ctypes and hasattr(ctypes, "windll") and hasattr(ctypes.windll, "winmm"):
        try:
            _play_mp3_win32(path)
            return
        except Exception:
            pass
    _play_via_start(path)


_PLAYBACK_THREADS: list[threading.Thread] = []


def play_startup_sound_async(path: str) -> None:
    """Play `path` in a background thread (non-blocking).

    On Windows this will block inside the worker thread until playback
    finishes so it does not affect the main process flow.
    """

    def _worker(p: str) -> None:
        try:
            _play(p)
        except Exception as e:
            logging.warning("Failed to play sound %s: %s", p, e)

    thr = threading.Thread(target=_worker, args=(path,), daemon=False)
    thr.start()
    _PLAYBACK_THREADS.append(thr)


def play_sound_async(path: str) -> None:
    """Generic alias to play any sound file asynchronously."""
    play_startup_sound_async(path)


def wait_for_all(timeout: float = 3.0) -> None:
    """Wait for outstanding playback threads to finish (best-effort).

    Joins each playback thread with a per-thread timeout so shutdown
    doesn't hang indefinitely. Safe to call multiple times.
    """
    if not _PLAYBACK_THREADS:
        return
    end = time.time() + timeout
    for thr in list(_PLAYBACK_THREADS):
        remaining = max(0.0, end - time.time())
        try:
            thr.join(remaining)
        except Exception:
            pass
    # Clear finished threads
    _PLAYBACK_THREADS[:] = [t for t in _PLAYBACK_THREADS if t.is_alive()]
