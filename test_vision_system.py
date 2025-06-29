"""
Test script for the Nova AI Vision System.

This script tests the vision system components to ensure they work correctly
before running the full Nova AI system.
"""

import traceback


def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")

    try:
        from classes.vision_system import VisionState, VRChatWindowCapture  # noqa
        from classes.vision_manager import VisionManager  # noqa
        import constants as constant  # noqa
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False


def test_vision_state():
    """Test the vision state management."""
    print("\nTesting vision state...")

    try:
        from classes.vision_system import VisionState

        state = VisionState()

        # Test writing and reading state
        test_state = {"should_look": True, "last_update": 123456}
        state.write_state(test_state)

        read_state = state.read_state()
        if read_state["should_look"]:
            print("✅ Vision state read/write works")
            return True
        else:
            print("❌ Vision state read/write failed")
            return False

    except Exception as e:
        print(f"❌ Vision state error: {e}")
        traceback.print_exc()
        return False


def test_window_capture():
    """Test VRChat window detection and screenshot capture."""
    print("\nTesting window capture...")

    try:
        from classes.vision_system import VRChatWindowCapture
        import win32gui

        capture = VRChatWindowCapture()
        vrchat_window = capture.find_vrchat_window()

        if not vrchat_window:
            print("⚠️ VRChat window not found (expected if not running)")
            return True  # This is expected if VRChat isn't running

        print("✅ VRChat window found")

        # Get window information for validation
        try:
            window_title = win32gui.GetWindowText(vrchat_window)
            window_rect = win32gui.GetWindowRect(vrchat_window)
            left, top, right, bottom = window_rect
            window_width = right - left
            window_height = bottom - top

            print(f"   - Window title: '{window_title}'")
            print(f"   - Window position: ({left}, {top})")
            print(f"   - Window size: {window_width}x{window_height}")

            # Test screenshot capture
            screenshot = capture.capture_vrchat_screenshot()

            if screenshot:
                print("✅ Screenshot captured successfully")
                print(f"   - Screenshot size: "
                      f"{screenshot.width}x{screenshot.height}")

                # Verify screenshot dimensions match window dimensions
                width_match = screenshot.width == window_width
                height_match = screenshot.height == window_height
                if width_match and height_match:
                    print("✅ Screenshot dimensions match window dimensions")
                else:
                    print(f"⚠️ Screenshot dimensions "
                          f"({screenshot.width}x{screenshot.height}) "
                          f"don't exactly match window "
                          f"({window_width}x{window_height})")
                    print("   This might be due to window borders or "
                          "DPI scaling")

                # Save a test screenshot for manual verification
                test_screenshot_path = "test_screenshot.png"
                screenshot.save(test_screenshot_path)
                print(f"✅ Test screenshot saved as '{test_screenshot_path}'")
                print("   Check this file to verify it shows VRChat content, "
                      "not desktop")

                return True
            else:
                print("❌ Failed to capture screenshot")
                return False

        except Exception as e:
            print(f"❌ Error getting window details: {e}")
            return False

    except Exception as e:
        print(f"❌ Window capture error: {e}")
        traceback.print_exc()
        return False


def test_vision_manager():
    """Test the vision manager."""
    print("\nTesting vision manager...")

    try:
        from classes.vision_manager import VisionManager

        manager = VisionManager()

        # Test state changes
        manager.set_listening_state(True)
        manager.set_listening_state(False)

        # Test getting updates (should be empty)
        manager.get_new_vision_updates()

        print("✅ Vision manager basic functions work")
        return True

    except Exception as e:
        print(f"❌ Vision manager error: {e}")
        traceback.print_exc()
        return False


def test_constants():
    """Test that vision constants are properly configured."""
    print("\nTesting constants...")

    try:
        import constants as constant

        # Check if vision constants exist
        if hasattr(constant, 'VisionSystem'):
            print("✅ Vision constants found")
            enabled = constant.VisionSystem.ENABLED
            interval = constant.VisionSystem.ANALYSIS_INTERVAL
            model = constant.VisionSystem.VISION_MODEL
            print(f"   - Enabled: {enabled}")
            print(f"   - Analysis interval: {interval}s")
            print(f"   - Vision model: {model}")
            return True
        else:
            print("❌ Vision constants not found")
            return False

    except Exception as e:
        print(f"❌ Constants error: {e}")
        traceback.print_exc()
        return False


