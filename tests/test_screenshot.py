"""Tests for classes/screenshot.py: ScreenshotManager with mss + PIL mocked.

The real module imports `mss` and `PIL.Image` at module level; we leave those
to the real installs (they're pure Python and available on CI) but mock their
runtime behavior so no actual screen capture occurs.
"""

import sys
import types
from unittest.mock import MagicMock, patch

# Stub mss and PIL if they're not installed in the test env.
if "mss" not in sys.modules:
    mss_mod = types.ModuleType("mss")
    mss_mod.mss = MagicMock()
    sys.modules["mss"] = mss_mod

if "PIL" not in sys.modules:
    pil_mod = types.ModuleType("PIL")
    image_mod = types.ModuleType("PIL.Image")
    image_mod.frombytes = MagicMock()
    pil_mod.Image = image_mod
    sys.modules["PIL"] = pil_mod
    sys.modules["PIL.Image"] = image_mod

from classes.screenshot import ScreenshotManager  # noqa: E402


def test_constructor_defaults():
    sm = ScreenshotManager()
    assert sm.target_window_name == "VRChat"
    assert sm.quality == 80
    assert sm._window_hwnd is None


def test_constructor_custom():
    sm = ScreenshotManager(target_window_name="Foo", quality=50)
    assert sm.target_window_name == "Foo"
    assert sm.quality == 50


def test_get_window_handle_no_target_returns_none():
    sm = ScreenshotManager(target_window_name=None)
    assert sm.get_window_handle() is None


def test_get_window_handle_on_non_windows_returns_none():
    """On macOS/Linux, ctypes.windll doesn't exist — call should swallow and return None."""
    sm = ScreenshotManager(target_window_name="VRChat")
    # On non-Windows platforms ctypes.windll raises AttributeError; the method
    # catches it and returns None.
    result = sm.get_window_handle()
    assert result is None


def test_capture_falls_back_to_primary_monitor():
    sm = ScreenshotManager(target_window_name=None)  # forces monitor path

    fake_screenshot = MagicMock()
    fake_sct = MagicMock()
    fake_sct.monitors = [None, {"left": 0, "top": 0, "width": 100, "height": 100}]
    fake_sct.grab.return_value = fake_screenshot
    fake_ctx = MagicMock()
    fake_ctx.__enter__.return_value = fake_sct
    fake_ctx.__exit__.return_value = False

    with patch("classes.screenshot.mss.mss", return_value=fake_ctx), patch.object(
        ScreenshotManager, "_convert_to_jpeg", return_value=b"jpeg-data"
    ) as conv:
        result = sm.capture_screenshot()

    assert result == b"jpeg-data"
    fake_sct.grab.assert_called_once()
    conv.assert_called_once()


def test_capture_returns_none_on_error():
    sm = ScreenshotManager(target_window_name=None)
    with patch("classes.screenshot.mss.mss", side_effect=RuntimeError("boom")):
        assert sm.capture_screenshot() is None


def test_convert_to_jpeg_returns_bytes():
    fake_screenshot = MagicMock()
    fake_screenshot.size = (10, 10)
    fake_screenshot.rgb = b"\x00" * 300

    fake_img = MagicMock()

    def fake_save(buf, format, quality):
        buf.write(b"FAKEJPEG")

    fake_img.save.side_effect = fake_save

    with patch("classes.screenshot.Image.frombytes", return_value=fake_img):
        result = ScreenshotManager._convert_to_jpeg(fake_screenshot, 80)

    assert result == b"FAKEJPEG"


def test_convert_to_jpeg_returns_none_on_error():
    fake_screenshot = MagicMock()
    fake_screenshot.size = (10, 10)
    fake_screenshot.rgb = b""
    with patch("classes.screenshot.Image.frombytes", side_effect=RuntimeError("bad")):
        assert ScreenshotManager._convert_to_jpeg(fake_screenshot, 80) is None


def test_capture_uses_window_bounds_when_hwnd_found():
    sm = ScreenshotManager(target_window_name="VRChat")

    fake_screenshot = MagicMock()
    fake_sct = MagicMock()
    fake_sct.grab.return_value = fake_screenshot
    fake_ctx = MagicMock()
    fake_ctx.__enter__.return_value = fake_sct
    fake_ctx.__exit__.return_value = False

    bounds = {"left": 10, "top": 20, "width": 800, "height": 600}

    with patch("classes.screenshot.mss.mss", return_value=fake_ctx), patch.object(
        sm, "get_window_handle", return_value=12345
    ), patch.object(sm, "get_window_bounds", return_value=bounds), patch.object(
        ScreenshotManager, "_convert_to_jpeg", return_value=b"win-jpeg"
    ):
        result = sm.capture_screenshot()

    assert result == b"win-jpeg"
    region = fake_sct.grab.call_args.args[0]
    assert region["width"] == 800
    assert region["height"] == 600
