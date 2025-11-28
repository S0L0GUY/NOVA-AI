"""
Training Script for NOVA-AI Hand Motion Model.

This script generates synthetic training data and trains the hand motion
neural network. Since real motion capture data is not available, it creates
procedural gesture sequences with controlled variations.

Usage:
    python train_hand_model.py [--epochs 100] [--batch-size 32] [--save-numpy]

Output:
    - models/hand_motion_model.pth (PyTorch model)
    - models/hand_motion_model.npz (Numpy fallback model)
"""

import argparse
import math
import os
import random
from typing import Any

import numpy as np

# Model parameters
INPUT_DIM = 34
OUTPUT_DIM = 23
HIDDEN_DIM = 64
NUM_LAYERS = 2
EMOTION_DIM = 6

# Training parameters
DEFAULT_EPOCHS = 100
DEFAULT_BATCH_SIZE = 32
DEFAULT_LR = 1e-3
SEQUENCE_LENGTH = 30  # Frames per sequence (about 1 second at 30 FPS)


def generate_gesture_envelope(
    num_frames: int,
    attack: float = 0.2,
    sustain: float = 0.5,
    release: float = 0.3
) -> np.ndarray:
    """
    Generate an ADSR-like gesture envelope.

    Args:
        num_frames: Total number of frames.
        attack: Attack duration ratio.
        sustain: Sustain duration ratio.
        release: Release duration ratio.

    Returns:
        np.ndarray: Envelope curve of shape (num_frames,).
    """
    envelope = np.zeros(num_frames, dtype=np.float32)

    attack_frames = int(num_frames * attack)
    sustain_frames = int(num_frames * sustain)
    release_frames = num_frames - attack_frames - sustain_frames

    # Attack
    for i in range(attack_frames):
        t = i / max(attack_frames - 1, 1)
        envelope[i] = t * t  # Quadratic ease in

    # Sustain
    for i in range(sustain_frames):
        idx = attack_frames + i
        # Slight variation during sustain
        envelope[idx] = 0.9 + 0.1 * math.sin(i / sustain_frames * math.pi)

    # Release
    for i in range(release_frames):
        idx = attack_frames + sustain_frames + i
        t = i / max(release_frames - 1, 1)
        envelope[idx] = 1.0 - t * t  # Quadratic ease out

    return envelope


def generate_hand_trajectory(
    num_frames: int,
    energy: float,
    emotion_idx: int,
    hand: str = 'left'
) -> np.ndarray:
    """
    Generate a hand position trajectory.

    Args:
        num_frames: Number of frames.
        energy: Gesture energy (0-1).
        emotion_idx: Dominant emotion index.
        hand: 'left' or 'right'.

    Returns:
        np.ndarray: Position trajectory of shape (num_frames, 3).
    """
    trajectory = np.zeros((num_frames, 3), dtype=np.float32)
    envelope = generate_gesture_envelope(num_frames)

    # Base gesture patterns for different emotions
    patterns = {
        0: {'amp': 0.1, 'freq': 0.5},   # Calm
        1: {'amp': 0.25, 'freq': 1.5},  # Happy
        2: {'amp': 0.1, 'freq': 0.3},   # Sad
        3: {'amp': 0.2, 'freq': 2.0},   # Angry
        4: {'amp': 0.15, 'freq': 1.0},  # Sarcastic
        5: {'amp': 0.08, 'freq': 0.4},  # Neutral
    }

    pattern = patterns.get(emotion_idx, patterns[5])
    amp = pattern['amp'] * energy
    freq = pattern['freq']

    # Mirror for right hand
    mirror = -1.0 if hand == 'right' else 1.0

    for i in range(num_frames):
        t = i / num_frames
        phase = t * 2 * math.pi * freq

        # X: Side-to-side movement
        trajectory[i, 0] = mirror * amp * math.sin(phase) * envelope[i]

        # Y: Up-down movement
        trajectory[i, 1] = amp * 0.7 * math.sin(phase * 1.5 + 0.5) * envelope[i]

        # Z: Forward-back movement
        trajectory[i, 2] = amp * 0.5 * math.sin(phase * 0.8) * envelope[i]

        # Add noise
        trajectory[i] += np.random.normal(0, 0.005, 3)

    return trajectory


