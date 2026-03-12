"""
Idle gaze module for NOVA-AI.

When NOVA is not speaking or typing it uses YOLO-based player detection
to subtly track nearby players by sending small look-turn OSC messages.
This makes the avatar feel alive even during silence.

Ported from Project Gabriel's idle.py and refactored to NOVA's
class-based, constants-driven coding style.
"""

import logging
import threading
import time
from typing import Optional, Tuple

import constants as constant

logger = logging.getLogger(__name__)

# Optional heavy imports – gracefully disabled if unavailable
try:
    import cv2
    import mss
    import numpy as np
    _VISION_DEPS_AVAILABLE = True
except ImportError:
    _VISION_DEPS_AVAILABLE = False
    logger.warning(
        "IdleGazeController: cv2/mss/numpy not available – idle gaze disabled."
    )


class IdleGazeController:
    """
    Runs a background thread that uses YOLO to detect players and gently
    steers the avatar's view towards them when NOVA is idle.

    Requires:
    - VisionManager to be accessible (for player detection)
    - OSC to be initialised (for look-turn messages)
    - cv2, mss, numpy (for screen capture)
    """

    def __init__(self) -> None:
        """
        Initialises the IdleGazeController.
        """
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._running: bool = False

    def start(self) -> bool:
        """
        Starts the idle-gaze background thread.

        Returns:
            bool: True if started (or already running), False if deps missing.
        """
        if not constant.IdleGazeConfig.ENABLED:
            logger.info("IdleGazeController: disabled via config.")
            return False

        if not _VISION_DEPS_AVAILABLE:
            logger.warning("IdleGazeController: vision dependencies missing – not starting.")
            return False

        if self._thread and self._thread.is_alive():
            logger.debug("IdleGazeController: already running.")
            return True

        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._gaze_loop, name="idle-gaze", daemon=True
        )
        self._thread.start()
        logger.info("IdleGazeController: started.")
        return True

    def stop(self) -> None:
        """
        Signals the idle-gaze thread to stop.
        """
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        self._running = False
        logger.info("IdleGazeController: stopped.")

    def is_active(self) -> bool:
        """
        Returns True if the idle-gaze thread is currently running.

        Returns:
            bool: Thread alive status.
        """
        return bool(self._thread and self._thread.is_alive())

    def _is_ai_idle(self) -> bool:
        """
        Returns True when NOVA is not speaking and the chatbox is quiet.

        Uses the OSC client's status dict where available and falls back
        to a conservative True (assume idle) if the client is unavailable.

        Returns:
            bool: True if NOVA appears to be idle.
        """
        try:
            from classes import adapters
            osc = adapters.initialize_osc.__globals__.get("_osc_instance")
            if osc is None:
                return True
        except Exception:
            return True

        cooldown = constant.IdleGazeConfig.COOLDOWN_AFTER_SPEECH
        # If the OSC object exposes a last_speech_end timestamp use it
        last_end = getattr(osc, "_last_speech_end", 0)
        if last_end > 0 and (time.time() - last_end) < cooldown:
            return False

        return True

    def _get_game_window(self) -> Optional[Tuple[int, int, int, int]]:
        """
        Finds the VRChat window position using the configured keywords.

        Returns:
            Optional[Tuple[int, int, int, int]]: (left, top, width, height)
                or None if the window cannot be found.
        """
        try:
            import pygetwindow as gw  # type: ignore
            for keyword in constant.VisionSystem.WINDOW_KEYWORDS:
                windows = gw.getWindowsWithTitle(keyword)
                if windows:
                    w = windows[0]
                    return (w.left, w.top, w.width, w.height)
        except Exception as exc:
            logger.debug(f"IdleGazeController: could not find game window: {exc}")
        return None

    def _detect_players(self, frame) -> list:
        """
        Runs YOLO player detection on a BGR frame if the vision manager
        is available; otherwise returns an empty list.

        Args:
            frame: BGR numpy array from OpenCV.

        Returns:
            list: List of bounding-box dicts or (x1,y1,x2,y2) tuples.
        """
        try:
            from classes.vision_manager import VisionManager
            return VisionManager.detect_players_static(frame)
        except Exception:
            return []

    def _send_turn(self, direction: str) -> None:
        """
        Sends a tiny look-turn via the OSC client.

        Args:
            direction (str): 'left' or 'right'.
        """
        try:
            from classes.movement import get_movement_controller
            import asyncio
            controller = get_movement_controller()
            loop = asyncio.new_event_loop()
            loop.run_until_complete(controller.look_turn(direction, duration=0.05))
            loop.close()
        except Exception as exc:
            logger.debug(f"IdleGazeController: send_turn error: {exc}")

    def _gaze_loop(self) -> None:
        """
        Main idle-gaze loop. Runs until _stop_event is set.
        """
        self._running = True
        logger.info("IdleGazeController: gaze loop started.")

        window = self._get_game_window()
        if not window:
            logger.warning("IdleGazeController: VRChat window not found – gaze loop exiting.")
            self._running = False
            return

        left, top, width, height = window
        deadzone = width * constant.IdleGazeConfig.DEADZONE_FRACTION
        poll = constant.IdleGazeConfig.POLL_INTERVAL

        with mss.mss() as sct:
            while not self._stop_event.is_set():
                if not self._is_ai_idle():
                    time.sleep(0.05)
                    continue

                monitor = {"top": top, "left": left, "width": width, "height": height}
                try:
                    screenshot = sct.grab(monitor)
                except Exception as exc:
                    logger.debug(f"IdleGazeController: grab error: {exc}")
                    time.sleep(0.1)
                    continue

                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                players = self._detect_players(frame)
                if players:
                    player = players[0]
                    if isinstance(player, dict):
                        x1, x2 = player["x1"], player["x2"]
                    else:
                        x1, x2 = player[0], player[2]

                    center_x = (x1 + x2) // 2
                    deviation = center_x - (width // 2)

                    if deviation > deadzone:
                        self._send_turn("right")
                    elif deviation < -deadzone:
                        self._send_turn("left")

                time.sleep(poll)

        self._running = False
        logger.info("IdleGazeController: gaze loop stopped.")

_idle_gaze_controller: Optional[IdleGazeController] = None


def get_idle_gaze_controller() -> IdleGazeController:
    """
    Returns the module-level IdleGazeController singleton.

    Returns:
        IdleGazeController: The shared instance.
    """
    global _idle_gaze_controller
    if _idle_gaze_controller is None:
        _idle_gaze_controller = IdleGazeController()
    return _idle_gaze_controller
