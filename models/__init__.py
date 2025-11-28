"""
Hand Motion Model Package for NOVA-AI.

This package contains the neural network model for generating naturalistic
hand motion parameters synchronized with speech.
"""

from .hand_motion_model import (
    HandMotionModel,
    HandMotionModelNumpy,
    is_torch_available,
    get_input_dim,
    get_output_dim,
    INPUT_DIM,
    OUTPUT_DIM,
)

__all__ = [
    'HandMotionModel',
    'HandMotionModelNumpy',
    'is_torch_available',
    'get_input_dim',
    'get_output_dim',
    'INPUT_DIM',
    'OUTPUT_DIM',
]