def test_vision_analysis():
    """Test the complete vision analysis pipeline."""
    print("\nTesting vision analysis...")

    try:
        from classes.vision_system import VRChatWindowCapture, VisionAnalyzer
        import win32gui

        capture = VRChatWindowCapture()
        analyzer = VisionAnalyzer()

        # Find VRChat window
        vrchat_window = capture.find_vrchat_window()

        if not vrchat_window:
            print("⚠️ VRChat window not found - skipping vision analysis test")
            return True

        # Capture screenshot
        screenshot = capture.capture_vrchat_screenshot()

        if not screenshot:
            print("❌ Failed to capture screenshot for analysis")
            return False

        print("✅ Screenshot captured for analysis")

        # Verify we're capturing the right window by checking window state
        try:
            # Check if window is minimized or obscured
            window_placement = win32gui.GetWindowPlacement(vrchat_window)
            show_state = window_placement[1]

            if show_state == 2:  # SW_SHOWMINIMIZED
                print("⚠️ VRChat window is minimized - screenshot may not "
                      "show actual content")
            elif show_state == 1:  # SW_SHOWNORMAL or SW_SHOWMAXIMIZED
                print("✅ VRChat window is visible and active")

            # Check if window is foreground window
            foreground_window = win32gui.GetForegroundWindow()
            if foreground_window == vrchat_window:
                print("✅ VRChat window is in foreground")
            else:
                foreground_title = win32gui.GetWindowText(foreground_window)
                print(f"⚠️ VRChat window is not in foreground "
                      f"(foreground: '{foreground_title}')")
                print("   Screenshot may show content behind other windows")

        except Exception as e:
            print(f"⚠️ Could not check window state: {e}")

        # Test vision analysis
        try:
            analysis_result = analyzer.analyze_screenshot(screenshot)

            if analysis_result and analysis_result.strip():
                print("✅ Vision analysis completed")
                print(f"   - Analysis result: {analysis_result[:100]}...")

                # Check if the analysis indicates it's actually VRChat content
                vrchat_indicators = [
                    "vrchat", "avatar", "world", "player", "virtual",
                    "3d", "game", "social", "menu"
                ]

                analysis_lower = analysis_result.lower()
                found_indicators = [
                    indicator for indicator in vrchat_indicators
                    if indicator in analysis_lower
                ]

                if found_indicators:
                    print(f"✅ Analysis suggests VRChat content detected: "
                          f"{', '.join(found_indicators)}")
                else:
                    print("⚠️ Analysis doesn't clearly indicate VRChat "
                          "content")
                    print("   This could mean the window shows something "
                          "else or vision model needs adjustment")

                return True
            else:
                print("❌ Vision analysis returned empty result")
                return False

        except Exception as e:
            print(f"❌ Vision analysis failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Vision analysis test error: {e}")
        traceback.print_exc()
        return False


def test_window_focus_and_capture():
    """Test capturing screenshots with different window states."""
    print("\nTesting window focus and capture scenarios...")

    try:
        from classes.vision_system import VRChatWindowCapture
        import win32gui
        import time

        capture = VRChatWindowCapture()
        vrchat_window = capture.find_vrchat_window()

        if not vrchat_window:
            print("⚠️ VRChat window not found - skipping focus tests")
            return True

        print("✅ VRChat window found for focus testing")

        # Test 1: Capture current state
        screenshot1 = capture.capture_vrchat_screenshot()
        if screenshot1:
            screenshot1.save("test_screenshot_current_state.png")
            print("✅ Captured screenshot in current window state")

        # Test 2: Try to bring window to front and capture again
        try:
            # Check if we can bring the window to front
            current_foreground = win32gui.GetForegroundWindow()

            if current_foreground != vrchat_window:
                print("   Attempting to bring VRChat window to foreground...")
                win32gui.SetForegroundWindow(vrchat_window)
                time.sleep(1)  # Give time for window to come to front

                # Capture after bringing to front
                screenshot2 = capture.capture_vrchat_screenshot()
                if screenshot2:
                    screenshot2.save("test_screenshot_foreground.png")
                    print("✅ Captured screenshot after bringing to "
                          "foreground")

                    # Compare if screenshots are different
                    if screenshot1 and screenshot2:
                        # Simple comparison - check if they have same size
                        # and basic characteristics
                        size_same = (screenshot1.size == screenshot2.size)
                        if size_same:
                            print("✅ Screenshots have consistent dimensions")
                        else:
                            print("⚠️ Screenshot dimensions changed between "
                                  "captures")
            else:
                print("✅ VRChat window was already in foreground")

        except Exception as e:
            print(f"⚠️ Could not test window focus changes: {e}")

        print("✅ Window focus and capture test completed")
        print("   Check saved screenshots to verify they show VRChat "
              "content")
        return True

    except Exception as e:
        print(f"❌ Window focus test error: {e}")
        traceback.print_exc()
        return False


