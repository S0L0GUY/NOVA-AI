"""
Test Harness for NOVA-AI Hand Motion System.

This script tests the hand motion subsystem in headless mode without VRChat.
It simulates NOVA responses and logs OSC messages to console.

Usage:
    python test_hands_output.py [--duration 10] [--verbose]
"""

import argparse
import asyncio
import time
import unittest
from typing import Any
from unittest.mock import patch

import numpy as np


class MockOSCClient:
    """Mock OSC client that logs messages instead of sending."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, float]] = []
        self.verbose = False

    def send_message(self, address: str, value: float) -> None:
        """Log an OSC message."""
        self.messages.append((address, value))
        if self.verbose:
            print(f"  OSC: {address} = {value:.4f}")

    def clear(self) -> None:
        """Clear logged messages."""
        self.messages = []


class TestEmotionExtractor(unittest.TestCase):
    """Test cases for EmotionExtractor."""

    def setUp(self) -> None:
        from emotion_extractor import EmotionExtractor
        self.extractor = EmotionExtractor()

    def test_happy_detection(self) -> None:
        """Test happy emotion detection."""
        text = "I'm so happy and excited! This is amazing!"
        emotion = self.extractor.extract(text)

        self.assertEqual(len(emotion), 6)
        self.assertAlmostEqual(np.sum(emotion), 1.0, places=5)
        # Happy should be dominant or significant
        self.assertGreater(emotion[1], 0.2)  # happy index

    def test_sad_detection(self) -> None:
        """Test sad emotion detection."""
        text = "I'm so sorry to hear that... it's really unfortunate."
        emotion = self.extractor.extract(text)

        self.assertEqual(len(emotion), 6)
        self.assertGreater(emotion[2], 0.2)  # sad index

    def test_angry_detection(self) -> None:
        """Test angry emotion detection."""
        text = "I'M SO FRUSTRATED! This is infuriating!"
        emotion = self.extractor.extract(text)

        self.assertEqual(len(emotion), 6)
        self.assertGreater(emotion[3], 0.2)  # angry index

    def test_neutral_detection(self) -> None:
        """Test neutral emotion detection."""
        text = "The weather is nice today."
        emotion = self.extractor.extract(text)

        self.assertEqual(len(emotion), 6)
        # Should default to mostly neutral
        self.assertGreater(emotion[5], 0.5)  # neutral index

    def test_empty_text(self) -> None:
        """Test empty text handling."""
        emotion = self.extractor.extract("")
        self.assertEqual(len(emotion), 6)
        self.assertAlmostEqual(np.sum(emotion), 1.0, places=5)

    def test_emotion_name(self) -> None:
        """Test emotion name extraction."""
        text = "I'm so happy!"
        emotion = self.extractor.extract(text)
        name = self.extractor.get_emotion_name(emotion)
        self.assertIn(name, ["calm", "happy", "sad", "angry", "sarcastic", "neutral"])


class TestCadenceAnalyzer(unittest.TestCase):
    """Test cases for CadenceAnalyzer."""

    def setUp(self) -> None:
        from cadence_analyzer import CadenceAnalyzer
        self.analyzer = CadenceAnalyzer()

    def test_basic_analysis(self) -> None:
        """Test basic text cadence analysis."""
        text = "Hello, how are you doing today?"
        result = self.analyzer.analyze_text(text)

        self.assertIn('speech_rate', result)
        self.assertIn('pause_penalty', result)
        self.assertIn('word_timestamps', result)
        self.assertIn('estimated_duration', result)
        self.assertIn('word_count', result)

        self.assertEqual(result['word_count'], 6)
        self.assertGreater(result['estimated_duration'], 0)

    def test_empty_text(self) -> None:
        """Test empty text handling."""
        result = self.analyzer.analyze_text("")

        self.assertEqual(result['word_count'], 0)
        self.assertEqual(result['estimated_duration'], 0.0)

    def test_punctuation_affects_pauses(self) -> None:
        """Test that punctuation creates pauses."""
        text_no_punct = "Hello how are you"
        text_with_punct = "Hello, how are you?"

        result_no = self.analyzer.analyze_text(text_no_punct)
        result_with = self.analyzer.analyze_text(text_with_punct)

        # Text with punctuation should have more pauses
        self.assertGreaterEqual(result_with['pause_penalty'], result_no['pause_penalty'])

    def test_word_timestamps(self) -> None:
        """Test word timestamp generation."""
        text = "One two three"
        result = self.analyzer.analyze_text(text)

        timestamps = result['word_timestamps']
        self.assertEqual(len(timestamps), 3)

        for ts in timestamps:
            self.assertIn('word', ts)
            self.assertIn('start', ts)
            self.assertIn('end', ts)
            self.assertLessEqual(ts['start'], ts['end'])

    def test_tts_plan_analysis(self) -> None:
        """Test TTS timing plan analysis."""
        tts_timing = {
            'duration': 2.0,
            'word_timestamps': [
                {'word': 'hello', 'start': 0.0, 'end': 0.4},
                {'word': 'world', 'start': 0.5, 'end': 1.0},
            ]
        }
        result = self.analyzer.analyze_tts_plan(tts_timing)

        self.assertEqual(result['word_count'], 2)
        self.assertEqual(result['estimated_duration'], 2.0)


class TestHandMapper(unittest.TestCase):
    """Test cases for HandMapper."""

    def setUp(self) -> None:
        from hand_mapper import HandMapper
        self.config = {
            'smoothing_alpha': 0.6,
            'max_hand_offset': {'x': 0.35, 'y': 0.35, 'z': 0.35},
            'finger_curl_range': [0.0, 1.0],
            'gesture_energy_multiplier': 1.0,
            'osc_parameters': {}
        }
        self.mapper = HandMapper(self.config)

    def test_output_clamping(self) -> None:
        """Test that outputs are clamped to valid ranges."""
        # Create output with extreme values
        extreme_output = np.ones(23, dtype=np.float32) * 10.0

        osc_messages = self.mapper.map_to_osc(extreme_output, apply_smoothing=False)

        for path, value in osc_messages:
            # Position values should be clamped
            if 'Hand' in path and 'Rot' not in path and 'Finger' not in path:
                self.assertLessEqual(abs(value), 1.5)  # With scaling
            # Finger values should be 0-1
            elif 'Finger' in path:
                self.assertGreaterEqual(value, -0.01)  # Allow tiny jitter
                self.assertLessEqual(value, 1.01)

    def test_zero_pose(self) -> None:
        """Test zero pose generation."""
        from hand_mapper import HandMapper
        pose = HandMapper.create_zero_pose()

        self.assertEqual(len(pose), 23)
        # Fingers should be slightly curled
        self.assertGreater(pose[6], 0)  # Left thumb
        self.assertGreater(pose[17], 0)  # Right thumb

    def test_osc_message_count(self) -> None:
        """Test that correct number of OSC messages are generated."""
        output = np.zeros(23, dtype=np.float32)
        osc_messages = self.mapper.map_to_osc(output, apply_smoothing=False)

        # 6 pos + 6 rot + 10 fingers + 1 energy = 23 messages
        self.assertEqual(len(osc_messages), 23)


class TestHandMotionModel(unittest.TestCase):
    """Test cases for HandMotionModel."""

    def test_numpy_model(self) -> None:
        """Test numpy fallback model."""
        from models.hand_motion_model import HandMotionModel

        model = HandMotionModel(use_torch=False)

        # Create input
        input_vec = np.random.randn(34).astype(np.float32)
        output = model.forward(input_vec)

        self.assertEqual(output.shape, (23,))
        # Outputs should be bounded by tanh
        self.assertTrue(np.all(np.abs(output) <= 1.0))

    def test_model_reset(self) -> None:
        """Test model state reset."""
        from models.hand_motion_model import HandMotionModel

        model = HandMotionModel(use_torch=False)

        # Run a few frames
        for _ in range(5):
            model.forward(np.random.randn(34).astype(np.float32))

        # Reset
        model.reset_state()

        # Should be able to run again
        output = model.forward(np.random.randn(34).astype(np.float32))
        self.assertEqual(output.shape, (23,))

    def test_input_creation(self) -> None:
        """Test input vector creation."""
        from models.hand_motion_model import HandMotionModel

        emotion = np.array([0.1, 0.6, 0.1, 0.1, 0.05, 0.05], dtype=np.float32)
        input_vec = HandMotionModel.create_input(
            energy=0.7,
            speech_rate=0.5,
            pause_penalty=0.2,
            emotion_vec=emotion
        )

        self.assertEqual(input_vec.shape, (34,))
        self.assertAlmostEqual(input_vec[0], 0.7)  # energy
        self.assertAlmostEqual(input_vec[1], 0.5)  # speech_rate


async def run_simulation(
    duration: float = 10.0,
    verbose: bool = False
) -> dict[str, Any]:
    """
    Run a simulation of the hands controller.

    Args:
        duration: Simulation duration in seconds.
        verbose: Whether to print verbose output.

    Returns:
        dict: Simulation results and statistics.
    """
    from hands_controller import HandsController

    print(f"\n=== Running Simulation ({duration}s) ===\n")

    # Create mock OSC client
    mock_client = MockOSCClient()
    mock_client.verbose = verbose

    # Create controller
    controller = HandsController()

    # Patch the udp_client creation to return our mock
    with patch('hands_controller.udp_client.SimpleUDPClient', return_value=mock_client):
        # Start controller
        await controller.start()

        # Simulate NOVA responses
        test_responses = [
            {
                'text': "Hello! How are you doing today? I'm so excited to talk with you!",
                'tts_timing': {'duration': 3.0},
                'delay': 0.0
            },
            {
                'text': "I'm sorry to hear that... that's really unfortunate.",
                'tts_timing': {'duration': 2.5},
                'delay': 4.0
            },
            {
                'text': "THAT'S AMAZING! I can't believe it!",
                'tts_timing': {'duration': 2.0},
                'delay': 7.0
            },
        ]

        start_time = time.time()

        for response in test_responses:
            wait_time = response['delay'] - (time.time() - start_time)
            if wait_time > 0:
                await asyncio.sleep(wait_time)

            print(f"\n>>> Triggering response: {response['text'][:50]}...")
            await controller.on_nova_response(
                text=response['text'],
                tts_timing=response.get('tts_timing')
            )
            print(f"    Emotion: {controller.get_current_emotion()}")
            print(f"    Energy: {controller.get_current_energy():.3f}")

        # Wait for remaining duration
        remaining = duration - (time.time() - start_time)
        if remaining > 0:
            await asyncio.sleep(remaining)

        # Stop controller
        await controller.stop()

    # Analyze results
    results = {
        'total_messages': len(mock_client.messages),
        'unique_paths': len(set(path for path, _ in mock_client.messages)),
        'duration': duration,
        'avg_messages_per_second': len(mock_client.messages) / duration
    }

    # Check value ranges
    values = [v for _, v in mock_client.messages]
    results['min_value'] = min(values) if values else 0
    results['max_value'] = max(values) if values else 0
    results['value_range_ok'] = results['min_value'] >= -1.5 and results['max_value'] <= 1.5

    print("\n=== Simulation Results ===")
    print(f"Total OSC messages: {results['total_messages']}")
    print(f"Unique parameter paths: {results['unique_paths']}")
    print(f"Messages per second: {results['avg_messages_per_second']:.1f}")
    print(f"Value range: [{results['min_value']:.3f}, {results['max_value']:.3f}]")
    print(f"Values in range: {results['value_range_ok']}")

    return results


def run_unit_tests() -> bool:
    """
    Run unit tests.

    Returns:
        bool: True if all tests passed.
    """
    print("\n=== Running Unit Tests ===\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestEmotionExtractor))
    suite.addTests(loader.loadTestsFromTestCase(TestCadenceAnalyzer))
    suite.addTests(loader.loadTestsFromTestCase(TestHandMapper))
    suite.addTests(loader.loadTestsFromTestCase(TestHandMotionModel))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


async def test_timing_accuracy(osc_rate: int = 30, duration: float = 5.0) -> dict[str, Any]:
    """
    Test that the update loop maintains timing accuracy.

    Args:
        osc_rate: Target frames per second.
        duration: Test duration in seconds.

    Returns:
        dict: Timing statistics.
    """
    from hands_controller import HandsController

    print(f"\n=== Testing Timing Accuracy ({osc_rate} FPS) ===\n")

    frame_times: list[float] = []
    last_time = time.time()

    mock_client = MockOSCClient()

    # Patch to capture frame times
    original_send = mock_client.send_message

    def capture_timing(*args: Any) -> None:
        nonlocal last_time
        now = time.time()
        frame_times.append(now - last_time)
        last_time = now
        original_send(*args)

    mock_client.send_message = capture_timing

    controller = HandsController()
    controller.osc_rate = osc_rate

    with patch('hands_controller.udp_client.SimpleUDPClient', return_value=mock_client):
        await controller.start()
        await asyncio.sleep(duration)
        await controller.stop()

    if not frame_times:
        return {'error': 'No frames captured'}

    # Calculate statistics
    # Group frame times by ~23 messages per frame
    actual_frame_times = []
    for i in range(0, len(frame_times), 23):
        if i + 22 < len(frame_times):
            actual_frame_times.append(sum(frame_times[i:i + 23]))

    if actual_frame_times:
        expected_frame_time = 1.0 / osc_rate
        avg_frame_time = np.mean(actual_frame_times)
        std_frame_time = np.std(actual_frame_times)
        timing_error = abs(avg_frame_time - expected_frame_time) / expected_frame_time * 100

        results = {
            'target_fps': osc_rate,
            'expected_frame_time': expected_frame_time,
            'avg_frame_time': avg_frame_time,
            'std_frame_time': std_frame_time,
            'timing_error_percent': timing_error,
            'timing_ok': timing_error < 20  # Allow 20% error
        }

        print(f"Target frame time: {expected_frame_time * 1000:.1f}ms")
        print(f"Actual avg frame time: {avg_frame_time * 1000:.1f}ms")
        print(f"Frame time std dev: {std_frame_time * 1000:.1f}ms")
        print(f"Timing error: {timing_error:.1f}%")
        print(f"Timing acceptable: {results['timing_ok']}")

        return results

    return {'error': 'Insufficient data'}


async def main_async(args: argparse.Namespace) -> None:
    """Async main function."""
    all_passed = True

    # Run unit tests
    if run_unit_tests():
        print("\n✓ All unit tests passed")
    else:
        print("\n✗ Some unit tests failed")
        all_passed = False

    # Run simulation
    results = await run_simulation(duration=args.duration, verbose=args.verbose)

    if results.get('value_range_ok'):
        print("\n✓ Value ranges within limits")
    else:
        print("\n✗ Value ranges exceeded limits")
        all_passed = False

    # Test timing accuracy
    timing = await test_timing_accuracy(osc_rate=30, duration=3.0)
    if timing.get('timing_ok'):
        print("\n✓ Timing accuracy acceptable")
    else:
        print("\n✗ Timing accuracy issues detected")
        all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("All tests passed!")
    else:
        print("Some tests failed.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test NOVA-AI Hands System")
    parser.add_argument("--duration", type=float, default=10.0, help="Simulation duration")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