def generate_rotation_sequence(
    num_frames: int,
    energy: float
) -> np.ndarray:
    """
    Generate hand rotation sequence.

    Args:
        num_frames: Number of frames.
        energy: Gesture energy (0-1).

    Returns:
        np.ndarray: Rotation sequence of shape (num_frames, 3).
    """
    rotations = np.zeros((num_frames, 3), dtype=np.float32)
    envelope = generate_gesture_envelope(num_frames, attack=0.3, release=0.4)

    amp = 0.3 * energy

    for i in range(num_frames):
        t = i / num_frames
        phase = t * 2 * math.pi

        rotations[i, 0] = amp * 0.5 * math.sin(phase * 1.2) * envelope[i]
        rotations[i, 1] = amp * 0.3 * math.sin(phase * 0.8 + 0.3) * envelope[i]
        rotations[i, 2] = amp * 0.4 * math.sin(phase * 1.5 + 0.7) * envelope[i]

        rotations[i] += np.random.normal(0, 0.01, 3)

    return rotations


def generate_finger_curls(
    num_frames: int,
    energy: float,
    emotion_idx: int
) -> np.ndarray:
    """
    Generate finger curl sequences.

    Args:
        num_frames: Number of frames.
        energy: Gesture energy (0-1).
        emotion_idx: Dominant emotion index.

    Returns:
        np.ndarray: Finger curl sequence of shape (num_frames, 5).
    """
    curls = np.zeros((num_frames, 5), dtype=np.float32)

    # Base curl per emotion
    base_curls = {
        0: 0.3,   # Calm - relaxed
        1: 0.15,  # Happy - open
        2: 0.5,   # Sad - curled
        3: 0.6,   # Angry - tense
        4: 0.25,  # Sarcastic - slightly open
        5: 0.35,  # Neutral
    }

    base = base_curls.get(emotion_idx, 0.35)
    envelope = generate_gesture_envelope(num_frames)

    for i in range(num_frames):
        for finger in range(5):
            # Each finger has slightly different timing
            t = i / num_frames
            phase = t * 2 * math.pi + finger * 0.3

            # Base curl plus movement
            movement = energy * 0.2 * math.sin(phase) * envelope[i]
            curls[i, finger] = np.clip(base + movement, 0.0, 1.0)

            # Add micro noise
            curls[i, finger] += np.random.normal(0, 0.01)
            curls[i, finger] = np.clip(curls[i, finger], 0.0, 1.0)

    return curls


