"""
Head Movement Controller for VRChat avatars.

This module provides random, natural head movement controlled via OSC messages.
The head target is constrained to a defined square region and uses smooth
interpolation for natural-looking motion.

Coordinate system: Normalized range [-1..1] for both x and y axes.
OSC format: Sends to /avatar/parameters/HeadX and /avatar/parameters/HeadY
            with float values in the normalized range.
"""

import logging
import random
import threading
import time
from typing import Optional

from pythonosc import udp_client

import constants as constant


class HeadMovementController:
    """
    Controls random head movement within a defined square region via OSC.

    The controller generates random head targets within square bounds defined
    by center (cx, cy) and half-size r. Targets satisfy:
        cx - r <= x <= cx + r
        cy - r <= y <= cy + r

    Movement can be configured to use either:
    - Step-limited mode: Small random offsets from current position for smooth motion
    - Random mode: Any position within the square bounds

    OSC messages are sent at configurable intervals with interpolation time
    for smooth client-side movement.
    """

    def __init__(
        self,
        osc_client: udp_client.SimpleUDPClient,
        center_x: float = constant.HeadMovement.CENTER_X,
        center_y: float = constant.HeadMovement.CENTER_Y,
        half_size: float = constant.HeadMovement.HALF_SIZE,
        t_min_ms: int = constant.HeadMovement.T_MIN_MS,
        t_max_ms: int = constant.HeadMovement.T_MAX_MS,
        interp_time_ms: int = constant.HeadMovement.INTERP_TIME_MS,
        use_step_limit: bool = constant.HeadMovement.USE_STEP_LIMIT,
        max_step: float = constant.HeadMovement.MAX_STEP,
        osc_address_x: str = constant.HeadMovement.OSC_ADDRESS,
        osc_address_y: str = constant.HeadMovement.OSC_ADDRESS_Y,
        random_seed: Optional[int] = constant.HeadMovement.RANDOM_SEED,
    ):
        """
        Initialize the HeadMovementController.

        Args:
            osc_client: The OSC client for sending messages.
            center_x: X coordinate of the square bounds center.
            center_y: Y coordinate of the square bounds center.
            half_size: Half-size of the square bounds (r).
            t_min_ms: Minimum time between updates in milliseconds.
            t_max_ms: Maximum time between updates in milliseconds.
            interp_time_ms: Interpolation time for smooth movement in ms.
            use_step_limit: If True, uses step-limited movement.
            max_step: Maximum step size per update (if use_step_limit is True).
            osc_address_x: OSC address for X coordinate messages.
            osc_address_y: OSC address for Y coordinate messages.
            random_seed: Optional fixed seed for deterministic movement.
        """
        self.osc_client = osc_client
        self.center_x = center_x
        self.center_y = center_y
        self.half_size = half_size
        self.t_min_ms = t_min_ms
        self.t_max_ms = t_max_ms
        self.interp_time_ms = interp_time_ms
        self.use_step_limit = use_step_limit
        self.max_step = max_step
        self.osc_address_x = osc_address_x
        self.osc_address_y = osc_address_y

        # Initialize random generator with optional seed
        self._rng = random.Random(random_seed)

        # Current head position (starts at center)
        self.current_x = center_x
        self.current_y = center_y

        # Threading control
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def clamp(self, value: float, min_val: float, max_val: float) -> float:
        """
        Clamp a value to the specified range.

        Args:
            value: The value to clamp.
            min_val: Minimum allowed value.
            max_val: Maximum allowed value.

        Returns:
            The clamped value.
        """
        return max(min_val, min(value, max_val))

    def clamp_to_bounds(self, x: float, y: float) -> tuple[float, float]:
        """
        Clamp coordinates to the square bounds.

        Args:
            x: X coordinate to clamp.
            y: Y coordinate to clamp.

        Returns:
            Tuple of (clamped_x, clamped_y).
        """
        min_x = self.center_x - self.half_size
        max_x = self.center_x + self.half_size
        min_y = self.center_y - self.half_size
        max_y = self.center_y + self.half_size

        return (self.clamp(x, min_x, max_x), self.clamp(y, min_y, max_y))

    def generate_random_target(self) -> tuple[float, float]:
        """
        Generate a new random target position.

        If use_step_limit is True, generates a small random offset from the
        current position. Otherwise, generates a random position anywhere
        within the square bounds.

        Returns:
            Tuple of (new_x, new_y) clamped to bounds.
        """
        if self.use_step_limit:
            # Step-limited movement: small random offset from current position
            offset_x = self._rng.uniform(-self.max_step, self.max_step)
            offset_y = self._rng.uniform(-self.max_step, self.max_step)
            new_x = self.current_x + offset_x
            new_y = self.current_y + offset_y
        else:
            # Random position anywhere in the square
            new_x = self._rng.uniform(
                self.center_x - self.half_size,
                self.center_x + self.half_size
            )
            new_y = self._rng.uniform(
                self.center_y - self.half_size,
                self.center_y + self.half_size
            )

        # Clamp to bounds to guarantee the head never travels outside
        return self.clamp_to_bounds(new_x, new_y)

    def get_random_interval(self) -> float:
        """
        Get a random interval between updates.

        Returns:
            Random interval in seconds.
        """
        return self._rng.uniform(self.t_min_ms, self.t_max_ms) / 1000.0

    def send_head_target(self, x: float, y: float) -> None:
        """
        Send head target position via OSC.

        Sends OSC messages to the configured addresses with the target
        coordinates. VRChat avatar parameters typically expect float values.

        Args:
            x: Target X coordinate.
            y: Target Y coordinate.
        """
        try:
            self.osc_client.send_message(self.osc_address_x, float(x))
            self.osc_client.send_message(self.osc_address_y, float(y))
        except Exception as e:
            logging.error(f"Failed to send head target OSC message: {e}")

    def update(self) -> tuple[float, float]:
        """
        Perform a single head movement update.

        Generates a new random target, updates the current position,
        and sends the OSC message.

        Returns:
            Tuple of (new_x, new_y) - the new head target position.
        """
        with self._lock:
            new_x, new_y = self.generate_random_target()
            self.current_x = new_x
            self.current_y = new_y

        self.send_head_target(new_x, new_y)
        return (new_x, new_y)

    def _run_loop(self) -> None:
        """
        Internal loop that continuously updates head position.

        Runs in a separate thread and generates new targets at random
        intervals until stopped.
        """
        while self._running:
            self.update()
            interval = self.get_random_interval()
            time.sleep(interval)

    def start(self) -> None:
        """
        Start the head movement controller.

        Begins generating and sending random head movements in a
        background thread.
        """
        if self._running:
            logging.warning("HeadMovementController is already running.")
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logging.info("HeadMovementController started.")

    def stop(self) -> None:
        """
        Stop the head movement controller.

        Stops the background thread and waits for it to finish.
        """
        if not self._running:
            return

        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        logging.info("HeadMovementController stopped.")

    def is_running(self) -> bool:
        """
        Check if the controller is currently running.

        Returns:
            True if the controller is running, False otherwise.
        """
        return self._running

    def get_current_position(self) -> tuple[float, float]:
        """
        Get the current head position.

        Returns:
            Tuple of (current_x, current_y).
        """
        with self._lock:
            return (self.current_x, self.current_y)

    def set_position(self, x: float, y: float) -> None:
        """
        Manually set the current head position.

        The position is clamped to the square bounds.

        Args:
            x: New X coordinate.
            y: New Y coordinate.
        """
        clamped_x, clamped_y = self.clamp_to_bounds(x, y)
        with self._lock:
            self.current_x = clamped_x
            self.current_y = clamped_y
        self.send_head_target(clamped_x, clamped_y)
