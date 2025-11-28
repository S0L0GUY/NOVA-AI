# NOVA-AI Hand Motion System

Neural-network-driven procedural hand motion for VRChat avatars via OSC.

## Overview

This subsystem adds continuous, naturalistic hand and finger gestures to NOVA-AI, synchronized with speech output. It runs asynchronously and never blocks the main audio or LLM processing.

### Features

- **Speech-synchronized gestures**: Hand movements correlate with emotional tone, speech rate, and emphasis
- **Neural network model**: Tiny GRU-based model for natural motion generation
- **Procedural fallback**: Perlin noise-based generator when model unavailable
- **Real-time OSC output**: Configurable frame rate (default 30 FPS)
- **Smooth transitions**: Exponential smoothing prevents jitter
- **Idle micro-movements**: Subtle motion when not speaking
- **CPU-only**: No GPU required, minimal computational overhead

## Installation

### Requirements

The hand motion system uses packages already in NOVA-AI's requirements:

```bash
# Core dependencies (already in requirements.txt)
pip install python-osc numpy torch
```

Optional for training:
```bash
pip install scipy  # For noise generation in training
```

### Files

```
hands_controller.py      # Main controller module
emotion_extractor.py     # Text emotion analysis
cadence_analyzer.py      # Speech timing analysis
hand_mapper.py           # OSC parameter mapping
models/
  hand_motion_model.py   # Neural network model
train_hand_model.py      # Model training script
test_hands_output.py     # Test harness
hands_config.json        # Configuration
README_HANDS.md          # This file
```

## Quick Start

### Basic Usage

```python
import asyncio
from hands_controller import HandsController

async def main():
    # Initialize controller
    hands = HandsController()
    
    # Start the OSC update loop
    await hands.start()
    
    # Trigger gestures when NOVA speaks
    await hands.on_nova_response(
        text="Hello! How are you today?",
        tts_timing={'duration': 2.0}
    )
    
    # Keep running...
    await asyncio.sleep(10)
    
    # Clean shutdown
    await hands.stop()

asyncio.run(main())
```

### Integration with NOVA

In your NOVA main loop, call `on_nova_response()` when the AI generates text:

```python
# In nova.py or where TTS is triggered
from hands_controller import HandsController

# Initialize once
hands_controller = HandsController()
await hands_controller.start()

# When AI responds:
async def process_ai_response(text: str, tts_timing: dict = None):
    # Trigger hand gestures
    await hands_controller.on_nova_response(text, tts_timing)
    
    # Continue with TTS...
    tts.add_to_queue(text)
```

## Configuration

### hands_config.json

```json
{
  "vrchat": {
    "address": "127.0.0.1",
    "port": 9000
  },
  "osc_rate": 30,
  "smoothing_alpha": 0.6,
  "model_path": "models/hand_motion_model.pth",
  "use_torch": true,
  "use_procedural_fallback": true,
  "max_hand_offset": {
    "x": 0.35,
    "y": 0.35,
    "z": 0.35
  },
  "finger_curl_range": [0.0, 1.0],
  "gesture_energy_multiplier": 1.0,
  "log_level": "INFO",
  "idle_energy_threshold": 0.1,
  "silence_threshold_seconds": 2.0
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `vrchat.address` | string | "127.0.0.1" | VRChat OSC address |
| `vrchat.port` | int | 9000 | VRChat OSC port |
| `osc_rate` | int | 30 | OSC messages per second |
| `smoothing_alpha` | float | 0.6 | Smoothing factor (0-1, higher = more responsive) |
| `model_path` | string | "models/hand_motion_model.pth" | Path to trained model |
| `use_torch` | bool | true | Use PyTorch model if available |
| `use_procedural_fallback` | bool | true | Use procedural motion if model unavailable |
| `max_hand_offset` | object | {x: 0.35, y: 0.35, z: 0.35} | Maximum hand position offset |
| `finger_curl_range` | array | [0.0, 1.0] | Min/max finger curl values |
| `gesture_energy_multiplier` | float | 1.0 | Scale gesture intensity |
| `idle_energy_threshold` | float | 0.1 | Energy below which idle motion is used |
| `silence_threshold_seconds` | float | 2.0 | Time after speech to return to idle |

### Environment Variables

Override VRChat connection:
```bash
export VRCHAT_OSC_ADDRESS=192.168.1.100
export VRCHAT_OSC_PORT=9001
```

## Training the Model

Generate synthetic training data and train the neural network:

```bash
# Train with defaults
python train_hand_model.py

# Custom training
python train_hand_model.py --epochs 200 --batch-size 64 --samples 2000

# Also save numpy fallback model
python train_hand_model.py --save-numpy

