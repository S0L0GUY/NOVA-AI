"""
Unit tests for HeadMovementController.

Tests cover the core functionality of random head movement generation,
bounds clamping, and OSC message sending.
"""

import unittest
from unittest.mock import MagicMock

from classes.head_movement import HeadMovementController

# Tolerance for floating point comparison due to clamping
FLOAT_TOLERANCE = 0.001


class TestHeadMovementController(unittest.TestCase):
    """Test cases for HeadMovementController."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_osc_client = MagicMock()
        self.controller = HeadMovementController(
            osc_client=self.mock_osc_client,
            center_x=0.0,
            center_y=0.0,
            half_size=0.1,
            t_min_ms=200,
            t_max_ms=600,
            interp_time_ms=300,
            use_step_limit=True,
            max_step=0.05,
            osc_address_x="/avatar/parameters/HeadX",
            osc_address_y="/avatar/parameters/HeadY",
            random_seed=42,  # Fixed seed for deterministic tests
        )

    def tearDown(self):
        """Clean up after tests."""
        if self.controller.is_running():
            self.controller.stop()

    def test_initialization(self):
        """Test that controller initializes with correct values."""
        self.assertEqual(self.controller.center_x, 0.0)
        self.assertEqual(self.controller.center_y, 0.0)
        self.assertEqual(self.controller.half_size, 0.1)
        self.assertEqual(self.controller.current_x, 0.0)
        self.assertEqual(self.controller.current_y, 0.0)
        self.assertFalse(self.controller.is_running())

    def test_clamp(self):
        """Test the clamp function."""
        # Test value within range
        self.assertEqual(self.controller.clamp(0.5, 0.0, 1.0), 0.5)
        # Test value below minimum
        self.assertEqual(self.controller.clamp(-0.5, 0.0, 1.0), 0.0)
        # Test value above maximum
        self.assertEqual(self.controller.clamp(1.5, 0.0, 1.0), 1.0)
        # Test edge cases
        self.assertEqual(self.controller.clamp(0.0, 0.0, 1.0), 0.0)
        self.assertEqual(self.controller.clamp(1.0, 0.0, 1.0), 1.0)

    def test_clamp_to_bounds(self):
        """Test that coordinates are clamped to square bounds."""
        # Test within bounds
        x, y = self.controller.clamp_to_bounds(0.05, 0.05)
        self.assertEqual(x, 0.05)
        self.assertEqual(y, 0.05)

        # Test outside bounds (positive)
        x, y = self.controller.clamp_to_bounds(0.2, 0.3)
        self.assertEqual(x, 0.1)  # cx + r = 0.0 + 0.1 = 0.1
        self.assertEqual(y, 0.1)

        # Test outside bounds (negative)
        x, y = self.controller.clamp_to_bounds(-0.2, -0.3)
        self.assertEqual(x, -0.1)  # cx - r = 0.0 - 0.1 = -0.1
        self.assertEqual(y, -0.1)

    def test_generate_random_target_within_bounds(self):
        """Test that generated targets are always within bounds."""
        for _ in range(100):
            x, y = self.controller.generate_random_target()
            # Check x is within bounds
            self.assertGreaterEqual(x, self.controller.center_x - self.controller.half_size)
            self.assertLessEqual(x, self.controller.center_x + self.controller.half_size)
            # Check y is within bounds
            self.assertGreaterEqual(y, self.controller.center_y - self.controller.half_size)
            self.assertLessEqual(y, self.controller.center_y + self.controller.half_size)

    def test_generate_random_target_step_limited(self):
        """Test step-limited movement mode."""
        self.controller.use_step_limit = True
        self.controller.max_step = 0.02

        for _ in range(10):
            prev_x, prev_y = self.controller.current_x, self.controller.current_y
            x, y = self.controller.generate_random_target()
            self.controller.current_x = x
            self.controller.current_y = y

            # The change should be limited to max_step (with tolerance for clamping)
            delta_x = abs(x - prev_x)
            delta_y = abs(y - prev_y)
            self.assertLessEqual(delta_x, self.controller.max_step + FLOAT_TOLERANCE)
            self.assertLessEqual(delta_y, self.controller.max_step + FLOAT_TOLERANCE)

    def test_generate_random_target_non_step_limited(self):
        """Test non-step-limited (random position) mode."""
        self.controller.use_step_limit = False

        # Generate many targets and verify they span the full range
        x_values = []
        y_values = []
        for _ in range(100):
            x, y = self.controller.generate_random_target()
            x_values.append(x)
            y_values.append(y)

        # Check that values span a reasonable portion of the range
        x_range = max(x_values) - min(x_values)
        y_range = max(y_values) - min(y_values)
        self.assertGreater(x_range, 0.05)  # Should have some spread
        self.assertGreater(y_range, 0.05)

    def test_get_random_interval(self):
        """Test that random intervals are within configured range."""
        for _ in range(50):
            interval = self.controller.get_random_interval()
            # Convert ms to seconds for comparison
            self.assertGreaterEqual(interval, self.controller.t_min_ms / 1000.0)
            self.assertLessEqual(interval, self.controller.t_max_ms / 1000.0)

    def test_send_head_target(self):
        """Test that OSC messages are sent correctly."""
        self.controller.send_head_target(0.05, -0.03)

        # Verify OSC messages were sent
        self.mock_osc_client.send_message.assert_any_call(
            "/avatar/parameters/HeadX", 0.05
        )
        self.mock_osc_client.send_message.assert_any_call(
            "/avatar/parameters/HeadY", -0.03
        )

    def test_update(self):
        """Test the update method."""
        new_x, new_y = self.controller.update()

        # Position should have changed (with deterministic seed)
        self.assertEqual(self.controller.current_x, new_x)
        self.assertEqual(self.controller.current_y, new_y)

        # OSC messages should have been sent
        self.assertTrue(self.mock_osc_client.send_message.called)

    def test_start_stop(self):
        """Test starting and stopping the controller."""
        self.assertFalse(self.controller.is_running())

        self.controller.start()
        self.assertTrue(self.controller.is_running())

        # Starting again should not create a new thread
        self.controller.start()
        self.assertTrue(self.controller.is_running())

        self.controller.stop()
        self.assertFalse(self.controller.is_running())

    def test_get_current_position(self):
        """Test getting the current position."""
        self.controller.current_x = 0.05
        self.controller.current_y = -0.02

        x, y = self.controller.get_current_position()
        self.assertEqual(x, 0.05)
        self.assertEqual(y, -0.02)

    def test_set_position(self):
        """Test manually setting position."""
        self.controller.set_position(0.05, -0.03)

        x, y = self.controller.get_current_position()
        self.assertEqual(x, 0.05)
        self.assertEqual(y, -0.03)

        # Verify OSC message was sent
        self.mock_osc_client.send_message.assert_any_call(
            "/avatar/parameters/HeadX", 0.05
        )
        self.mock_osc_client.send_message.assert_any_call(
            "/avatar/parameters/HeadY", -0.03
        )

    def test_set_position_clamped(self):
        """Test that set_position clamps to bounds."""
        self.controller.set_position(1.0, -1.0)

        x, y = self.controller.get_current_position()
        self.assertEqual(x, 0.1)   # Clamped to max bound
        self.assertEqual(y, -0.1)  # Clamped to min bound

    def test_deterministic_with_seed(self):
        """Test that results are deterministic with the same seed."""
        controller1 = HeadMovementController(
            osc_client=self.mock_osc_client,
            random_seed=123,
        )
        controller2 = HeadMovementController(
            osc_client=self.mock_osc_client,
            random_seed=123,
        )

        # Both should generate the same sequence
        for _ in range(10):
            x1, y1 = controller1.generate_random_target()
            x2, y2 = controller2.generate_random_target()
            controller1.current_x, controller1.current_y = x1, y1
            controller2.current_x, controller2.current_y = x2, y2
            self.assertEqual(x1, x2)
            self.assertEqual(y1, y2)

    def test_different_seeds_different_results(self):
        """Test that different seeds produce different results."""
        controller1 = HeadMovementController(
            osc_client=self.mock_osc_client,
            random_seed=123,
        )
        controller2 = HeadMovementController(
            osc_client=self.mock_osc_client,
            random_seed=456,
        )

        x1, y1 = controller1.generate_random_target()
        x2, y2 = controller2.generate_random_target()

        # At least one coordinate should be different
        self.assertTrue(x1 != x2 or y1 != y2)


class TestHeadMovementControllerCustomBounds(unittest.TestCase):
    """Test HeadMovementController with custom bounds."""

    def test_offset_center(self):
        """Test controller with offset center."""
        mock_osc = MagicMock()
        controller = HeadMovementController(
            osc_client=mock_osc,
            center_x=0.5,
            center_y=-0.3,
            half_size=0.2,
            random_seed=42,
        )

        # Generate many targets and verify all are within bounds
        for _ in range(100):
            x, y = controller.generate_random_target()
            controller.current_x = x
            controller.current_y = y
            self.assertGreaterEqual(x, 0.3)   # 0.5 - 0.2
            self.assertLessEqual(x, 0.7)      # 0.5 + 0.2
            self.assertGreaterEqual(y, -0.5)  # -0.3 - 0.2
            self.assertLessEqual(y, -0.1)     # -0.3 + 0.2


if __name__ == "__main__":
    unittest.main()
