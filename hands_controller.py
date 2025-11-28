"""
Hands Controller Module for NOVA-AI VRChat OSC Bot.

This module provides continuous, naturalistic hand motion synchronized with
speech. It receives text responses and TTS timing metadata from NOVA and
generates real-time hand gestures via OSC messages to VRChat.

Integration point: Call HandsController.on_nova_response() from NOVA's main
loop when scheduling TTS outputs.

Example usage:
    from hands_controller import HandsController

    hands = HandsController()
    await hands.start()

    # When NOVA generates a response:
    await hands.on_nova_response(
        text="Hello! How are you today?",
        tts_timing={'duration': 2.5, 'word_timestamps': [...]}
    )

    # When shutting down:
    await hands.stop()
"""

import asyncio
import json
import logging
import math
import os
import time
from typing import Any

import numpy as np
from pythonosc import udp_client

from cadence_analyzer import CadenceAnalyzer
from emotion_extractor import EmotionExtractor
from hand_mapper import HandMapper, OUTPUT_DIM
from models.hand_motion_model import HandMotionModel

# Configure logging
logger = logging.getLogger(__name__)


def _perlin_noise_1d(t: float, octaves: int = 4, seed: int = 0) -> float:
    """
    Generate 1D Perlin-like noise using sine wave composition.

    Args:
        t: Time/position value.
        octaves: Number of octaves to combine.
        seed: Seed for phase offset.

    Returns:
        float: Noise value in range [-1, 1].
    """
    value = 0.0
    amplitude = 1.0
    frequency = 1.0
    max_value = 0.0

    for i in range(octaves):
        phase = seed * 1000 + i * 137
        value += amplitude * math.sin(t * frequency + phase)
        max_value += amplitude
        amplitude *= 0.5
        frequency *= 2.0

    return value / max_value if max_value > 0 else 0.0


def _bezier_ease(t: float, p1: float = 0.25, p2: float = 0.75) -> float:
    """
    Cubic bezier easing function.

    Args:
        t: Input value [0, 1].
        p1: First control point.
        p2: Second control point.

    Returns:
        float: Eased value [0, 1].
    """
    t = max(0.0, min(1.0, t))
    # Simple cubic ease in-out approximation
    if t < 0.5:
        return 2 * t * t
    else:
        return 1 - pow(-2 * t + 2, 2) / 2


