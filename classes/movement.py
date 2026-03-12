"""
Movement module for NOVA-AI.

Exposes full avatar movement via VRChat OSC inputs including turning,
walking, jumping, crouching, and crawling.

Ported from Project Gabriel's movement.py and refactored to NOVA's
class-based, constants-driven coding style.  All movement parameters are
read from constants.MovementConfig so they can be tuned from one place.
"""

import asyncio
import logging
import random
from typing import Any, Dict, Optional

from pythonosc.udp_client import SimpleUDPClient

import constants as constant

logger = logging.getLogger(__name__)


class MovementController:
    """
    Controls avatar movement via VRChat OSC messages.

    Supports:
    - look_turn / look_behind
    - move_direction (forward / backward / left / right)
    - jump, crouch, crawl
    - stop_all_inputs (safety release)

    Keyboard injection (crouch / crawl) requires pydirectinput to be
    installed.  If it is not available those actions log a warning and
    return a failure dict rather than raising.
    """

    def __init__(self, osc_client: Optional[SimpleUDPClient] = None) -> None:
        """
        Initialises the MovementController.

        Args:
            osc_client: Pre-built pythonosc SimpleUDPClient.  If None the
                        controller will attempt to build one from constants.
        """
        self._client: Optional[SimpleUDPClient] = osc_client
        self._active_tasks: Dict[str, asyncio.Task] = {}
        self._key_injector = None
        self._init_key_injector()

    def _init_key_injector(self) -> None:
        """
        Tries to import pydirectinput for keyboard-based inputs.
        Logs a warning (not an error) if unavailable – crouch/crawl simply
        will not work.
        """
        try:
            import pydirectinput as _pdi
            self._key_injector = _pdi
            pause = float(constant.MovementConfig.KEY_TAP_DURATION)
            try:
                _pdi.PAUSE = pause
            except Exception:
                pass
            logger.info("MovementController: keyboard injector ready via pydirectinput.")
        except Exception as exc:
            logger.warning(
                f"MovementController: pydirectinput not available – "
                f"crouch/crawl disabled. ({exc})"
            )

    def set_osc_client(self, client: SimpleUDPClient) -> None:
        """
        Injects or replaces the OSC client after construction.

        Args:
            client: A pythonosc SimpleUDPClient instance.
        """
        self._client = client

    async def _press_button(self, address: str, duration: float) -> None:
        """
        Presses an OSC button for *duration* seconds then releases it.

        Args:
            address (str): The VRChat OSC input address (e.g. /input/Jump).
            duration (float): How long to hold the button in seconds.
        """
        if not self._client:
            logger.error("MovementController: OSC client not available.")
            return
        try:
            self._client.send_message(address, 1)
            await asyncio.sleep(max(0.0, duration))
        finally:
            try:
                self._client.send_message(address, 0)
            except Exception as exc:
                logger.warning(f"MovementController: failed to release {address}: {exc}")

    async def _set_axis(self, address: str, value: float, duration: float) -> None:
        """
        Sets an OSC axis to *value* for *duration* seconds then resets to 0.

        Args:
            address (str): The VRChat OSC axis address.
            value (float): The axis value to send.
            duration (float): How long to hold the value.
        """
        if not self._client:
            logger.error("MovementController: OSC client not available.")
            return
        try:
            self._client.send_message(address, float(value))
            await asyncio.sleep(max(0.0, duration))
        finally:
            try:
                self._client.send_message(address, 0.0)
            except Exception as exc:
                logger.warning(f"MovementController: failed to reset axis {address}: {exc}")

    def _spawn_unique(self, key: str, coro_factory) -> None:
        """
        Spawns an asyncio task for *key*, cancelling any existing one first.

        Args:
            key (str): Identifier for deduplication.
            coro_factory: Zero-arg callable that returns a coroutine.
        """
        existing = self._active_tasks.get(key)
        if existing and not existing.done():
            existing.cancel()
        task = asyncio.create_task(coro_factory())
        self._active_tasks[key] = task

    async def _press_key(self, key: str, duration: float) -> None:
        """
        Holds a keyboard key for *duration* seconds using pydirectinput.

        Args:
            key (str): Key string (e.g. 'c', 'z').
            duration (float): How long to hold the key.
        """
        if not self._key_injector:
            raise RuntimeError(
                "Keyboard injector not available. Install pydirectinput."
            )
        try:
            self._key_injector.keyDown(key)
            await asyncio.sleep(max(0.0, duration))
        finally:
            try:
                self._key_injector.keyUp(key)
            except Exception as exc:
                logger.warning(f"MovementController: failed to release key '{key}': {exc}")

    async def look_turn(
        self, direction: str, duration: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Turns the avatar's view left or right for a set duration.

        Args:
            direction (str): 'left' or 'right'.
            duration (Optional[float]): Override duration in seconds.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        direction = (direction or "").lower()
        if direction not in {"left", "right"}:
            return {"success": False, "message": "direction must be 'left' or 'right'"}

        use_axis = constant.MovementConfig.USE_AXIS
        default_dur = constant.MovementConfig.TURN_DURATION_DEFAULT
        axis_value = constant.MovementConfig.AXIS_TURN_VALUE
        dur = float(duration if duration is not None else default_dur)

        if use_axis:
            value = -axis_value if direction == "left" else axis_value
            addr = "/input/LookHorizontal"
            self._spawn_unique(addr, lambda: self._set_axis(addr, value, dur))
        else:
            addr = "/input/LookLeft" if direction == "left" else "/input/LookRight"
            self._spawn_unique(addr, lambda: self._press_button(addr, dur))

        return {"success": True, "action": "look_turn", "direction": direction, "duration": dur}

    async def look_behind(
        self,
        min_seconds: Optional[float] = None,
        max_seconds: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Turns the avatar around by a randomised duration within configured bounds.

        Args:
            min_seconds (Optional[float]): Override min duration.
            max_seconds (Optional[float]): Override max duration.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        lb_min = float(min_seconds if min_seconds is not None else constant.MovementConfig.LOOK_BEHIND_MIN)
        lb_max = float(max_seconds if max_seconds is not None else constant.MovementConfig.LOOK_BEHIND_MAX)

        if lb_max < lb_min:
            lb_min, lb_max = lb_max, lb_min

        dur = lb_min if abs(lb_max - lb_min) < 1e-6 else random.uniform(lb_min, lb_max)
        direction = (
            random.choice(["left", "right"])
            if constant.MovementConfig.RANDOMIZE_BACK_TURN
            else "left"
        )
        result = await self.look_turn(direction, dur)
        result.update(
            {
                "action": "look_behind",
                "randomized": lb_min != lb_max,
                "min": lb_min,
                "max": lb_max,
                "duration": dur,
            }
        )
        return result

    async def move_direction(
        self,
        direction: str,
        duration: Optional[float] = None,
        run: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Moves the avatar in a cardinal direction.

        Args:
            direction (str): One of 'forward', 'backward', 'left', 'right'.
            duration (Optional[float]): Override duration in seconds.
            run (Optional[bool]): Whether to hold Run during movement.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        direction = (direction or "").lower()
        if direction not in {"forward", "backward", "left", "right"}:
            return {
                "success": False,
                "message": "direction must be forward|backward|left|right",
            }

        button_map = {
            "forward": "/input/MoveForward",
            "backward": "/input/MoveBackward",
            "left": "/input/MoveLeft",
            "right": "/input/MoveRight",
        }
        addr = button_map[direction]
        dur = float(duration if duration is not None else constant.MovementConfig.MOVE_DURATION_DEFAULT)

        run_enabled = constant.MovementConfig.ALLOW_RUN
        should_run = (run is True) or (run is None and constant.MovementConfig.RUN_BY_DEFAULT)

        if run_enabled and should_run:
            self._spawn_unique("/input/Run", lambda: self._press_button("/input/Run", dur))

        self._spawn_unique(addr, lambda: self._press_button(addr, dur))
        return {
            "success": True,
            "action": "move",
            "direction": direction,
            "duration": dur,
            "run": bool(run_enabled and should_run),
        }

    async def jump(self) -> Dict[str, Any]:
        """
        Triggers a brief jump press.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        self._spawn_unique("/input/Jump", lambda: self._press_button("/input/Jump", 0.05))
        return {"success": True, "action": "jump"}

    async def crouch(self) -> Dict[str, Any]:
        """
        Toggles crouch by tapping the 'C' key.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        tap = constant.MovementConfig.KEY_TAP_DURATION
        try:
            self._spawn_unique("key:c", lambda: self._press_key("c", tap))
            return {"success": True, "action": "crouch", "key": "c", "duration": tap}
        except Exception as exc:
            return {"success": False, "message": f"Crouch failed: {exc}"}

    async def crawl(self) -> Dict[str, Any]:
        """
        Toggles crawl by tapping the 'Z' key.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        tap = constant.MovementConfig.KEY_TAP_DURATION
        try:
            self._spawn_unique("key:z", lambda: self._press_key("z", tap))
            return {"success": True, "action": "crawl", "key": "z", "duration": tap}
        except Exception as exc:
            return {"success": False, "message": f"Crawl failed: {exc}"}

    async def stop_all_inputs(self) -> Dict[str, Any]:
        """
        Cancels all active movement tasks and releases any held keys.

        Returns:
            Dict[str, Any]: Result dict with 'success' key.
        """
        for addr, task in list(self._active_tasks.items()):
            if task and not task.done():
                task.cancel()
            self._active_tasks.pop(addr, None)

        # Best-effort release of keyboard keys
        for key in ("c", "z"):
            try:
                if self._key_injector:
                    self._key_injector.keyUp(key)
            except Exception:
                pass

        return {"success": True, "action": "stop_all_inputs"}

    FUNCTION_DECLARATIONS = [
        {
            "name": "look_behind",
            "description": (
                "Turn the avatar around using a randomised duration. "
                "Direction (left/right) is chosen randomly each call."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "min_seconds": {
                        "type": "number",
                        "description": "Minimum hold duration (omit to use config defaults).",
                    },
                    "max_seconds": {
                        "type": "number",
                        "description": "Maximum hold duration (omit to use config defaults).",
                    },
                },
            },
        },
        {
            "name": "look_turn",
            "description": "Turn the avatar's view left or right for a set duration.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["left", "right"],
                        "description": "Turn direction.",
                    },
                    "duration": {
                        "type": "number",
                        "description": "Seconds to hold the turn.",
                        "default": 1.0,
                    },
                },
                "required": ["direction"],
            },
        },
        {
            "name": "move_direction",
            "description": "Move the avatar in a cardinal direction, optionally holding Run.",
            "parameters": {
                "type": "object",
                "properties": {
                    "direction": {
                        "type": "string",
                        "enum": ["forward", "backward", "left", "right"],
                        "description": "Movement direction.",
                    },
                    "duration": {
                        "type": "number",
                        "description": "How long to move.",
                        "default": 1.0,
                    },
                    "run": {
                        "type": "boolean",
                        "description": "Hold Run while moving.",
                    },
                },
                "required": ["direction"],
            },
        },
        {
            "name": "jump",
            "description": "Trigger a brief jump.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "crouch",
            "description": "Toggle crouch by tapping the 'C' key.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "crawl",
            "description": "Toggle crawl by tapping the 'Z' key.",
            "parameters": {"type": "object", "properties": {}},
        },
        {
            "name": "stop_all_inputs",
            "description": "Release all movement/look inputs to avoid the avatar getting stuck.",
            "parameters": {"type": "object", "properties": {}},
        },
    ]

    async def handle_function_call(self, function_call) -> Any:
        """
        Dispatches a Gemini function-call object to the correct movement action.

        Args:
            function_call: A Gemini types.FunctionCall object with .name and .args.

        Returns:
            A types.FunctionResponse object (imported lazily to keep the module
            usable without the google-genai package installed).
        """
        from google.genai import types

        name = function_call.name
        args = function_call.args or {}

        try:
            if name == "look_behind":
                result = await self.look_behind(args.get("min_seconds"), args.get("max_seconds"))
            elif name == "look_turn":
                result = await self.look_turn(args.get("direction"), args.get("duration"))
            elif name == "move_direction":
                result = await self.move_direction(
                    args.get("direction"), args.get("duration"), args.get("run")
                )
            elif name == "jump":
                result = await self.jump()
            elif name == "crouch":
                result = await self.crouch()
            elif name == "crawl":
                result = await self.crawl()
            elif name == "stop_all_inputs":
                result = await self.stop_all_inputs()
            else:
                result = {"success": False, "message": f"Unknown movement function: {name}"}

            return types.FunctionResponse(id=function_call.id, name=name, response=result)

        except Exception as exc:
            logger.error(f"MovementController: function '{name}' failed: {exc}")
            return types.FunctionResponse(
                id=function_call.id,
                name=name,
                response={"success": False, "message": f"Error executing {name}: {exc}"},
            )

_movement_controller: Optional[MovementController] = None


def get_movement_controller() -> MovementController:
    """
    Returns the module-level MovementController singleton.

    Returns:
        MovementController: The shared instance.
    """
    global _movement_controller
    if _movement_controller is None:
        _movement_controller = MovementController()
    return _movement_controller


def initialize_movement(osc_client: SimpleUDPClient) -> MovementController:
    """
    Initialises (or re-initialises) the module-level MovementController
    with the given OSC client.

    Args:
        osc_client: A pythonosc SimpleUDPClient aimed at VRChat.

    Returns:
        MovementController: The initialised controller.
    """
    global _movement_controller
    _movement_controller = MovementController(osc_client=osc_client)
    logger.info("MovementController initialised.")
    return _movement_controller
