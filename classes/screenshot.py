"""
screenshot.py: Screenshot capture for video input to Gemini Live.

Captures screenshots of the screen or specific windows and converts them
to JPEG format for sending to the Gemini Live video input queue.
"""
import ctypes
import ctypes.wintypes
import io
import mss
from PIL import Image


class ScreenshotManager:
    """Handles screenshot capture for AI video input."""

    def __init__(self, target_window_name="VRChat", quality=80):
        """
        Initialize the screenshot manager.

        Args:
            target_window_name (str): Name of window to capture (e.g. "VRChat").
                                      If None, captures primary monitor.
            quality (int): JPEG quality 1-100. Default 80 (good balance).
        """
        self.target_window_name = target_window_name
        self.quality = quality
        self._window_hwnd = None

    def get_window_handle(self):
        """Get window handle by name (Windows only)."""
        if not self.target_window_name:
            return None

        try:
            # Use Windows API to find window
            hwnd = ctypes.windll.user32.FindWindowW(None, self.target_window_name)
            if hwnd:
                return hwnd

            # Try partial match using EnumWindows
            for hwnd in self._find_windows_by_name(self.target_window_name):
                return hwnd
        except Exception:
            pass

        return None

    @staticmethod
    def _find_windows_by_name(name):
        """Find windows by partial name match (Windows)."""
        windows = []

        def enum_windows(hwnd, _):
            try:
                # Get window title using Windows API
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    window_title = buf.value
                    if name.lower() in window_title.lower():
                        windows.append(hwnd)
            except Exception as e:
                print(f"Error enumerating window {hwnd}: {e}")

            return True

        try:
            ctypes.windll.user32.EnumWindows(
                ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)(enum_windows),
                None
            )
        except Exception as e:
            print(f"Error enumerating windows: {e}")

        return windows

    def get_window_bounds(self, hwnd):
        """Get window boundaries (Windows only)."""
        try:
            rect = ctypes.wintypes.RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            return {
                "left": rect.left,
                "top": rect.top,
                "width": rect.right - rect.left,
                "height": rect.bottom - rect.top,
            }
        except Exception as e:
            print(f"Error getting window bounds for {hwnd}: {e}")
            return None

    def capture_screenshot(self):
        """
        Capture screenshot and return as JPEG bytes.

        Returns:
            bytes: JPEG-encoded screenshot data, or None on failure
        """
        try:
            with mss.mss() as sct:
                # Try to capture specific window if name provided
                if self.target_window_name:
                    hwnd = self.get_window_handle()
                    if hwnd:
                        bounds = self.get_window_bounds(hwnd)
                        if bounds and bounds["width"] > 0 and bounds["height"] > 0:
                            # Capture window region
                            region = {
                                "left": bounds["left"],
                                "top": bounds["top"],
                                "width": bounds["width"],
                                "height": bounds["height"],
                            }
                            screenshot = sct.grab(region)
                            return self._convert_to_jpeg(screenshot, self.quality)

                # Fall back to primary monitor
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                return self._convert_to_jpeg(screenshot, self.quality)

        except Exception as e:
            print(f"Screenshot error: {e}")
            return None

    @staticmethod
    def _convert_to_jpeg(mss_screenshot, quality):
        """Convert mss screenshot to JPEG bytes."""
        try:
            # mss returns PIL-compatible format
            img = Image.frombytes(
                "RGB",
                mss_screenshot.size,
                mss_screenshot.rgb,
            )

            # Convert to JPEG and return bytes
            jpeg_buffer = io.BytesIO()
            img.save(jpeg_buffer, format="JPEG", quality=quality)
            return jpeg_buffer.getvalue()
        except Exception as e:
            print(f"JPEG conversion error: {e}")
            return None