def test_window_validation():
    """Test to validate that window capture is working correctly."""
    print("\nTesting window capture validation...")

    try:
        from classes.vision_system import VRChatWindowCapture
        import win32gui
        import win32con

        capture = VRChatWindowCapture()
        vrchat_window = capture.find_vrchat_window()

        if not vrchat_window:
            print("⚠️ VRChat window not found - skipping validation")
            return True

        # Comprehensive window validation
        try:
            # Get window title and verify it matches VRChat
            window_title = win32gui.GetWindowText(vrchat_window)
            print(f"✅ Found window: '{window_title}'")

            # Check if window is actually VRChat
            vrchat_keywords = ["vrchat", "VRChat"]
            is_vrchat = any(keyword in window_title
                            for keyword in vrchat_keywords)

            if is_vrchat:
                print("✅ Window title confirms it's VRChat")
            else:
                print(f"⚠️ Window title '{window_title}' doesn't clearly "
                      "indicate VRChat")

            # Check window visibility
            is_visible = win32gui.IsWindowVisible(vrchat_window)
            if is_visible:
                print("✅ Window is visible")
            else:
                print("❌ Window is not visible")
                return False

            # Check window state
            window_placement = win32gui.GetWindowPlacement(vrchat_window)
            show_state = window_placement[1]

            state_descriptions = {
                1: "normal",
                2: "minimized",
                3: "maximized"
            }

            state_desc = state_descriptions.get(
                show_state, f"unknown({show_state})")
            print(f"✅ Window state: {state_desc}")

            if show_state == 2:  # minimized
                print("⚠️ Window is minimized - screenshots may not capture "
                      "actual content")

            # Get window rectangle and validate it's reasonable
            rect = win32gui.GetWindowRect(vrchat_window)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top

            print(f"✅ Window rectangle: ({left}, {top}, {right}, {bottom})")
            print(f"✅ Window dimensions: {width}x{height}")

            # Check if window has reasonable size
            if width < 100 or height < 100:
                print("⚠️ Window is very small - may not be actual "
                      "game window")
            elif width > 5000 or height > 5000:
                print("⚠️ Window is very large - coordinates may be "
                      "incorrect")
            else:
                print("✅ Window size appears reasonable")

            # Check if window is on screen
            screen_width = win32gui.GetSystemMetrics(win32con.SM_CXSCREEN)
            screen_height = win32gui.GetSystemMetrics(win32con.SM_CYSCREEN)

            off_screen = (left < -width or top < -height or
                          left > screen_width or top > screen_height)
            if off_screen:
                print("⚠️ Window appears to be off-screen")
            else:
                print("✅ Window is positioned on screen")

            # Test actual screenshot capture and verify it's not empty
            screenshot = capture.capture_window(vrchat_window)

            if screenshot:
                # Basic validation that we got actual image data
                if screenshot.width > 0 and screenshot.height > 0:
                    print(f"✅ Screenshot captured: "
                          f"{screenshot.width}x{screenshot.height}")

                    # Save for manual inspection
                    screenshot.save("validation_screenshot.png")
                    print("✅ Validation screenshot saved as "
                          "'validation_screenshot.png'")

                    # Basic check - if image is completely black,
                    # it might indicate an issue
                    # Convert to grayscale and check average brightness
                    grayscale = screenshot.convert('L')
                    import statistics
                    pixels = list(grayscale.getdata())
                    avg_brightness = statistics.mean(pixels)

                    print(f"✅ Average image brightness: "
                          f"{avg_brightness:.1f}/255")

                    if avg_brightness < 5:
                        print("⚠️ Screenshot appears to be mostly black - "
                              "window may be obscured or minimized")
                    elif avg_brightness > 250:
                        print("⚠️ Screenshot appears to be mostly white - "
                              "possible capture issue")
                    else:
                        print("✅ Screenshot brightness looks normal")

                    return True
                else:
                    print("❌ Screenshot has invalid dimensions")
                    return False
            else:
                print("❌ Failed to capture screenshot")
                return False

        except Exception as e:
            print(f"❌ Window validation error: {e}")
            return False

    except Exception as e:
        print(f"❌ Window validation test error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🔍 Testing Nova AI Vision System Components\n")
    print("=" * 50)

    tests = [
        test_imports,
        test_constants,
        test_vision_state,
        test_window_capture,
        test_vision_manager,
        test_vision_analysis,
        test_window_focus_and_capture,
        test_window_validation,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Vision system should work correctly.")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

    print("\nNote: The vision system requires:")
    print("- VRChat to be running for window capture")
    print("- VRChat window to be visible (not minimized) for best results")
    print("- A vision-capable AI model for screenshot analysis")
    print("- Proper OpenAI API configuration")
    print("\nIf VRChat is running, check the saved test screenshots:")
    print("- test_screenshot.png - Basic window capture")
    print("- test_screenshot_current_state.png - Current window state")
    print("- test_screenshot_foreground.png - After bringing to foreground")
    print("- validation_screenshot.png - Validation capture")
    print("These files should show VRChat content, not desktop/other apps")


if __name__ == "__main__":
    main()