def generate_synthetic_sample(
    num_frames: int = SEQUENCE_LENGTH
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a single synthetic training sample.

    Returns:
        tuple: (inputs, targets) arrays of shapes
               (num_frames, INPUT_DIM) and (num_frames, OUTPUT_DIM).
    """
    # Random parameters
    energy = random.uniform(0.1, 1.0)
    speech_rate = random.uniform(0.2, 0.8)
    pause_penalty = random.uniform(0.0, 0.5)

    # Random emotion (one-hot with some noise)
    emotion_idx = random.randint(0, 5)
    emotion_vec = np.zeros(EMOTION_DIM, dtype=np.float32)
    emotion_vec[emotion_idx] = 0.7 + random.uniform(0, 0.3)
    # Add small values to other emotions
    for i in range(EMOTION_DIM):
        if i != emotion_idx:
            emotion_vec[i] = random.uniform(0, 0.15)
    emotion_vec = emotion_vec / np.sum(emotion_vec)

    # Generate target sequences
    l_pos = generate_hand_trajectory(num_frames, energy, emotion_idx, 'left')
    l_rot = generate_rotation_sequence(num_frames, energy)
    l_fingers = generate_finger_curls(num_frames, energy, emotion_idx)

    r_pos = generate_hand_trajectory(num_frames, energy, emotion_idx, 'right')
    r_rot = generate_rotation_sequence(num_frames, energy)
    r_fingers = generate_finger_curls(num_frames, energy, emotion_idx)

    # Gesture phase
    gesture_phase = np.linspace(0, 1, num_frames).astype(np.float32)

    # Build target array
    targets = np.zeros((num_frames, OUTPUT_DIM), dtype=np.float32)
    targets[:, 0:3] = l_pos
    targets[:, 3:6] = l_rot
    targets[:, 6:11] = l_fingers
    targets[:, 11:14] = r_pos
    targets[:, 14:17] = r_rot
    targets[:, 17:22] = r_fingers
    targets[:, 22] = gesture_phase

    # Build input array (with autoregressive prev_pose)
    inputs = np.zeros((num_frames, INPUT_DIM), dtype=np.float32)

    # Fixed inputs across sequence
    gesture_seed = np.random.uniform(-1, 1, size=2).astype(np.float32)

    for i in range(num_frames):
        # Time-varying energy based on envelope
        envelope = generate_gesture_envelope(num_frames)
        frame_energy = energy * (0.5 + 0.5 * envelope[i])

        inputs[i, 0] = frame_energy
        inputs[i, 1] = speech_rate
        inputs[i, 2] = pause_penalty
        inputs[i, 3:9] = emotion_vec
        inputs[i, 9:11] = gesture_seed

        # Previous pose (autoregressive)
        if i == 0:
            inputs[i, 11:34] = 0.0  # Zero initial pose
        else:
            inputs[i, 11:34] = targets[i - 1, :]

    return inputs, targets


def generate_dataset(
    num_samples: int = 1000,
    sequence_length: int = SEQUENCE_LENGTH
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a full synthetic dataset.

    Args:
        num_samples: Number of sequences to generate.
        sequence_length: Frames per sequence.

    Returns:
        tuple: (inputs, targets) of shapes
               (num_samples, seq_len, INPUT_DIM) and (num_samples, seq_len, OUTPUT_DIM).
    """
    print(f"Generating {num_samples} training samples...")

    inputs_list = []
    targets_list = []

    for i in range(num_samples):
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{num_samples}")

        inp, tgt = generate_synthetic_sample(sequence_length)
        inputs_list.append(inp)
        targets_list.append(tgt)

    inputs = np.stack(inputs_list, axis=0)
    targets = np.stack(targets_list, axis=0)

    print(f"Dataset shape: inputs={inputs.shape}, targets={targets.shape}")
    return inputs, targets


def train_pytorch_model(
    inputs: np.ndarray,
    targets: np.ndarray,
    epochs: int = DEFAULT_EPOCHS,
    batch_size: int = DEFAULT_BATCH_SIZE,
    learning_rate: float = DEFAULT_LR,
    save_path: str = "models/hand_motion_model.pth"
) -> dict[str, Any]:
    """
    Train the PyTorch hand motion model.

    Args:
        inputs: Training inputs of shape (N, seq_len, INPUT_DIM).
        targets: Training targets of shape (N, seq_len, OUTPUT_DIM).
        epochs: Number of training epochs.
        batch_size: Batch size.
        learning_rate: Learning rate.
        save_path: Path to save the model.

    Returns:
        dict: Training history with losses.
    """
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        print("PyTorch not available. Skipping PyTorch training.")
        return {}

    # Import model
    from models.hand_motion_model import HandMotionModelTorch

    print("\n--- Training PyTorch Model ---")

    # Convert to tensors
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(targets, dtype=torch.float32)

    dataset = TensorDataset(X, Y)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # Create model
    model = HandMotionModelTorch(
        input_dim=INPUT_DIM,
        hidden_dim=HIDDEN_DIM,
        output_dim=OUTPUT_DIM,
        num_layers=NUM_LAYERS
    )

    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=10
    )

    history = {'loss': []}
    best_loss = float('inf')

    for epoch in range(epochs):
        model.train()
        epoch_loss = 0.0
        num_batches = 0

        for batch_x, batch_y in dataloader:
            optimizer.zero_grad()

            # Reset hidden state for each batch
            model.reset_state()

            # Forward pass (teacher forcing: use ground truth for each step)
            outputs = []
            for t in range(batch_x.size(1)):
                frame_input = batch_x[:, t, :]
                output, _ = model(frame_input)
                outputs.append(output)

            outputs = torch.stack(outputs, dim=1)

            # Compute loss
            loss = criterion(outputs, batch_y)

            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            epoch_loss += loss.item()
            num_batches += 1

        avg_loss = epoch_loss / num_batches
        history['loss'].append(avg_loss)
        scheduler.step(avg_loss)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch {epoch + 1}/{epochs} - Loss: {avg_loss:.6f}")

        # Save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            torch.save(model.state_dict(), save_path)

    print(f"\nBest loss: {best_loss:.6f}")
    print(f"Model saved to {save_path}")

    return history