class ProceduralGestureGenerator:
    """
    Procedural fallback generator for hand gestures using Perlin noise
    and bezier easing curves.

    Used when the neural network model is not available or loaded.
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Initialize the procedural generator.

        Args:
            seed: Random seed for reproducible noise patterns.
        """
        self.seed = seed
        self.time = 0.0
        self.prev_pose = np.zeros(OUTPUT_DIM, dtype=np.float32)

        # Gesture state
        self.gesture_energy = 0.0
        self.gesture_phase = 0.0
        self.gesture_duration = 1.0
        self.gesture_start_time = 0.0

        # Per-finger oscillator phases
        self.finger_phases = np.random.uniform(0, 2 * math.pi, size=10)

        # Hand position targets for gesture envelope
        self.left_target = np.zeros(3, dtype=np.float32)
        self.right_target = np.zeros(3, dtype=np.float32)

    def set_gesture_params(
        self,
        energy: float,
        duration: float,
        emotion_vec: np.ndarray
    ) -> None:
        """
        Set parameters for a new gesture sequence.

        Args:
            energy: Gesture intensity (0-1).
            duration: Expected gesture duration in seconds.
            emotion_vec: Emotion vector for style modulation.
        """
        self.gesture_energy = np.clip(energy, 0.0, 1.0)
        self.gesture_duration = max(duration, 0.1)
        self.gesture_start_time = self.time
        self.gesture_phase = 0.0

        # Generate hand targets based on emotion and energy
        emotion_idx = int(np.argmax(emotion_vec))

        # Different gestures for different emotions
        if emotion_idx == 1:  # Happy
            # Open, outward gestures
            self.left_target = np.array([-0.2, 0.15, 0.1]) * energy
            self.right_target = np.array([0.2, 0.15, 0.1]) * energy
        elif emotion_idx == 2:  # Sad
            # Inward, lower gestures
            self.left_target = np.array([0.05, -0.1, -0.05]) * energy
            self.right_target = np.array([-0.05, -0.1, -0.05]) * energy
        elif emotion_idx == 3:  # Angry
            # Tense, forward gestures
            self.left_target = np.array([-0.1, 0.0, 0.15]) * energy
            self.right_target = np.array([0.1, 0.0, 0.15]) * energy
        elif emotion_idx == 4:  # Sarcastic
            # Asymmetric gestures
            self.left_target = np.array([-0.15, 0.1, 0.0]) * energy
            self.right_target = np.array([0.05, -0.05, 0.05]) * energy
        else:  # Calm/Neutral
            # Small, centered gestures
            self.left_target = np.array([-0.05, 0.0, 0.0]) * energy
            self.right_target = np.array([0.05, 0.0, 0.0]) * energy

    def generate_frame(self, dt: float) -> np.ndarray:
        """
        Generate a single frame of hand motion.

        Args:
            dt: Time delta since last frame in seconds.

        Returns:
            np.ndarray: Output pose of shape (OUTPUT_DIM,).
        """
        self.time += dt

        # Update gesture phase
        elapsed = self.time - self.gesture_start_time
        self.gesture_phase = min(elapsed / self.gesture_duration, 1.0)

        # Create envelope curve
        envelope = _bezier_ease(self.gesture_phase)
        if self.gesture_phase > 0.7:
            # Decay phase
            decay = (self.gesture_phase - 0.7) / 0.3
            envelope *= 1.0 - decay * 0.7

        output = np.zeros(OUTPUT_DIM, dtype=np.float32)

        # Generate hand positions with noise
        noise_scale = 0.03 * self.gesture_energy

        # Left hand position
        for i in range(3):
            noise = _perlin_noise_1d(self.time * 2, seed=self.seed + i) * noise_scale
            output[i] = self.left_target[i] * envelope + noise

        # Left hand rotation (smaller movements)
        for i in range(3):
            noise = _perlin_noise_1d(self.time * 1.5, seed=self.seed + 10 + i) * 0.02
            output[3 + i] = noise * self.gesture_energy

        # Left fingers
        for i in range(5):
            phase = self.finger_phases[i] + self.time * (2 + i * 0.3)
            base_curl = 0.3
            movement = math.sin(phase) * 0.1 * self.gesture_energy
            output[6 + i] = base_curl + movement

        # Right hand position
        for i in range(3):
            noise = _perlin_noise_1d(self.time * 2, seed=self.seed + 20 + i) * noise_scale
            output[11 + i] = self.right_target[i] * envelope + noise

        # Right hand rotation
        for i in range(3):
            noise = _perlin_noise_1d(self.time * 1.5, seed=self.seed + 30 + i) * 0.02
            output[14 + i] = noise * self.gesture_energy

        # Right fingers
        for i in range(5):
            phase = self.finger_phases[5 + i] + self.time * (2 + i * 0.3)
            base_curl = 0.3
            movement = math.sin(phase) * 0.1 * self.gesture_energy
            output[17 + i] = base_curl + movement

        # Gesture phase output
        output[22] = self.gesture_phase

        # Blend with previous pose for smoothness
        alpha = min(dt * 10, 0.8)
        output = alpha * output + (1 - alpha) * self.prev_pose
        self.prev_pose = output.copy()

        return output

    def generate_idle_frame(self, dt: float) -> np.ndarray:
        """
        Generate an idle micro-movement frame.

        Args:
            dt: Time delta since last frame in seconds.

        Returns:
            np.ndarray: Output pose of shape (OUTPUT_DIM,).
        """
        self.time += dt
        output = np.zeros(OUTPUT_DIM, dtype=np.float32)

        # Very subtle hand sway
        sway = _perlin_noise_1d(self.time * 0.5, seed=self.seed) * 0.02
        output[0] = sway  # Left hand X
        output[11] = -sway  # Right hand X

        # Subtle breathing-like Y movement
        breath = math.sin(self.time * 0.8) * 0.01
        output[1] = breath
        output[12] = breath

        # Idle finger micro-movements
        for i in range(5):
            phase = self.finger_phases[i] + self.time * 0.5
            output[6 + i] = 0.25 + math.sin(phase) * 0.02
            output[17 + i] = 0.25 + math.sin(phase + math.pi * 0.3) * 0.02

        # Blend with previous
        alpha = min(dt * 5, 0.5)
        output = alpha * output + (1 - alpha) * self.prev_pose
        self.prev_pose = output.copy()

        return output

    def reset(self) -> None:
        """Reset generator state."""
        self.time = 0.0
        self.prev_pose = np.zeros(OUTPUT_DIM, dtype=np.float32)
        self.gesture_energy = 0.0
        self.gesture_phase = 0.0


