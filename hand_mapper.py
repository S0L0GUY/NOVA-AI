"""
Hand Mapper Module for NOVA-AI Hand Motion System.

This module maps neural network model outputs to VRChat OSC parameter names
and values. Handles clamping, scaling, jitter, and smoothing filters.

Integration point: Called by HandsController._update_loop() to convert
model outputs to OSC messages for VRChat.
"""

import json
from typing import Any

import numpy as np


# Output vector indices
# L_hand_pos: 0-2 (x, y, z)
# L_hand_rot: 3-5 (x, y, z euler)
# L_fingers: 6-10 (thumb to pinky curl)
# R_hand_pos: 11-13 (x, y, z)
# R_hand_rot: 14-16 (x, y, z euler)
# R_fingers: 17-21 (thumb to pinky curl)
# gesture_phase: 22

OUTPUT_DIM = 23

# Slice definitions for clarity
L_POS_SLICE = slice(0, 3)
L_ROT_SLICE = slice(3, 6)
L_FINGER_SLICE = slice(6, 11)
R_POS_SLICE = slice(11, 14)
R_ROT_SLICE = slice(14, 17)
R_FINGER_SLICE = slice(17, 22)
GESTURE_PHASE_IDX = 22


class HandMapper:
    """
    Maps model output vectors to VRChat OSC parameter messages.

    Handles:
    - Clamping values to valid ranges
    - Scaling by config multipliers
    - Adding natural jitter for liveness
    - Smoothing for fluid motion
    - Converting to OSC path/value pairs

    Attributes:
        config: Configuration dictionary.
        osc_params: OSC parameter path mappings.
        max_offset: Maximum hand position offset values.
        finger_range: Valid range for finger curl values.
        energy_multiplier: Gesture energy scaling factor.
        jitter_amount: Amount of random jitter to add.
        prev_output: Previous output for smoothing.
        smoothing_alpha: Exponential smoothing factor.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize the HandMapper with configuration.

        Args:
            config: Configuration dictionary from hands_config.json.
        """
        self.config = config

        # Load OSC parameter paths
        self.osc_params = config.get('osc_parameters', {})
        self._setup_default_osc_params()

        # Value ranges
        self.max_offset = config.get('max_hand_offset', {'x': 0.35, 'y': 0.35, 'z': 0.35})
        self.finger_range = config.get('finger_curl_range', [0.0, 1.0])
        self.energy_multiplier = config.get('gesture_energy_multiplier', 1.0)

        # Smoothing
        self.smoothing_alpha = config.get('smoothing_alpha', 0.6)
        self.prev_output: np.ndarray | None = None

        # Small jitter for liveness
        self.jitter_amount = 0.005

    def _setup_default_osc_params(self) -> None:
        """Set up default OSC parameter paths if not in config."""
        defaults = {
            'left_hand_x': '/avatar/parameters/LeftHandX',
            'left_hand_y': '/avatar/parameters/LeftHandY',
            'left_hand_z': '/avatar/parameters/LeftHandZ',
            'left_hand_rot_x': '/avatar/parameters/LeftHandRotX',
            'left_hand_rot_y': '/avatar/parameters/LeftHandRotY',
            'left_hand_rot_z': '/avatar/parameters/LeftHandRotZ',
            'left_finger_1': '/avatar/parameters/LeftFinger1',
            'left_finger_2': '/avatar/parameters/LeftFinger2',
            'left_finger_3': '/avatar/parameters/LeftFinger3',
            'left_finger_4': '/avatar/parameters/LeftFinger4',
            'left_finger_5': '/avatar/parameters/LeftFinger5',
            'right_hand_x': '/avatar/parameters/RightHandX',
            'right_hand_y': '/avatar/parameters/RightHandY',
            'right_hand_z': '/avatar/parameters/RightHandZ',
            'right_hand_rot_x': '/avatar/parameters/RightHandRotX',
            'right_hand_rot_y': '/avatar/parameters/RightHandRotY',
            'right_hand_rot_z': '/avatar/parameters/RightHandRotZ',
            'right_finger_1': '/avatar/parameters/RightFinger1',
            'right_finger_2': '/avatar/parameters/RightFinger2',
            'right_finger_3': '/avatar/parameters/RightFinger3',
            'right_finger_4': '/avatar/parameters/RightFinger4',
            'right_finger_5': '/avatar/parameters/RightFinger5',
            'gesture_energy': '/avatar/parameters/HandGestureEnergy'
        }

        for key, value in defaults.items():
            if key not in self.osc_params:
                self.osc_params[key] = value

    def map_to_osc(
        self,
        model_output: np.ndarray,
        apply_smoothing: bool = True
    ) -> list[tuple[str, float]]:
        """
        Convert model output to list of OSC path/value pairs.

        Args:
            model_output: Model output array of shape (23,) or (OUTPUT_DIM,).
            apply_smoothing: Whether to apply exponential smoothing.

        Returns:
            list: List of (osc_path, value) tuples for sending to VRChat.
        """
        output = np.array(model_output, dtype=np.float32).flatten()

        # Ensure correct shape
        if len(output) < OUTPUT_DIM:
            padded = np.zeros(OUTPUT_DIM, dtype=np.float32)
            padded[:len(output)] = output
            output = padded

        # Apply smoothing if requested and previous output exists
        if apply_smoothing and self.prev_output is not None:
            output = self._smooth_output(output)

        # Store for next frame smoothing
        self.prev_output = output.copy()

        # Clamp and scale values
        output = self._clamp_and_scale(output)

        # Add micro jitter for liveness
        output = self._add_jitter(output)

        # Build OSC message list
        osc_messages = []

        # Left hand position
        osc_messages.append((self.osc_params['left_hand_x'], float(output[0])))
        osc_messages.append((self.osc_params['left_hand_y'], float(output[1])))
        osc_messages.append((self.osc_params['left_hand_z'], float(output[2])))

        # Left hand rotation
        osc_messages.append((self.osc_params['left_hand_rot_x'], float(output[3])))
        osc_messages.append((self.osc_params['left_hand_rot_y'], float(output[4])))
        osc_messages.append((self.osc_params['left_hand_rot_z'], float(output[5])))

        # Left fingers
        osc_messages.append((self.osc_params['left_finger_1'], float(output[6])))
        osc_messages.append((self.osc_params['left_finger_2'], float(output[7])))
        osc_messages.append((self.osc_params['left_finger_3'], float(output[8])))
        osc_messages.append((self.osc_params['left_finger_4'], float(output[9])))
        osc_messages.append((self.osc_params['left_finger_5'], float(output[10])))

        # Right hand position
        osc_messages.append((self.osc_params['right_hand_x'], float(output[11])))
        osc_messages.append((self.osc_params['right_hand_y'], float(output[12])))
        osc_messages.append((self.osc_params['right_hand_z'], float(output[13])))

        # Right hand rotation
        osc_messages.append((self.osc_params['right_hand_rot_x'], float(output[14])))
        osc_messages.append((self.osc_params['right_hand_rot_y'], float(output[15])))
        osc_messages.append((self.osc_params['right_hand_rot_z'], float(output[16])))

        # Right fingers
        osc_messages.append((self.osc_params['right_finger_1'], float(output[17])))
        osc_messages.append((self.osc_params['right_finger_2'], float(output[18])))
        osc_messages.append((self.osc_params['right_finger_3'], float(output[19])))
        osc_messages.append((self.osc_params['right_finger_4'], float(output[20])))
        osc_messages.append((self.osc_params['right_finger_5'], float(output[21])))

        # Gesture energy (derived from output magnitude)
        energy = self._calculate_gesture_energy(output)
        osc_messages.append((self.osc_params['gesture_energy'], float(energy)))

        return osc_messages

    def _smooth_output(self, output: np.ndarray) -> np.ndarray:
        """
        Apply exponential moving average smoothing.

        Args:
            output: Current output values.

        Returns:
            np.ndarray: Smoothed output values.
        """
        alpha = self.smoothing_alpha
        return alpha * output + (1 - alpha) * self.prev_output

    def _clamp_and_scale(self, output: np.ndarray) -> np.ndarray:
        """
        Clamp values to valid ranges and apply scaling.

        Args:
            output: Raw output values.

        Returns:
            np.ndarray: Clamped and scaled values.
        """
        result = output.copy()

        # Scale and clamp position values (-1 to 1 range, then scale by max offset)
        max_x = self.max_offset.get('x', 0.35)
        max_y = self.max_offset.get('y', 0.35)
        max_z = self.max_offset.get('z', 0.35)

        # Left hand position
        result[0] = np.clip(result[0], -1.0, 1.0) * max_x / 0.35
        result[1] = np.clip(result[1], -1.0, 1.0) * max_y / 0.35
        result[2] = np.clip(result[2], -1.0, 1.0) * max_z / 0.35

        # Right hand position
        result[11] = np.clip(result[11], -1.0, 1.0) * max_x / 0.35
        result[12] = np.clip(result[12], -1.0, 1.0) * max_y / 0.35
        result[13] = np.clip(result[13], -1.0, 1.0) * max_z / 0.35

        # Rotation values (-1 to 1)
        result[3:6] = np.clip(result[3:6], -1.0, 1.0)
        result[14:17] = np.clip(result[14:17], -1.0, 1.0)

        # Finger curl values (finger_range)
        min_curl, max_curl = self.finger_range
        result[6:11] = np.clip(result[6:11], min_curl, max_curl)
        result[17:22] = np.clip(result[17:22], min_curl, max_curl)

        # Gesture phase (0 to 1)
        if len(result) > GESTURE_PHASE_IDX:
            result[GESTURE_PHASE_IDX] = np.clip(result[GESTURE_PHASE_IDX], 0.0, 1.0)

        return result

    def _add_jitter(self, output: np.ndarray) -> np.ndarray:
        """
        Add small random jitter for natural liveness.

        Args:
            output: Output values.

        Returns:
            np.ndarray: Values with micro jitter added.
        """
        result = output.copy()

        # Add small jitter to position values
        jitter = np.random.uniform(
            -self.jitter_amount,
            self.jitter_amount,
            size=6
        )
        result[0:3] += jitter[0:3]
        result[11:14] += jitter[3:6]

        # Add very small jitter to finger curls
        finger_jitter = np.random.uniform(-0.002, 0.002, size=10)
        result[6:11] += finger_jitter[0:5]
        result[17:22] += finger_jitter[5:10]

        return result

    def _calculate_gesture_energy(self, output: np.ndarray) -> float:
        """
        Calculate overall gesture energy from output.

        Args:
            output: Output values.

        Returns:
            float: Gesture energy value (0-1).
        """
        # Combine position and rotation magnitudes
        l_pos_mag = np.linalg.norm(output[0:3])
        r_pos_mag = np.linalg.norm(output[11:14])
        l_rot_mag = np.linalg.norm(output[3:6])
        r_rot_mag = np.linalg.norm(output[14:17])

        # Normalize and combine
        pos_energy = (l_pos_mag + r_pos_mag) / 2.0
        rot_energy = (l_rot_mag + r_rot_mag) / 2.0

        energy = (pos_energy + rot_energy * 0.5) * self.energy_multiplier
        return float(np.clip(energy, 0.0, 1.0))

    def reset_smoothing(self) -> None:
        """Reset the smoothing state for new gesture sequences."""
        self.prev_output = None

    def set_energy_multiplier(self, multiplier: float) -> None:
        """
        Set the gesture energy multiplier.

        Args:
            multiplier: Energy scaling factor (typically 0.5 to 2.0).
        """
        self.energy_multiplier = max(0.0, multiplier)

    @staticmethod
    def create_zero_pose() -> np.ndarray:
        """
        Create a neutral/zero pose output vector.

        Returns:
            np.ndarray: Zero pose with shape (23,).
        """
        pose = np.zeros(OUTPUT_DIM, dtype=np.float32)
        # Set fingers to slightly curled neutral position
        pose[6:11] = 0.2  # Left fingers
        pose[17:22] = 0.2  # Right fingers
        return pose

    @staticmethod
    def create_idle_pose(phase: float) -> np.ndarray:
        """
        Create a subtle idle pose with minor oscillation.

        Args:
            phase: Animation phase (0-1) for oscillation.

        Returns:
            np.ndarray: Idle pose with shape (23,).
        """
        pose = np.zeros(OUTPUT_DIM, dtype=np.float32)

        # Subtle hand sway
        sway = np.sin(phase * 2 * np.pi) * 0.02
        pose[0] = sway  # L hand X
        pose[11] = -sway  # R hand X (opposite)

        # Subtle finger movement
        finger_base = 0.25
        finger_wave = np.sin(phase * 2 * np.pi + np.arange(5) * 0.3) * 0.05
        pose[6:11] = finger_base + finger_wave
        pose[17:22] = finger_base + finger_wave

        pose[GESTURE_PHASE_IDX] = phase
        return pose

    def get_osc_param_path(self, param_key: str) -> str:
        """
        Get OSC parameter path for a given key.

        Args:
            param_key: Parameter key name.

        Returns:
            str: OSC path string.
        """
        return self.osc_params.get(param_key, '')

    def load_config_from_file(self, config_path: str) -> None:
        """
        Reload configuration from a JSON file.

        Args:
            config_path: Path to configuration JSON file.
        """
        with open(config_path, 'r') as f:
            config = json.load(f)

        self.config = config
        self.osc_params = config.get('osc_parameters', self.osc_params)
        self.max_offset = config.get('max_hand_offset', self.max_offset)
        self.finger_range = config.get('finger_curl_range', self.finger_range)
        self.energy_multiplier = config.get('gesture_energy_multiplier', self.energy_multiplier)
        self.smoothing_alpha = config.get('smoothing_alpha', self.smoothing_alpha)
