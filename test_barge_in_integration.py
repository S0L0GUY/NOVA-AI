"""
Integration test for barge-in functionality.
Tests the core interrupt mechanisms by directly checking the code structure.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_constants_barge_in_settings():
    """Test that barge-in constants are defined."""
    print("Testing barge-in constants...")

    import constants

    assert hasattr(constants.WhisperSettings, "BARGE_IN_ENABLED"), "Should have BARGE_IN_ENABLED"
    assert hasattr(constants.WhisperSettings, "BARGE_IN_THRESHOLD"), "Should have BARGE_IN_THRESHOLD"
    assert hasattr(constants.WhisperSettings, "BARGE_IN_FRAMES"), "Should have BARGE_IN_FRAMES"
    assert hasattr(constants.WhisperSettings, "BARGE_IN_VAD_AGGRESSIVENESS"), "Should have BARGE_IN_VAD_AGGRESSIVENESS"

    # Check types and reasonable values
    assert isinstance(constants.WhisperSettings.BARGE_IN_ENABLED, bool), "BARGE_IN_ENABLED should be bool"
    assert 0 < constants.WhisperSettings.BARGE_IN_THRESHOLD <= 1, "BARGE_IN_THRESHOLD should be 0-1"
    assert constants.WhisperSettings.BARGE_IN_FRAMES > 0, "BARGE_IN_FRAMES should be positive"
    assert 0 <= constants.WhisperSettings.BARGE_IN_VAD_AGGRESSIVENESS <= 3, "VAD aggressiveness should be 0-3"

    print("✓ Barge-in constants test passed")


def test_tts_class_structure():
    """Test that TextToSpeechManager has required interrupt methods."""
    print("Testing TTS class structure...")

    # Read the file and check for required methods and attributes
    with open("classes/edge_tts.py", "r") as f:
        content = f.read()

    # Check for interrupt-related additions
    assert "interrupt_flag" in content, "TTS should have interrupt_flag"
    assert "interrupt_callback" in content, "TTS should have interrupt_callback"
    assert "def interrupt(self)" in content, "TTS should have interrupt() method"
    assert "def reset_interrupt(self)" in content, "TTS should have reset_interrupt() method"
    assert "def set_interrupt_callback(self" in content, "TTS should have set_interrupt_callback() method"
    assert "threading.Event()" in content, "TTS should use threading.Event for interrupt_flag"

    print("✓ TTS class structure test passed")


def test_whisper_class_structure():
    """Test that WhisperTranscriber has required barge-in methods."""
    print("Testing Whisper class structure...")

    # Read the file and check for required methods and attributes
    with open("classes/whisper.py", "r") as f:
        content = f.read()

    # Check for barge-in related additions
    assert "barge_in_active" in content, "Whisper should have barge_in_active"
    assert "barge_in_callback" in content, "Whisper should have barge_in_callback"
    assert "barge_in_vad" in content, "Whisper should have barge_in_vad"
    assert "def start_barge_in_monitoring(self" in content, "Whisper should have start_barge_in_monitoring() method"
    assert "def stop_barge_in_monitoring(self)" in content, "Whisper should have stop_barge_in_monitoring() method"
    assert "def _barge_in_monitor_loop(self)" in content, "Whisper should have _barge_in_monitor_loop() method"

    print("✓ Whisper class structure test passed")


def test_nova_integration():
    """Test that nova.py properly integrates barge-in."""
    print("Testing nova.py integration...")

    # Read the file and check for integration
    with open("nova.py", "r") as f:
        content = f.read()

    # Check that process_completion has transcriber parameter
    assert "transcriber: WhisperTranscriber" in content, "process_completion should accept transcriber"
    assert "was_interrupted" in content, "Should track interruption state"
    assert "start_barge_in_monitoring" in content, "Should start barge-in monitoring"
    assert "stop_barge_in_monitoring" in content, "Should stop barge-in monitoring"
    assert "handle_interrupt" in content, "Should have interrupt handler"

    # Check that run_main_loop passes transcriber to process_completion
    assert (
        "process_completion(completion, osc, tts, transcriber)" in content
    ), "run_main_loop should pass transcriber to process_completion"

    print("✓ nova.py integration test passed")


def test_interrupt_flow():
    """Test that the interrupt flow is properly structured."""
    print("Testing interrupt flow...")

    # Read files
    with open("classes/edge_tts.py", "r") as f:
        tts_content = f.read()
    with open("classes/whisper.py", "r") as f:
        whisper_content = f.read()
    with open("nova.py", "r") as f:
        nova_content = f.read()

    # Check TTS interrupt flow
    assert "self.interrupt_flag.is_set()" in tts_content, "TTS should check interrupt flag"
    assert "sd.stop()" in tts_content, "TTS should stop sounddevice on interrupt"

    # Check Whisper interrupt flow
    assert "self.barge_in_callback()" in whisper_content, "Whisper should call callback on detection"
    assert "self.barge_in_stop_event.is_set()" in whisper_content, "Whisper should check stop event"

    # Check nova.py interrupt flow
    assert "tts.interrupt()" in nova_content, "nova should call tts.interrupt()"
    assert "tts.reset_interrupt()" in nova_content, "nova should reset interrupt flag"

    print("✓ Interrupt flow test passed")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("BARGE-IN INTEGRATION TESTS")
    print("=" * 60)
    print()

    try:
        test_constants_barge_in_settings()
        test_tts_class_structure()
        test_whisper_class_structure()
        test_nova_integration()
        test_interrupt_flow()

        print()
        print("=" * 60)
        print("ALL INTEGRATION TESTS PASSED ✓")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"TEST FAILED: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print(f"UNEXPECTED ERROR: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