class HandsController:
    """
    Main controller for NOVA-AI hand motion generation.

    Manages the real-time update loop, model inference, and OSC communication
    with VRChat. Supports both neural network and procedural fallback modes.

    Attributes:
        config: Configuration dictionary.
        osc_client: OSC UDP client for VRChat.
        emotion_extractor: Emotion extraction module.
        cadence_analyzer: Cadence analysis module.
        hand_mapper: Output to OSC mapping module.
        model: Hand motion neural network model.
        procedural_gen: Procedural fallback generator.
    """

    def __init__(self, config_path: str = "hands_config.json") -> None:
        """
        Initialize the HandsController.

        Args:
            config_path: Path to the configuration JSON file.
        """
        self.config = self._load_config(config_path)
        self._setup_logging()

        # OSC client setup
        vrchat_config = self.config.get('vrchat', {})
        self.osc_address = os.environ.get(
            'VRCHAT_OSC_ADDRESS',
            vrchat_config.get('address', '127.0.0.1')
        )
        self.osc_port = int(os.environ.get(
            'VRCHAT_OSC_PORT',
            vrchat_config.get('port', 9000)
        ))
        self.osc_client: udp_client.SimpleUDPClient | None = None

        # OSC rate and timing
        self.osc_rate = self.config.get('osc_rate', 30)
        self.frame_time = 1.0 / self.osc_rate

        # Components
        self.emotion_extractor = EmotionExtractor()
        self.cadence_analyzer = CadenceAnalyzer()
        self.hand_mapper = HandMapper(self.config)

        # Model setup
        self.model: HandMotionModel | None = None
        self.use_model = False
        self.procedural_gen = ProceduralGestureGenerator()

        # State
        self._running = False
        self._update_task: asyncio.Task | None = None
        self._current_energy = 0.0
        self._target_energy = 0.0
        self._energy_override: float | None = None
        self._prev_pose = np.zeros(OUTPUT_DIM, dtype=np.float32)
        self._gesture_seed = np.random.uniform(-1, 1, size=2).astype(np.float32)

        # Current speech context
        self._current_emotion = np.zeros(6, dtype=np.float32)
        self._current_emotion[5] = 1.0  # Neutral default
        self._speech_rate = 0.5
        self._pause_penalty = 0.0
        self._speech_duration = 0.0
        self._speech_start_time = 0.0
        self._is_speaking = False

        # Timing
        self._last_frame_time = 0.0
        self._frame_count = 0

        # Debug
        self.debug_mode = self.config.get('log_level', 'INFO') == 'DEBUG'
        self.debug_interval = self.config.get('debug_print_interval', 30)

        # Load model if configured
        if self.config.get('use_torch', True) or self.config.get('use_procedural_fallback', True):
            model_path = self.config.get('model_path', 'models/hand_motion_model.pth')
            self.load_model(model_path)

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to configuration file.

        Returns:
            dict: Configuration dictionary with defaults merged.
        """
        defaults = {
            'vrchat': {'address': '127.0.0.1', 'port': 9000},
            'osc_rate': 30,
            'smoothing_alpha': 0.6,
            'model_path': 'models/hand_motion_model.pth',
            'use_torch': True,
            'use_procedural_fallback': True,
            'max_hand_offset': {'x': 0.35, 'y': 0.35, 'z': 0.35},
            'finger_curl_range': [0.0, 1.0],
            'gesture_energy_multiplier': 1.0,
            'log_level': 'INFO',
            'idle_energy_threshold': 0.1,
            'silence_threshold_seconds': 2.0,
            'debug_print_interval': 30
        }

        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            # Merge with defaults
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if k not in config[key]:
                            config[key][k] = v
            return config
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load config from {config_path}: {e}. Using defaults.")
            return defaults

    def _setup_logging(self) -> None:
        """Configure logging based on config."""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level, logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def start(self) -> None:
        """
        Start the hands controller.

        Initializes the OSC client and starts the update loop.
        """
        if self._running:
            logger.warning("HandsController already running")
            return

        # Initialize OSC client
        try:
            self.osc_client = udp_client.SimpleUDPClient(self.osc_address, self.osc_port)
            logger.info(f"OSC client connected to {self.osc_address}:{self.osc_port}")
        except Exception as e:
            logger.error(f"Failed to create OSC client: {e}")
            raise

        self._running = True
        self._last_frame_time = time.time()
        self._frame_count = 0

        # Start update loop
        self._update_task = asyncio.create_task(self._update_loop())
        logger.info("HandsController started")

    async def stop(self) -> None:
        """
        Stop the hands controller cleanly.

        Cancels the update loop and resets state.
        """
        if not self._running:
            return

        self._running = False

        if self._update_task is not None:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            self._update_task = None

        # Send neutral pose before stopping
        if self.osc_client is not None:
            try:
                neutral_pose = HandMapper.create_zero_pose()
                osc_messages = self.hand_mapper.map_to_osc(neutral_pose, apply_smoothing=False)
                for path, value in osc_messages:
                    self.osc_client.send_message(path, value)
            except Exception as e:
                logger.warning(f"Error sending neutral pose on stop: {e}")

        logger.info("HandsController stopped")

    async def on_nova_response(
        self,
        text: str,
        tts_timing: dict[str, Any] | None = None
    ) -> None:
        """
        Handle a new NOVA response.

        Called when NOVA plans to speak. Extracts emotion and cadence features
        to drive hand gestures.

        Args:
            text: The text response NOVA will speak.
            tts_timing: Optional TTS timing metadata containing:
                - duration: Total speech duration in seconds
                - word_timestamps: List of {word, start, end} dicts
        """
        if not text:
            return

        logger.debug(f"Processing response: {text[:50]}...")

        # Extract emotion
        self._current_emotion = self.emotion_extractor.extract(text)
        emotion_name = self.emotion_extractor.get_emotion_name(self._current_emotion)
        logger.debug(f"Detected emotion: {emotion_name}")

        # Analyze cadence
        if tts_timing is not None:
            cadence = self.cadence_analyzer.analyze_tts_plan(tts_timing)
        else:
            cadence = self.cadence_analyzer.analyze_text(text)

        self._speech_rate = cadence['speech_rate']
        self._pause_penalty = cadence['pause_penalty']
        self._speech_duration = cadence['estimated_duration']

        # Calculate target energy based on emotion and speech
        emotion_intensity = self.emotion_extractor.get_emotion_intensity(self._current_emotion)
        self._target_energy = self._calculate_energy(
            emotion_intensity,
            self._speech_rate,
            len(cadence.get('emphasis_indices', [])),
            len(text)
        )

        # Start speaking state
        self._speech_start_time = time.time()
        self._is_speaking = True

        # Reset model/generator for new sequence
        if self.model is not None:
            self.model.reset_state()

        # Set up procedural generator
        self.procedural_gen.set_gesture_params(
            energy=self._target_energy,
            duration=self._speech_duration,
            emotion_vec=self._current_emotion
        )

        # Generate new gesture seed
        self._gesture_seed = np.random.uniform(-1, 1, size=2).astype(np.float32)

        logger.info(
            f"Started gesture: energy={self._target_energy:.2f}, "
            f"duration={self._speech_duration:.2f}s, emotion={emotion_name}"
        )

    def _calculate_energy(
        self,
        emotion_intensity: float,
        speech_rate: float,
        emphasis_count: int,
        text_length: int
    ) -> float:
        """
        Calculate gesture energy from speech features.

        Args:
            emotion_intensity: Dominant emotion strength.
            speech_rate: Normalized speech rate.
            emphasis_count: Number of emphasis points.
            text_length: Length of text in characters.

        Returns:
            float: Gesture energy (0-1).
        """
        # Base energy from emotion intensity
        energy = emotion_intensity * 0.4

        # Add speech rate contribution
        energy += speech_rate * 0.3

        # Emphasis boosts energy
        if text_length > 0:
            emphasis_ratio = min(emphasis_count / (text_length / 50), 1.0)
            energy += emphasis_ratio * 0.2

        # Short, punchy text gets higher energy
        if text_length < 50:
            energy += 0.1

        return min(max(energy, 0.0), 1.0)

    def load_model(self, path: str | None) -> None:
        """
        Load the neural network model or enable procedural fallback.

        Args:
            path: Path to model file, or None to use procedural only.
        """
        self.use_model = False

        if path is None:
            logger.info("Using procedural fallback (no model path)")
            return

        # Try to load model
        use_torch = self.config.get('use_torch', True)
        self.model = HandMotionModel(use_torch=use_torch)

        if os.path.exists(path):
            success = self.model.load(path)
            if success:
                self.use_model = True
                logger.info(f"Loaded hand motion model from {path}")
                return

        # Try numpy fallback
        npz_path = path.replace('.pth', '.npz')
        if os.path.exists(npz_path):
            success = self.model.load(npz_path)
            if success:
                self.use_model = True
                logger.info(f"Loaded numpy model from {npz_path}")
                return

        if self.config.get('use_procedural_fallback', True):
            logger.info("Model not found, using procedural fallback")
        else:
            logger.warning("Model not found and procedural fallback disabled")

    def set_energy_override(self, energy: float) -> None:
        """
        Override gesture energy externally.

        Args:
            energy: Energy value (0-1), or negative to disable override.
        """
        if energy < 0:
            self._energy_override = None
        else:
            self._energy_override = max(0.0, min(1.0, energy))

    async def _update_loop(self) -> None:
        """
        Main update loop that runs at osc_rate FPS.

        Generates hand motion frames and sends OSC messages.
        """
        while self._running:
            try:
                loop_start = time.time()

                # Calculate delta time
                dt = loop_start - self._last_frame_time
                self._last_frame_time = loop_start

                # Update energy with smooth transition
                self._update_energy(dt)

                # Generate frame
                output = self._generate_frame(dt)

                # Send OSC messages
                await self._send_osc(output)

                # Debug logging
                self._frame_count += 1
                if self.debug_mode and self._frame_count % self.debug_interval == 0:
                    self._log_debug_info(output)

                # Check if speech ended
                self._check_speech_end()

                # Sleep to maintain frame rate
                elapsed = time.time() - loop_start
                sleep_time = max(0, self.frame_time - elapsed)
                await asyncio.sleep(sleep_time)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                await asyncio.sleep(self.frame_time)

    def _update_energy(self, dt: float) -> None:
        """
        Smoothly update current energy toward target.

        Args:
            dt: Delta time in seconds.
        """
        # Use override if set
        target = self._energy_override if self._energy_override is not None else self._target_energy

        # Smooth transition
        rate = 3.0 * dt  # Transition rate
        diff = target - self._current_energy

        if abs(diff) < 0.01:
            self._current_energy = target
        else:
            self._current_energy += diff * rate

    def _generate_frame(self, dt: float) -> np.ndarray:
        """
        Generate a single frame of hand motion.

        Args:
            dt: Delta time in seconds.

        Returns:
            np.ndarray: Output pose vector.
        """
        idle_threshold = self.config.get('idle_energy_threshold', 0.1)

        # Check if should use idle motion
        if self._current_energy < idle_threshold and not self._is_speaking:
            return self.procedural_gen.generate_idle_frame(dt)

        # Use neural network model if available
        if self.use_model and self.model is not None:
            return self._generate_model_frame(dt)

        # Procedural fallback
        return self.procedural_gen.generate_frame(dt)

    def _generate_model_frame(self, dt: float) -> np.ndarray:
        """
        Generate frame using neural network model.

        Args:
            dt: Delta time in seconds.

        Returns:
            np.ndarray: Output pose vector.
        """
        # Build model input
        input_vec = HandMotionModel.create_input(
            energy=self._current_energy,
            speech_rate=self._speech_rate,
            pause_penalty=self._pause_penalty,
            emotion_vec=self._current_emotion,
            gesture_seed=self._gesture_seed,
            prev_pose=self._prev_pose
        )

        # Run model inference
        output = self.model.forward(input_vec)

        # Scale by energy
        output = output * (0.3 + 0.7 * self._current_energy)

        # Update prev pose
        self._prev_pose = output.copy()

        return output

    async def _send_osc(self, output: np.ndarray) -> None:
        """
        Send OSC messages for hand pose.

        Args:
            output: Output pose vector.
        """
        if self.osc_client is None:
            return

        try:
            osc_messages = self.hand_mapper.map_to_osc(output)

            for path, value in osc_messages:
                self.osc_client.send_message(path, value)

        except Exception as e:
            logger.warning(f"Error sending OSC: {e}")

    def _check_speech_end(self) -> None:
        """Check if speech has ended and transition to idle."""
        if not self._is_speaking:
            return

        elapsed = time.time() - self._speech_start_time
        silence_threshold = self.config.get('silence_threshold_seconds', 2.0)

        if elapsed > self._speech_duration + silence_threshold:
            self._is_speaking = False
            self._target_energy = 0.0
            logger.debug("Speech ended, transitioning to idle")

    def _log_debug_info(self, output: np.ndarray) -> None:
        """
        Log debug information about current state.

        Args:
            output: Current output pose.
        """
        logger.debug(
            f"Frame {self._frame_count}: "
            f"energy={self._current_energy:.3f}, "
            f"speaking={self._is_speaking}, "
            f"L_pos={output[0:3]}, R_pos={output[11:14]}"
        )

    def is_running(self) -> bool:
        """Check if the controller is running."""
        return self._running

    def get_current_energy(self) -> float:
        """Get the current gesture energy level."""
        return self._current_energy

    def get_current_emotion(self) -> str:
        """Get the name of the current dominant emotion."""
        return self.emotion_extractor.get_emotion_name(self._current_emotion)