# Export to ONNX
python train_hand_model.py --export-onnx
```

### Training Options

| Option | Default | Description |
|--------|---------|-------------|
| `--epochs` | 100 | Training epochs |
| `--batch-size` | 32 | Batch size |
| `--lr` | 0.001 | Learning rate |
| `--samples` | 1000 | Number of synthetic samples |
| `--save-numpy` | false | Also train numpy fallback |
| `--export-onnx` | false | Export ONNX model |

### Output Files

- `models/hand_motion_model.pth` - PyTorch model weights
- `models/hand_motion_model.npz` - Numpy fallback weights
- `models/hand_motion_model.onnx` - ONNX export (optional)

## Procedural Fallback

When the neural network model is unavailable, the system uses procedural generation:

- **Perlin noise**: Continuous natural variation for each joint
- **Bezier curves**: Smooth gesture envelopes (attack/sustain/release)
- **Emotion mapping**: Different gesture styles per emotion
- **Finger oscillators**: Independent micro-movement per finger

Enable/disable in config:
```json
{
  "use_procedural_fallback": true
}
```

## VRChat OSC Parameters

### Required Avatar Parameters

Add these float parameters to your VRChat avatar:

```
/avatar/parameters/LeftHandX      float (-1..1)  - Left hand X offset
/avatar/parameters/LeftHandY      float (-1..1)  - Left hand Y offset
/avatar/parameters/LeftHandZ      float (-1..1)  - Left hand Z offset
/avatar/parameters/LeftHandRotX   float (-1..1)  - Left hand pitch
/avatar/parameters/LeftHandRotY   float (-1..1)  - Left hand yaw
/avatar/parameters/LeftHandRotZ   float (-1..1)  - Left hand roll
/avatar/parameters/LeftFinger1    float (0..1)   - Left thumb curl
/avatar/parameters/LeftFinger2    float (0..1)   - Left index curl
/avatar/parameters/LeftFinger3    float (0..1)   - Left middle curl
/avatar/parameters/LeftFinger4    float (0..1)   - Left ring curl
/avatar/parameters/LeftFinger5    float (0..1)   - Left pinky curl

/avatar/parameters/RightHandX     float (-1..1)  - Right hand X offset
/avatar/parameters/RightHandY     float (-1..1)  - Right hand Y offset
/avatar/parameters/RightHandZ     float (-1..1)  - Right hand Z offset
/avatar/parameters/RightHandRotX  float (-1..1)  - Right hand pitch
/avatar/parameters/RightHandRotY  float (-1..1)  - Right hand yaw
/avatar/parameters/RightHandRotZ  float (-1..1)  - Right hand roll
/avatar/parameters/RightFinger1   float (0..1)   - Right thumb curl
/avatar/parameters/RightFinger2   float (0..1)   - Right index curl
/avatar/parameters/RightFinger3   float (0..1)   - Right middle curl
/avatar/parameters/RightFinger4   float (0..1)   - Right ring curl
/avatar/parameters/RightFinger5   float (0..1)   - Right pinky curl

/avatar/parameters/HandGestureEnergy float (0..1) - Overall gesture energy
```

### Custom Parameter Names

Override parameter paths in `hands_config.json`:

```json
{
  "osc_parameters": {
    "left_hand_x": "/avatar/parameters/MyLeftX",
    "left_finger_1": "/avatar/parameters/Thumb_L"
  }
}
```

## Testing

Run the test harness:

```bash
# Run all tests
python test_hands_output.py

# Extended simulation
python test_hands_output.py --duration 30

# Verbose OSC output
python test_hands_output.py --verbose
```

### Test Output

The test script:
1. Runs unit tests for all modules
2. Simulates NOVA responses with different emotions
3. Verifies OSC output values are within range
4. Tests timing accuracy of the update loop

## API Reference

### HandsController

```python
class HandsController:
    def __init__(self, config_path: str = "hands_config.json")
    
    async def start(self) -> None
        """Start OSC client and update loop."""
    
    async def stop(self) -> None
        """Stop update loop cleanly."""
    
    async def on_nova_response(
        self,
        text: str,
        tts_timing: dict | None = None
    ) -> None
        """
        Handle NOVA response.
        
        Args:
            text: Response text to speak
            tts_timing: Optional TTS metadata with 'duration' and 'word_timestamps'
        """
    
    def load_model(self, path: str | None) -> None
        """Load NN model or enable procedural fallback."""
    
    def set_energy_override(self, energy: float) -> None
        """Override gesture energy (negative to disable)."""
    
    def is_running(self) -> bool
        """Check if controller is active."""
    
    def get_current_energy(self) -> float
        """Get current gesture energy level."""
    
    def get_current_emotion(self) -> str
        """Get dominant emotion name."""
```

### EmotionExtractor

```python
class EmotionExtractor:
    def __init__(self, model_path: str | None = None)
    
    def extract(self, text: str) -> np.ndarray
        """
        Extract 6-dim emotion vector: 
        [calm, happy, sad, angry, sarcastic, neutral]
        """
    
    def get_emotion_name(self, emotion_vec: np.ndarray) -> str
        """Get dominant emotion name."""
```

### CadenceAnalyzer

```python
class CadenceAnalyzer:
    def analyze_text(self, text: str) -> dict
        """
        Analyze text cadence.
        
        Returns:
            {
                'speech_rate': float,      # 0-1 normalized
                'pause_penalty': float,    # 0-1 silence ratio
                'word_timestamps': [...],  # Estimated timing
                'estimated_duration': float,
                'word_count': int,
                'emphasis_indices': [...]
            }
        """
    
    def analyze_tts_plan(self, tts_timing: dict) -> dict
        """Analyze with actual TTS timing data."""
```

## Performance Notes

- **CPU only**: No GPU required
- **Model size**: ~200KB (PyTorch), ~50KB (numpy)
- **Frame time**: <1ms per frame on modern CPU
- **Memory**: ~10MB peak during operation
- **Update rate**: Stable 30 FPS default

## Troubleshooting

### No movement in VRChat

1. Check VRChat OSC is enabled (Settings > OSC)
2. Verify port matches config (default 9000)
3. Confirm avatar has required parameters
4. Check `log_level: DEBUG` for diagnostics

### Jittery movement

1. Increase `smoothing_alpha` (0.6 → 0.8)
2. Reduce `osc_rate` if CPU-limited
3. Check for network latency

### Model not loading

1. Train model first: `python train_hand_model.py`
2. Check path in config matches actual file
3. Enable `use_procedural_fallback: true`

### High CPU usage

1. Reduce `osc_rate` (30 → 20)
2. Use numpy model instead of PyTorch
3. Disable if not needed during heavy LLM processing

## License

Part of NOVA-AI project. See main LICENSE file.