def train_numpy_model(
    inputs: np.ndarray,
    targets: np.ndarray,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LR,
    save_path: str = "models/hand_motion_model.npz"
) -> dict[str, Any]:
    """
    Train the numpy fallback model.

    Uses simple gradient descent on the linear layers.

    Args:
        inputs: Training inputs of shape (N, seq_len, INPUT_DIM).
        targets: Training targets of shape (N, seq_len, OUTPUT_DIM).
        epochs: Number of training epochs.
        learning_rate: Learning rate.
        save_path: Path to save the model.

    Returns:
        dict: Training history with losses.
    """
    from models.hand_motion_model import HandMotionModelNumpy

    print("\n--- Training Numpy Model ---")

    model = HandMotionModelNumpy()
    history = {'loss': []}
    best_loss = float('inf')

    num_samples = inputs.shape[0]
    seq_len = inputs.shape[1]

    for epoch in range(epochs):
        epoch_loss = 0.0
        indices = np.random.permutation(num_samples)

        for idx in indices:
            sample_inputs = inputs[idx]  # (seq_len, INPUT_DIM)
            sample_targets = targets[idx]  # (seq_len, OUTPUT_DIM)

            model.reset_state()

            # Forward pass and collect gradients
            outputs = []
            for t in range(seq_len):
                output = model.forward(sample_inputs[t])
                outputs.append(output)

            outputs = np.array(outputs)

            # MSE loss
            loss = np.mean((outputs - sample_targets) ** 2)
            epoch_loss += loss

            # Simple gradient update (approximate)
            # Update output layer weights towards targets
            for t in range(seq_len):
                error = outputs[t] - sample_targets[t]
                # Simplified gradient (assumes hidden state is similar)
                grad = learning_rate * error / seq_len
                model.bias2 -= grad

        avg_loss = epoch_loss / num_samples
        history['loss'].append(avg_loss)

        if (epoch + 1) % 10 == 0 or epoch == 0:
            print(f"Epoch {epoch + 1}/{epochs} - Loss: {avg_loss:.6f}")

        # Save best model
        if avg_loss < best_loss:
            best_loss = avg_loss
            model.save(save_path)

    print(f"\nBest loss: {best_loss:.6f}")
    print(f"Model saved to {save_path}")

    return history


def export_onnx(model_path: str, output_path: str) -> None:
    """
    Export PyTorch model to ONNX format.

    Args:
        model_path: Path to PyTorch model.
        output_path: Path for ONNX output.
    """
    try:
        import torch
        from models.hand_motion_model import HandMotionModelTorch
    except ImportError:
        print("PyTorch not available. Cannot export ONNX.")
        return

    print(f"\nExporting model to ONNX: {output_path}")

    model = HandMotionModelTorch()
    model.load_state_dict(torch.load(model_path, map_location='cpu', weights_only=True))
    model.eval()

    # Dummy input
    dummy_input = torch.randn(1, 1, INPUT_DIM)

    try:
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=11,
            input_names=['input'],
            output_names=['output', 'hidden'],
            dynamic_axes={
                'input': {0: 'batch_size', 1: 'sequence'},
                'output': {0: 'batch_size', 1: 'sequence'}
            }
        )
        print(f"ONNX model exported to {output_path}")
    except Exception as e:
        print(f"ONNX export failed: {e}")


def main() -> None:
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train NOVA-AI Hand Motion Model")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS, help="Number of epochs")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size")
    parser.add_argument("--lr", type=float, default=DEFAULT_LR, help="Learning rate")
    parser.add_argument("--samples", type=int, default=1000, help="Number of training samples")
    parser.add_argument("--save-numpy", action="store_true", help="Also train numpy model")
    parser.add_argument("--export-onnx", action="store_true", help="Export to ONNX format")
    args = parser.parse_args()

    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)

    # Generate synthetic data
    inputs, targets = generate_dataset(num_samples=args.samples)

    # Train PyTorch model
    try:
        import torch  # noqa: F401
        train_pytorch_model(
            inputs, targets,
            epochs=args.epochs,
            batch_size=args.batch_size,
            learning_rate=args.lr
        )

        if args.export_onnx:
            export_onnx(
                "models/hand_motion_model.pth",
                "models/hand_motion_model.onnx"
            )
    except ImportError:
        print("PyTorch not available. Only numpy model will be trained.")
        args.save_numpy = True

    # Train numpy fallback model
    if args.save_numpy:
        train_numpy_model(
            inputs, targets,
            epochs=min(args.epochs, 50),  # Fewer epochs for numpy
            learning_rate=args.lr * 0.1
        )

    print("\nTraining Complete")


if __name__ == "__main__":
    main()
