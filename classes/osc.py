import asyncio
import time
import logging
import threading
import queue
from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pynput.keyboard import Key, Controller as KeyboardController

logger = logging.getLogger(__name__)

CHATBOX_CHAR_LIMIT = 144
CHATBOX_RATE_LIMIT = 1.27  # VRChat chatbox rate limit in seconds

# Keyboard controller for VRChat actions
_keyboard = KeyboardController()


class VRChatOSC:
    def __init__(self, config):
        self.config = config
        self.client = udp_client.SimpleUDPClient(config.osc_ip, config.osc_port)
        self._typing = False
        self._last_chatbox_time = 0
        self._chatbox_queue = queue.Queue()
        self._chatbox_thread = threading.Thread(target=self._chatbox_worker, daemon=True)
        self._chatbox_thread.start()

        # Avatar velocity from VRChat OSC output (read by wanderer for stuck detection)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.velocity_z = 0.0
        self.grounded = True
        self.velocity_received = False  # True once any velocity update arrives

        # Start OSC listener for avatar parameters
        self._start_osc_listener(config)

    def _start_osc_listener(self, config):
        """Start background OSC server to receive avatar parameters from VRChat."""
        receive_port = getattr(config, "osc_receive_port", 9001)
        dispatcher = Dispatcher()
        dispatcher.map("/avatar/parameters/VelocityZ", self._on_velocity_z)
        dispatcher.map("/avatar/parameters/VelocityX", self._on_velocity_x)
        dispatcher.map("/avatar/parameters/VelocityY", self._on_velocity_y)
        dispatcher.map("/avatar/parameters/Grounded", self._on_grounded)

        try:
            server = ThreadingOSCUDPServer(("127.0.0.1", receive_port), dispatcher)
            thread = threading.Thread(target=server.serve_forever, daemon=True, name="osc-listener")
            thread.start()
            logger.info(f"OSC listener started on port {receive_port}")
        except OSError as e:
            logger.warning(f"OSC listener failed to start on port {receive_port}: {e}")

    def _on_velocity_z(self, address, value):
        self.velocity_z = float(value)
        self.velocity_received = True

    def _on_velocity_x(self, address, value):
        self.velocity_x = float(value)
        self.velocity_received = True

    def _on_velocity_y(self, address, value):
        self.velocity_y = float(value)

    def _on_grounded(self, address, value):
        self.grounded = bool(value)

    def _chatbox_worker(self):
        """Background thread that sends chatbox messages respecting rate limit."""
        while True:
            try:
                text = self._chatbox_queue.get()
                
                # Rate limit enforcement
                now = time.time()
                elapsed = now - self._last_chatbox_time
                if elapsed < CHATBOX_RATE_LIMIT:
                    time.sleep(CHATBOX_RATE_LIMIT - elapsed)
                
                # Send the message
                self.client.send_message("/chatbox/input", [text, True, False])
                self._last_chatbox_time = time.time()
                
            except Exception as e:
                logger.error(f"Chatbox worker error: {e}")

    def set_typing(self, typing: bool):
        if self._typing != typing:
            self._typing = typing
            self.client.send_message("/chatbox/typing", typing)

    def send_chatbox(self, text: str):
        """Queue a chatbox message (non-blocking, sent by background thread)."""
        # Clear any pending messages and use the latest text
        try:
            while True:
                self._chatbox_queue.get_nowait()
        except queue.Empty:
            pass
        self._chatbox_queue.put(text)

    def send_chatbox_paginated(self, text: str) -> list[str]:
        if len(text) <= CHATBOX_CHAR_LIMIT:
            self.send_chatbox(text)
            return [text]
        pages = self._paginate(text)
        if pages:
            self.send_chatbox(pages[0])
        return pages

    def _paginate(self, text: str) -> list[str]:
        words = text.split()
        if not words:
            return [text[:CHATBOX_CHAR_LIMIT]]

        indicator_reserve = len(" (99/99)")
        usable = CHATBOX_CHAR_LIMIT - indicator_reserve

        chunks = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip() if current else word
            if len(test) > usable:
                if current:
                    chunks.append(current)
                    current = word
                else:
                    chunks.append(word[:usable])
                    current = ""
            else:
                current = test
        if current:
            chunks.append(current)

        total = len(chunks)
        return [f"{c} ({i + 1}/{total})" for i, c in enumerate(chunks)]

    def send_chatbox_direct(self, text: str):
        """Send chatbox message directly via the queue (for paginated display)."""
        self._chatbox_queue.put(text)

    async def display_pages(self, pages: list[str], delay: float = 3.0):
        # Ensure delay is at least the rate limit
        actual_delay = max(delay, CHATBOX_RATE_LIMIT)
        for page in pages:
            self.send_chatbox_direct(page)
            self.set_typing(True)
            await asyncio.sleep(actual_delay)

    def toggle_voice(self):
        self.client.send_message("/input/Voice", 1)
        time.sleep(0.05)
        self.client.send_message("/input/Voice", 0)

    def set_movement(self, forward: float = 0.0, horizontal: float = 0.0):
        """Set movement axes (float -1 to 1). Reset to 0 when done."""
        self.client.send_message("/input/Vertical", max(-1.0, min(1.0, forward)))
        self.client.send_message("/input/LookHorizontal", max(-1.0, min(1.0, horizontal)))

    def stop_movement(self):
        self.client.send_message("/input/Vertical", 0.0)
        self.client.send_message("/input/LookHorizontal", 0.0)
        self.client.send_message("/input/Horizontal", 0.0)

    def toggle_crouch(self):
        """Toggle crouch in VRChat by pressing C key."""
        _keyboard.press('c')
        time.sleep(0.05)
        _keyboard.release('c')
        logger.info("Toggled crouch (C key)")

    def toggle_crawl(self):
        """Toggle crawl/prone in VRChat by pressing Z key."""
        _keyboard.press('z')
        time.sleep(0.05)
        _keyboard.release('z')
        logger.info("Toggled crawl (Z key)")

    # Manual movement methods for AI control
    def start_move(self, direction: str, speed: str = "normal"):
        """Start moving in a direction with speed control.
        
        direction: forward, backward, left (strafe), right (strafe)
        speed: 'slow' (0.5), 'normal' (0.8), 'fast' (1.0), 'sprint' (1.0 + Run)
        """
        speed_map = {"slow": 0.5, "normal": 0.8, "fast": 1.0, "sprint": 1.0}
        axis_val = speed_map.get(speed, 0.8)
        sprinting = speed == "sprint"

        if direction == "forward":
            self.client.send_message("/input/Vertical", axis_val)
        elif direction == "backward":
            self.client.send_message("/input/Vertical", -axis_val)
        elif direction == "left":
            self.client.send_message("/input/Horizontal", -axis_val)
        elif direction == "right":
            self.client.send_message("/input/Horizontal", axis_val)

        self.client.send_message("/input/Run", 1 if sprinting else 0)
        logger.info(f"Started moving {direction} (speed={speed}, axis={axis_val}, sprint={sprinting})")

    def stop_all_movement(self):
        """Reset all movement axes and sprint to zero."""
        self.client.send_message("/input/Vertical", 0.0)
        self.client.send_message("/input/Horizontal", 0.0)
        self.client.send_message("/input/LookHorizontal", 0.0)
        self.client.send_message("/input/Run", 0)
        logger.info("Stopped all movement")

    def jump(self):
        """Make the avatar jump."""
        self.client.send_message("/input/Jump", 1)
        time.sleep(0.05)
        self.client.send_message("/input/Jump", 0)
        logger.info("Jumped")

    def look(self, direction: str, duration: float, speed: str = "normal"):
        """Smooth turn left or right, ramping up/down like the tracker system.
        
        speed: 'slow' (0.3), 'normal' (0.6), 'fast' (1.0) - max axis value
        """
        speed_map = {"slow": 0.6, "normal": 0.8, "fast": 1.0}
        target = speed_map.get(speed, 0.6)
        if direction == "left":
            target = -target

        step_interval = 1.0 / 30  # ~30 updates per second like the tracker
        alpha = 0.4  # EMA smoothing factor (same as tracker default)
        max_rate = 0.12  # Max change per step (same as tracker)
        current = 0.0

        elapsed = 0.0
        # Ramp up and hold
        while elapsed < duration:
            new_val = current * (1 - alpha) + target * alpha
            delta = new_val - current
            if abs(delta) > max_rate:
                new_val = current + max_rate * (1 if delta > 0 else -1)
            current = max(-1.0, min(1.0, new_val))
            self.client.send_message("/input/LookHorizontal", float(current))
            time.sleep(step_interval)
            elapsed += step_interval

        # Ramp down smoothly
        while abs(current) > 0.01:
            new_val = current * (1 - alpha)
            delta = new_val - current
            if abs(delta) > max_rate:
                new_val = current + max_rate * (1 if delta > 0 else -1)
            current = max(-1.0, min(1.0, new_val))
            self.client.send_message("/input/LookHorizontal", float(current))
            time.sleep(step_interval)

        self.client.send_message("/input/LookHorizontal", 0.0)
        logger.info(f"Looked {direction} for {duration}s (speed={speed})")

    def look_vertical(self, direction: str, duration: float, speed: str = "normal"):
        """Smooth look up or down, same EMA ramp as horizontal look."""
        speed_map = {"slow": 0.6, "normal": 0.8, "fast": 1.0}
        target = speed_map.get(speed, 0.6)
        if direction == "down":
            target = -target

        step_interval = 1.0 / 30
        alpha = 0.4
        max_rate = 0.12
        current = 0.0

        elapsed = 0.0
        while elapsed < duration:
            new_val = current * (1 - alpha) + target * alpha
            delta = new_val - current
            if abs(delta) > max_rate:
                new_val = current + max_rate * (1 if delta > 0 else -1)
            current = max(-1.0, min(1.0, new_val))
            self.client.send_message("/input/LookVertical", float(current))
            time.sleep(step_interval)
            elapsed += step_interval

        while abs(current) > 0.01:
            new_val = current * (1 - alpha)
            delta = new_val - current
            if abs(delta) > max_rate:
                new_val = current + max_rate * (1 if delta > 0 else -1)
            current = max(-1.0, min(1.0, new_val))
            self.client.send_message("/input/LookVertical", float(current))
            time.sleep(step_interval)

        self.client.send_message("/input/LookVertical", 0.0)
        logger.info(f"Looked {direction} for {duration}s (speed={speed})")

    def grab(self):
        """Grab and hold the item highlighted in front of you. Stays held until drop() is called."""
        self.client.send_message("/input/GrabRight", 1)
        logger.info("Grabbing item (GrabRight held)")

    def drop(self):
        """Release the item currently held in right hand."""
        self.client.send_message("/input/GrabRight", 0)
        logger.info("Dropped item (GrabRight released)")

    def use(self):
        """Use/interact with the item highlighted in front of you using right hand."""
        self.client.send_message("/input/UseRight", 1)
        time.sleep(0.15)
        self.client.send_message("/input/UseRight", 0)
        logger.info("Used item (UseRight)")