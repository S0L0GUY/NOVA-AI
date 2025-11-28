"""
Hand Motion Model Module for NOVA-AI Hand Motion System.

This module defines a tiny, low-latency recurrent neural network for generating
naturalistic hand motion parameters. Includes both PyTorch implementation and
pure numpy fallback.

Integration point: Used by HandsController to generate per-frame hand poses.
"""

from typing import Any

import numpy as np

# Input dimensions
# energy (1) + speech_rate (1) + pause_penalty (1) + emotion_vec (6) +
# gesture_seed (2) + prev_pose (23) = 34
INPUT_DIM = 34
OUTPUT_DIM = 23
HIDDEN_DIM = 64
NUM_LAYERS = 2

# Emotion vector dimension
EMOTION_DIM = 6


def get_input_dim() -> int:
    """Get the input dimension for the hand motion model."""
    return INPUT_DIM


def get_output_dim() -> int:
    """Get the output dimension for the hand motion model."""
    return OUTPUT_DIM


class HandMotionModelNumpy:
    """
    Pure numpy fallback implementation of the hand motion model.

    Uses simple exponential smoothing with linear layers for basic
    hand motion generation when PyTorch is not available.

    Attributes:
        hidden_state: Internal state for temporal continuity.
        weights1: First layer weights.
        weights2: Second layer weights.
        bias1: First layer bias.
        bias2: Second layer bias.
    """

    def __init__(self) -> None:
        """Initialize the numpy fallback model with random weights."""
        # Initialize weights with small random values for stability
        np.random.seed(42)  # Reproducible initialization

        self.hidden_state = np.zeros(HIDDEN_DIM, dtype=np.float32)

        # Two-layer MLP with hidden state feedback
        self.weights1 = np.random.randn(INPUT_DIM + HIDDEN_DIM, HIDDEN_DIM).astype(np.float32) * 0.1
        self.bias1 = np.zeros(HIDDEN_DIM, dtype=np.float32)

        self.weights2 = np.random.randn(HIDDEN_DIM, OUTPUT_DIM).astype(np.float32) * 0.1
        self.bias2 = np.zeros(OUTPUT_DIM, dtype=np.float32)

        # Hidden state update weights
        self.hidden_decay = 0.9

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass through the model.

        Args:
            x: Input array of shape (batch, INPUT_DIM) or (INPUT_DIM,).

        Returns:
            np.ndarray: Output array of shape (batch, OUTPUT_DIM) or (OUTPUT_DIM,).
        """
        # Handle both batched and single inputs
        if x.ndim == 1:
            x = x.reshape(1, -1)

        batch_size = x.shape[0]
        outputs = []

        for i in range(batch_size):
            # Concatenate input with hidden state
            combined = np.concatenate([x[i], self.hidden_state])

            # First layer with tanh activation
            h = np.tanh(np.dot(combined, self.weights1) + self.bias1)

            # Update hidden state
            self.hidden_state = self.hidden_decay * self.hidden_state + (1 - self.hidden_decay) * h

            # Output layer
            output = np.dot(h, self.weights2) + self.bias2

            # Apply tanh to bound outputs to -1, 1
            output = np.tanh(output)

            outputs.append(output)

        result = np.stack(outputs, axis=0)
        return result.squeeze()

    def reset_state(self) -> None:
        """Reset the hidden state for new sequences."""
        self.hidden_state = np.zeros(HIDDEN_DIM, dtype=np.float32)

    def save(self, path: str) -> None:
        """
        Save model weights to a numpy file.

        Args:
            path: Path to save the .npz file.
        """
        np.savez(
            path,
            weights1=self.weights1,
            bias1=self.bias1,
            weights2=self.weights2,
            bias2=self.bias2
        )

    def load(self, path: str) -> None:
        """
        Load model weights from a numpy file.

        Args:
            path: Path to the .npz file.
        """
        data = np.load(path)
        self.weights1 = data['weights1']
        self.bias1 = data['bias1']
        self.weights2 = data['weights2']
        self.bias2 = data['bias2']


# Try to import PyTorch for the main model
_TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn as nn
    _TORCH_AVAILABLE = True
except ImportError:
    pass


if _TORCH_AVAILABLE:
    class HandMotionModelTorch(nn.Module):
        """
        PyTorch implementation of the hand motion model.

        Uses a small GRU-based architecture for efficient temporal
        modeling of hand motion sequences.

        Attributes:
            gru: GRU layer for temporal modeling.
            fc_out: Output fully connected layer.
            hidden: Current hidden state.
        """

        def __init__(
            self,
            input_dim: int = INPUT_DIM,
            hidden_dim: int = HIDDEN_DIM,
            output_dim: int = OUTPUT_DIM,
            num_layers: int = NUM_LAYERS
        ) -> None:
            """
            Initialize the PyTorch hand motion model.

            Args:
                input_dim: Input feature dimension.
                hidden_dim: Hidden layer dimension.
                output_dim: Output dimension.
                num_layers: Number of GRU layers.
            """
            super().__init__()

            self.input_dim = input_dim
            self.hidden_dim = hidden_dim
            self.output_dim = output_dim
            self.num_layers = num_layers

            # GRU for temporal modeling
            self.gru = nn.GRU(
                input_size=input_dim,
                hidden_size=hidden_dim,
                num_layers=num_layers,
                batch_first=True,
                dropout=0.0 if num_layers == 1 else 0.1
            )

            # Output projection
            self.fc_out = nn.Sequential(
                nn.Linear(hidden_dim, hidden_dim),
                nn.Tanh(),
                nn.Linear(hidden_dim, output_dim),
                nn.Tanh()  # Bound outputs to -1, 1
            )

            # Hidden state storage
            self.hidden: torch.Tensor | None = None

            # Initialize weights
            self._init_weights()

        def _init_weights(self) -> None:
            """Initialize model weights."""
            for name, param in self.named_parameters():
                if 'weight' in name:
                    nn.init.xavier_uniform_(param)
                elif 'bias' in name:
                    nn.init.zeros_(param)

        def forward(
            self,
            x: torch.Tensor,
            hidden: torch.Tensor | None = None
        ) -> tuple[torch.Tensor, torch.Tensor]:
            """
            Forward pass through the model.

            Args:
                x: Input tensor of shape (batch, seq_len, input_dim).
                hidden: Optional hidden state tensor.

            Returns:
                tuple: (output tensor, new hidden state).
            """
            # Handle 2D input (batch, features) -> add sequence dimension
            if x.dim() == 2:
                x = x.unsqueeze(1)

            batch_size = x.size(0)

            # Use provided hidden state or stored state
            if hidden is None:
                hidden = self.hidden
            if hidden is None:
                hidden = torch.zeros(
                    self.num_layers, batch_size, self.hidden_dim,
                    device=x.device, dtype=x.dtype
                )

            # GRU forward
            gru_out, new_hidden = self.gru(x, hidden)

            # Output projection
            output = self.fc_out(gru_out)

            # Store hidden state for autoregressive generation
            self.hidden = new_hidden.detach()

            # Squeeze sequence dimension if input was 2D
            if output.size(1) == 1:
                output = output.squeeze(1)

            return output, new_hidden

        def reset_state(self) -> None:
            """Reset hidden state for new sequences."""
            self.hidden = None

        def generate_sequence(
            self,
            initial_input: torch.Tensor,
            num_frames: int,
            prev_pose_idx: int = 8  # Index where prev_pose starts in input
        ) -> torch.Tensor:
            """
            Generate a sequence of hand poses autoregressively.

            Args:
                initial_input: Initial input tensor of shape (batch, input_dim).
                num_frames: Number of frames to generate.
                prev_pose_idx: Index in input where prev_pose starts.

            Returns:
                torch.Tensor: Generated sequence of shape (batch, num_frames, output_dim).
            """
            self.reset_state()

            outputs = []

            current_input = initial_input.clone()

            for _ in range(num_frames):
                output, _ = self.forward(current_input)
                outputs.append(output)

                # Update prev_pose in input for next iteration
                current_input = current_input.clone()
                current_input[:, prev_pose_idx:prev_pose_idx + self.output_dim] = output

            return torch.stack(outputs, dim=1)

        def save_torchscript(self, path: str) -> None:
            """
            Save model as TorchScript for inference.

            Args:
                path: Path to save the .pt file.
            """
            self.eval()
            scripted = torch.jit.script(self)
            torch.jit.save(scripted, path)

        def save_state_dict(self, path: str) -> None:
            """
            Save model state dict.

            Args:
                path: Path to save the .pth file.
            """
            torch.save(self.state_dict(), path)

        @classmethod
        def load_from_state_dict(cls, path: str, **kwargs: Any) -> "HandMotionModelTorch":
            """
            Load model from state dict file.

            Args:
                path: Path to the .pth file.
                **kwargs: Model constructor arguments.

            Returns:
                HandMotionModelTorch: Loaded model instance.
            """
            model = cls(**kwargs)
            model.load_state_dict(torch.load(path, map_location='cpu', weights_only=True))
            model.eval()
            return model


class HandMotionModel:
    """
    Unified interface for hand motion models.

    Automatically selects PyTorch or numpy backend based on availability
    and configuration.

    Attributes:
        model: Underlying model (PyTorch or numpy).
        use_torch: Whether PyTorch backend is active.
    """

    def __init__(self, use_torch: bool = True) -> None:
        """
        Initialize the hand motion model.

        Args:
            use_torch: Whether to prefer PyTorch (if available).
        """
        self.use_torch = use_torch and _TORCH_AVAILABLE

        if self.use_torch:
            self.model = HandMotionModelTorch()
            self.model.eval()
        else:
            self.model = HandMotionModelNumpy()

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Generate hand motion output from input features.

        Args:
            x: Input array of shape (INPUT_DIM,) or (batch, INPUT_DIM).

        Returns:
            np.ndarray: Output array of shape (OUTPUT_DIM,) or (batch, OUTPUT_DIM).
        """
        if self.use_torch:
            import torch
            with torch.no_grad():
                x_tensor = torch.tensor(x, dtype=torch.float32)
                if x_tensor.dim() == 1:
                    x_tensor = x_tensor.unsqueeze(0)
                output, _ = self.model(x_tensor)
                return output.numpy()
        else:
            return self.model.forward(x)

    def reset_state(self) -> None:
        """Reset model state for new sequences."""
        self.model.reset_state()

    def load(self, path: str) -> bool:
        """
        Load model weights from file.

        Args:
            path: Path to model file (.pth for PyTorch, .npz for numpy).

        Returns:
            bool: True if loading succeeded.
        """
        try:
            if self.use_torch and path.endswith('.pth'):
                import torch
                self.model.load_state_dict(
                    torch.load(path, map_location='cpu', weights_only=True)
                )
                self.model.eval()
                return True
            elif path.endswith('.npz'):
                if self.use_torch:
                    # Fall back to numpy model
                    self.model = HandMotionModelNumpy()
                    self.use_torch = False
                self.model.load(path)
                return True
        except (FileNotFoundError, RuntimeError, KeyError) as e:
            print(f"Failed to load model from {path}: {e}")
            return False
        return False

    def save(self, path: str) -> None:
        """
        Save model weights to file.

        Args:
            path: Path to save model (.pth for PyTorch, .npz for numpy).
        """
        if self.use_torch:
            self.model.save_state_dict(path)
        else:
            self.model.save(path)

    @staticmethod
    def create_input(
        energy: float,
        speech_rate: float,
        pause_penalty: float,
        emotion_vec: np.ndarray,
        gesture_seed: np.ndarray | None = None,
        prev_pose: np.ndarray | None = None
    ) -> np.ndarray:
        """
        Create model input vector from components.

        Args:
            energy: Gesture energy level (0-1).
            speech_rate: Normalized speech rate (0-1).
            pause_penalty: Recent silence ratio (0-1).
            emotion_vec: Emotion vector of shape (6,).
            gesture_seed: Random seed values of shape (2,), or None for random.
            prev_pose: Previous output pose of shape (23,), or None for zeros.

        Returns:
            np.ndarray: Input vector of shape (INPUT_DIM,).
        """
        if gesture_seed is None:
            gesture_seed = np.random.uniform(-1, 1, size=2).astype(np.float32)

        if prev_pose is None:
            prev_pose = np.zeros(OUTPUT_DIM, dtype=np.float32)

        # Ensure correct shapes
        emotion_vec = np.asarray(emotion_vec, dtype=np.float32).flatten()[:EMOTION_DIM]
        if len(emotion_vec) < EMOTION_DIM:
            emotion_vec = np.pad(emotion_vec, (0, EMOTION_DIM - len(emotion_vec)))

        gesture_seed = np.asarray(gesture_seed, dtype=np.float32).flatten()[:2]
        prev_pose = np.asarray(prev_pose, dtype=np.float32).flatten()[:OUTPUT_DIM]
        if len(prev_pose) < OUTPUT_DIM:
            prev_pose = np.pad(prev_pose, (0, OUTPUT_DIM - len(prev_pose)))

        # Concatenate all components
        input_vec = np.concatenate([
            [energy, speech_rate, pause_penalty],
            emotion_vec,
            gesture_seed,
            prev_pose
        ]).astype(np.float32)

        return input_vec


def is_torch_available() -> bool:
    """Check if PyTorch is available."""
    return _TORCH_AVAILABLE
