import threading
import time
from typing import List

from together import Together

import constants as constant
from classes.json_wrapper import JsonWrapper
from classes.vision_system import VisionState, VisionSystem


class VisionManager:
    def __init__(self):
        self.vision_state = VisionState()
        self.vision_system = None
        self.vision_thread = None
        self.last_update_check = 0
        self.is_running = False

    def start_vision_system(self):
        """Start the vision system as a background thread."""
        if not constant.VisionSystem.ENABLED:
            print("\033[96m[VISION]\033[0m " "\033[91mVision system is disabled\033[0m")

            return

        try:
            VisionManager.clear_vision_history()

            # Create the Together AI client for the vision system
            client = Together(
                base_url=constant.Vision_API.BASE_URL,
                api_key=constant.Vision_API.API_KEY,
            )

            self.vision_system = VisionSystem(client)
            self.vision_thread = threading.Thread(target=self.vision_system.run_vision_loop, daemon=True)
            self.vision_thread.start()
            self.is_running = True

            print("\033[96m[VISION]\033[0m \033[94mVision system started " "asynchronously\033[0m")

        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m " f"Error starting vision system: {e}")

    def stop_vision_system(self):
        """Stop the vision system thread."""
        if self.vision_system and self.is_running:
            try:
                self.vision_system.stop()
                if self.vision_thread and self.vision_thread.is_alive():
                    self.vision_thread.join(timeout=5)
                self.is_running = False
                print("\033[96m[VISION]\033[0m \033[94mVision system " "stopped\033[0m")
            except Exception as e:
                print(f"\033[91m[VISION ERROR]\033[0m " f"Error stopping vision system: {e}")
            finally:
                self.vision_system = None
                self.vision_thread = None

    def get_new_vision_updates(self) -> List[str]:
        """Get any new vision updates since last check."""
        if not constant.VisionSystem.ENABLED:
            return []

        try:
            updates = self.vision_state.get_new_vision_updates(self.last_update_check)
            self.last_update_check = time.time()
            return updates
        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m " f"Error getting vision updates: {e}")
            return []

    @staticmethod
    def clear_vision_history():
        """Clear vision history and state files at startup."""

        try:
            # Clear vision log (history)
            JsonWrapper.write(constant.VisionSystem.LOG_FILE, [])

            # Reset vision state
            JsonWrapper.write(
                constant.VisionSystem.STATE_FILE,
                {"should_look": False, "last_update": 0},
            )

            print("\033[96m[VISION]\033[0m \033[94mVision history " "cleared\033[0m")

        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m " f"Error clearing vision history: {e}")

    def cleanup(self):
        """Clean up resources."""
        self.stop_vision_system()
