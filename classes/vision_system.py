from io import BytesIO
from typing import Optional

import win32gui
from PIL import Image, ImageGrab

import constants as constant


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
            print(f"\033[91m[VISION ERROR]\033[0m " f"Error capturing window: {e}")
            return None

    def capture_vrchat_screenshot(self) -> Optional[Image.Image]:
        """Capture a screenshot of the VRChat window."""
        hwnd = self.find_vrchat_window()
        if not hwnd:
            return None

        return self.capture_window(hwnd)

    def image_to_bytes(self, image: Image.Image) -> bytes:
        # Encode PIL Image into JPEG bytes (the API expects a real image file, not raw pixels)
        buf = BytesIO()
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(buf, format="JPEG", quality=85)
        return buf.getvalue()
