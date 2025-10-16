import time
import json
import os
from typing import Optional, Dict, Any, List
import base64
from io import BytesIO
from PIL import Image, ImageGrab
from together import Together
import win32gui
import constants as constant


class VisionState:
    def __init__(self):
        self.state_file = constant.VisionSystem.STATE_FILE
        self.vision_log_file = constant.VisionSystem.LOG_FILE
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Ensure state and log files exist."""
        os.makedirs("json_files", exist_ok=True)

        if not os.path.exists(self.state_file):
            self.write_state({"should_look": False, "last_update": 0})

        if not os.path.exists(self.vision_log_file):
            with open(self.vision_log_file, 'w') as f:
                json.dump([], f)

    def write_state(self, state: Dict[str, Any]):
        """Write vision state to file."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error writing vision state: {e}")

    def read_state(self) -> Dict[str, Any]:
        """Read vision state from file."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error reading vision state: {e}")
            return {"should_look": False, "last_update": 0}

    def log_vision_update(self, update: str):
        """Log a vision update for the main process to read."""
        try:
            # Read existing log
            with open(self.vision_log_file, 'r') as f:
                log = json.load(f)

            # Add new update with timestamp
            log.append({
                "timestamp": time.time(),
                "update": update
            })

            # Keep only last entries to prevent file from growing too large
            log = log[-constant.VisionSystem.MAX_LOG_ENTRIES:]

            # Write back to file
            with open(self.vision_log_file, 'w') as f:
                json.dump(log, f)

        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error logging vision update: {e}")

    def get_new_vision_updates(self, last_read_time: float) -> List[str]:
        """Get vision updates newer than the specified timestamp."""
        try:
            with open(self.vision_log_file, 'r') as f:
                log = json.load(f)

            new_updates = [
                entry["update"] for entry in log
                if entry["timestamp"] > last_read_time
            ]

            return new_updates

        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error getting vision updates: {e}")

            return []


class VRChatWindowCapture:
    def __init__(self):
        self.window_title_keywords = constant.VisionSystem.WINDOW_KEYWORDS

    def find_vrchat_window(self) -> Optional[int]:
        """Find the VRChat window handle."""
        def enum_windows_proc(hwnd, results):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                for keyword in self.window_title_keywords:
                    if keyword.lower() in window_title.lower():
                        results.append(hwnd)
            return True

        results = []
        win32gui.EnumWindows(enum_windows_proc, results)
        return results[0] if results else None

    def capture_window(self, hwnd: int) -> Optional[Image.Image]:
        """Capture a screenshot of the specified window."""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = rect

            # Take screenshot of the window area
            screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
            return screenshot
        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error capturing window: {e}")
            return None

    def capture_vrchat_screenshot(self) -> Optional[Image.Image]:
        """Capture a screenshot of the VRChat window."""
        hwnd = self.find_vrchat_window()
        if not hwnd:
            return None

        return self.capture_window(hwnd)


class VisionAnalyzer:
    def __init__(self, client):
        self.client = client

    def image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        # Resize image to reduce API costs while maintaining quality
        max_size = constant.VisionSystem.MAX_IMAGE_SIZE
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="JPEG",
                   quality=constant.VisionSystem.IMAGE_QUALITY)
        return base64.b64encode(buffer.getvalue()).decode()

    def analyze_screenshot(self, image: Image.Image) -> str:
        """Analyze a screenshot and return description of what's visible."""
        try:
            base64_image = self.image_to_base64(image)

            # Try vision model first, fallback to text model if needed
            try:
                response = self.client.chat.completions.create(
                    model=constant.VisionSystem.VISION_MODEL,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self._get_vision_prompt()
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,"
                                               f"{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=constant.VisionSystem.MAX_VISION_TOKENS,
                    temperature=constant.VisionSystem.VISION_TEMPERATURE
                )
            except Exception as vision_error:
                print(f"\033[91m[VISION ERROR]\033[0m "
                      f"Vision model not available: {vision_error}")
                # Fallback to simple text-based response
                return "Vision: Looking around the VRChat world"

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error analyzing screenshot: {e}")
            return "Vision system temporarily unavailable"

    def _get_vision_prompt(self) -> str:
        """Get the vision analysis prompt."""
        try:
            with open(constant.VisionSystem.VISION_PROMPT_PATH, 'r',
                      encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error reading vision prompt: {e}")

            # Fallback prompt if file can't be read
            return ("You are Nova's vision system. Look at this VRChat "
                    "screenshot and report what you see concisely.")


class VisionSystem:
    def __init__(self, client):
        self.state = VisionState()
        self.capture = VRChatWindowCapture()
        self.analyzer = VisionAnalyzer(client)
        self.last_analysis_time = 0
        self.analysis_interval = constant.VisionSystem.ANALYSIS_INTERVAL
        self.running = False

    def should_analyze_now(self) -> bool:
        """Check if enough time has passed for a new analysis."""
        current_time = time.time()
        time_diff = current_time - self.last_analysis_time
        return time_diff >= self.analysis_interval

    def perform_vision_analysis(self):
        """Take a screenshot and analyze it."""
        try:
            screenshot = self.capture.capture_vrchat_screenshot()

            if not screenshot:
                self.state.log_vision_update("Vision: VRChat window not found")
                return

            analysis = self.analyzer.analyze_screenshot(screenshot)

            if analysis and analysis.strip():
                print(f"\033[96m[VISION]\033[0m \033[94m{analysis}\033[0m")
                self.state.log_vision_update(f"Vision: {analysis}")

            self.last_analysis_time = time.time()

        except Exception as e:
            print(f"\033[91m[VISION ERROR]\033[0m "
                  f"Error in vision analysis: {e}")
            error_msg = "Vision: Error occurred during analysis"
            self.state.log_vision_update(error_msg)

    def run_vision_loop(self):
        """Main vision system loop - runs continuously and asynchronously."""
        self.running = True
        print("\033[96m[VISION]\033[0m \033[94mStarting continuous vision "
              "monitoring...\033[0m")

        while self.running:
            try:
                # Always perform analysis if enough time has passed
                if self.should_analyze_now():
                    self.perform_vision_analysis()

                time.sleep(2)  # Check every 2 seconds

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\033[91m[VISION ERROR]\033[0m "
                      f"Error in vision loop: {e}")
                time.sleep(5)  # Wait before retrying

    def stop(self):
        """Stop the vision system."""
        self.running = False


def run_vision_subprocess():
    """Entry point for running vision system as a subprocess."""

    client = Together(
        base_url=constant.Vision_API.BASE_URL,
        api_key=constant.Vision_API.API_KEY
    )

    vision_system = VisionSystem(client)
    try:
        vision_system.run_vision_loop()
    except KeyboardInterrupt:
        vision_system.stop()
