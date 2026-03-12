"""
Head tracking module for NOVA AI.
Provides random, natural head movement that stays within defined bounds.
Controlled via OSC messages to VRChat.
"""

import random
import threading
import time

import constants as constant
from classes.osc import VRChatOSC


class HeadTracker:
    """
    Manages head movement for the NOVA avatar in VRChat.

    Features:
    - Random movement within a defined square region
    - Smooth interpolation between positions
    - OSC control via /nova/head/target
    - Configurable timing and bounds
    """

    def __init__(self, osc: VRChatOSC):
        """
        Initialize the head tracker.

        Args:
            osc: VRChatOSC instance for sending OSC messages
        """
        self.osc = osc
        self.running = False
        self.thread = None

        # Head movement configuration
        self.center_x = 0.0
        self.center_y = 0.0
        self.bound_radius = 0.1  # Half-size of the square bounds

        # Timing (milliseconds)
        self.min_interval = 200  # ms between updates
        self.max_interval = 600  # ms between updates
        self.interp_time = 300  # ms for interpolation

        # Movement smoothing
        self.use_step_limit = True
        self.max_step = 0.05  # Maximum step size for smooth movement

        # Current position
        self.current_x = self.center_x
        self.current_y = self.center_y

        # OSC address
        self.osc_address = "/nova/head/target"

    def set_bounds(self, cx: float, cy: float, r: float):
        """
        Set the bounds for head movement.

        Args:
            cx: Center X coordinate
            cy: Center Y coordinate
            r: Half-size of square bounds
        """
        self.center_x = cx
        self.center_y = cy
        self.bound_radius = r

    def set_timing(self, min_ms: int, max_ms: int, interp_ms: int):
        """
        Set timing parameters for head movement.

        Args:
            min_ms: Minimum interval between updates (ms)
            max_ms: Maximum interval between updates (ms)
            interp_ms: Interpolation time for smooth movement (ms)
        """
        self.min_interval = min_ms
        self.max_interval = max_ms
        self.interp_time = interp_ms

    def clamp(self, x: float, y: float) -> tuple:
        """
        Clamp coordinates to bounds.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Tuple of clamped (x, y)
        """
        x = max(self.center_x - self.bound_radius, min(x, self.center_x + self.bound_radius))
        y = max(self.center_y - self.bound_radius, min(y, self.center_y + self.bound_radius))
        return x, y

    def generate_target(self) -> tuple:
        """
        Generate a new target position.

        Returns:
            Tuple of (x, y) target coordinates
        """
        if self.use_step_limit:
            # Smooth movement: small random offset from current position
            new_x = self.current_x + random.uniform(-self.max_step, self.max_step)
            new_y = self.current_y + random.uniform(-self.max_step, self.max_step)
        else:
            # Random position anywhere in bounds
            new_x = random.uniform(self.center_x - self.bound_radius, self.center_x + self.bound_radius)
            new_y = random.uniform(self.center_y - self.bound_radius, self.center_y + self.bound_radius)

        # Clamp to bounds
        new_x, new_y = self.clamp(new_x, new_y)
        return new_x, new_y

    def movement_loop(self):
        """
        Main movement loop. Runs in a background thread.
        """
        print("\033[94m[HeadTracker] Starting head movement loop\033[0m")

        while self.running:
            # Wait random interval
            interval = random.uniform(self.min_interval, self.max_interval)
            time.sleep(interval / 1000.0)

            if not self.running:
                break

            # Generate new target
            new_x, new_y = self.generate_target()

            # Send OSC message
            if self.osc:
                try:
                    self.osc.send_osc(self.osc_address, [new_x, new_y, self.interp_time])
                except Exception as e:
                    print(f"\033[91m[HeadTracker] OSC error: {e}\033[0m")

            # Update current position
            self.current_x, self.current_y = new_x, new_y

        print("\033[94m[HeadTracker] Head movement loop stopped\033[0m")

    def start(self):
        """
        Start the head tracking in a background thread.
        """
        if self.running:
            print("\033[93m[HeadTracker] Already running\033[0m")
            return

        self.running = True
        self.thread = threading.Thread(target=self.movement_loop, daemon=True)
        self.thread.start()
        print("\033[92m[HeadTracker] Started\033[0m")

    def stop(self):
        """
        Stop the head tracking.
        """
        if not self.running:
            return

        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        print("\033[94m[HeadTracker] Stopped\033[0m")

    def is_active(self) -> bool:
        """
        Check if head tracking is active.

        Returns:
            True if running, False otherwise
        """
        return self.running


# Global head tracker instance
_head_tracker = None


def create_head_tracker(osc: VRChatOSC) -> HeadTracker:
    """
    Create and configure the global head tracker.

    Args:
        osc: VRChatOSC instance

    Returns:
        Configured HeadTracker instance
    """
    global _head_tracker
    _head_tracker = HeadTracker(osc=osc)

    # Configure from constants if available
    if hasattr(constant, 'NovaPlacement'):
        if hasattr(constant.NovaPlacement, 'STARTUP_DELAY'):
            pass  # Could use for initial delay

    return _head_tracker


def get_head_tracker() -> HeadTracker:
    """
    Get the global head tracker instance.

    Returns:
        HeadTracker instance or None if not created
    """
    return _head_tracker
