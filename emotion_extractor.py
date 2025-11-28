"""
Emotion Extractor Module for NOVA-AI Hand Motion System.

This module derives emotional embedding vectors from text input to drive
naturalistic hand gestures. It provides both rule-based and neural network
approaches for emotion detection.

Integration point: Called by HandsController.on_nova_response() to extract
emotional features from NOVA's text responses.
"""

import re
from typing import Optional

import numpy as np

# Emotion vector indices: [calm, happy, sad, angry, sarcastic, neutral]
EMOTION_DIM = 6
EMOTION_LABELS = ["calm", "happy", "sad", "angry", "sarcastic", "neutral"]

# Keywords for rule-based emotion detection
HAPPY_KEYWORDS = [
    "happy", "joy", "excited", "great", "wonderful", "amazing", "awesome",
    "love", "fantastic", "excellent", "yay", "haha", "lol", "fun", "glad",
    "delighted", "thrilled", "pleased", "cheerful", "smile", "laugh"
]

SAD_KEYWORDS = [
    "sad", "sorry", "unfortunately", "miss", "lost", "cry", "tear",
    "depressed", "down", "unhappy", "regret", "sorrow", "grief", "lonely",
    "disappointed", "heartbroken", "melancholy"
]

ANGRY_KEYWORDS = [
    "angry", "mad", "furious", "annoyed", "frustrated", "hate", "damn",
    "ugh", "irritated", "rage", "outraged", "hostile", "bitter", "upset"
]

CALM_KEYWORDS = [
    "calm", "peaceful", "relaxed", "serene", "quiet", "gentle", "soft",
    "tranquil", "soothing", "mellow", "easy", "steady", "composed"
]

SARCASTIC_KEYWORDS = [
    "sure", "right", "whatever", "obviously", "clearly", "totally",
    "yeah right", "oh really", "wow", "brilliant", "genius"
]


class EmotionExtractor:
    """
    Extracts emotional embedding vectors from text input.

    Provides both rule-based heuristics and optional neural network classifier
    for emotion detection. The output is a normalized 6-dimensional vector
    representing emotion intensities.

    Attributes:
        model: Optional neural network model for emotion classification.
        use_nn: Whether to use neural network classification.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        """
        Initialize the EmotionExtractor.

        Args:
            model_path: Optional path to a trained emotion classifier model.
                       If None, uses rule-based extraction only.
        """
        self.model = None
        self.use_nn = False

        if model_path is not None:
            self._load_model(model_path)

    def _load_model(self, model_path: str) -> None:
        """
        Load a neural network model for emotion classification.

        Args:
            model_path: Path to the model file (.pth or .npz).
        """
        try:
            # Try PyTorch first
            import torch
            if model_path.endswith('.pth'):
                self.model = torch.load(model_path, map_location='cpu', weights_only=False)
                self.model.eval()
                self.use_nn = True
                return
        except (ImportError, FileNotFoundError, RuntimeError):
            pass

        try:
            # Try numpy fallback
            if model_path.endswith('.npz'):
                data = np.load(model_path)
                self.model = {
                    'weights': data['weights'],
                    'bias': data['bias']
                }
                self.use_nn = True
        except (FileNotFoundError, KeyError):
            self.use_nn = False

    def extract(self, text: str) -> np.ndarray:
        """
        Extract emotion vector from text.

        Args:
            text: Input text string to analyze.

        Returns:
            np.ndarray: Normalized emotion vector of shape (6,) with values
                       representing [calm, happy, sad, angry, sarcastic, neutral].
        """
        if self.use_nn and self.model is not None:
            return self._extract_nn(text)
        return self._extract_rules(text)

    def _extract_rules(self, text: str) -> np.ndarray:
        """
        Extract emotions using rule-based heuristics.

        Uses keyword matching, punctuation analysis, and capitalization
        patterns to determine emotional content.

        Args:
            text: Input text to analyze.

        Returns:
            np.ndarray: Normalized emotion vector.
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        # Initialize scores
        scores = np.zeros(EMOTION_DIM, dtype=np.float32)

        # Count keyword matches
        for word in words:
            if word in CALM_KEYWORDS:
                scores[0] += 1.0
            if word in HAPPY_KEYWORDS:
                scores[1] += 1.0
            if word in SAD_KEYWORDS:
                scores[2] += 1.0
            if word in ANGRY_KEYWORDS:
                scores[3] += 1.0
            if word in SARCASTIC_KEYWORDS:
                scores[4] += 1.0

        # Analyze punctuation patterns
        exclamation_count = text.count('!')
        question_count = text.count('?')
        ellipsis_count = text.count('...')

        # Exclamations suggest excitement or anger
        if exclamation_count > 0:
            scores[1] += exclamation_count * 0.3  # happy/excited
            scores[3] += exclamation_count * 0.2  # angry (if caps)

        # Questions can indicate various emotions
        if question_count > 1:
            scores[4] += 0.2  # slight sarcasm for multiple questions

        # Ellipsis often indicates hesitation/sadness
        if ellipsis_count > 0:
            scores[2] += ellipsis_count * 0.3

        # ALL CAPS detection suggests strong emotion
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            scores[3] += caps_ratio * 2.0  # angry
            scores[1] += caps_ratio * 0.5  # excited

        # Check for sarcasm patterns (quotes, certain phrases)
        if '"' in text or "'" in text:
            scores[4] += 0.2

        # Detect mixed signals that might indicate sarcasm
        if scores[1] > 0 and scores[3] > 0:
            scores[4] += 0.3

        # If no strong signals, default to neutral
        if np.sum(scores) < 0.5:
            scores[5] = 1.0

        # Normalize to sum to 1
        total = np.sum(scores)
        if total > 0:
            scores = scores / total

        return scores.astype(np.float32)

    def _extract_nn(self, text: str) -> np.ndarray:
        """
        Extract emotions using neural network model.

        Args:
            text: Input text to analyze.

        Returns:
            np.ndarray: Normalized emotion vector.
        """
        # Create simple bag-of-words features
        features = self._text_to_features(text)

        try:
            # PyTorch model
            import torch
            if hasattr(self.model, 'forward'):
                with torch.no_grad():
                    input_tensor = torch.tensor(features, dtype=torch.float32).unsqueeze(0)
                    output = self.model(input_tensor)
                    output = torch.softmax(output, dim=1)
                    return output.squeeze().numpy()
        except (ImportError, AttributeError):
            pass

        # Numpy fallback model
        if isinstance(self.model, dict):
            logits = np.dot(features, self.model['weights']) + self.model['bias']
            # Softmax
            exp_logits = np.exp(logits - np.max(logits))
            return (exp_logits / np.sum(exp_logits)).astype(np.float32)

        # Fallback to rules if model failed
        return self._extract_rules(text)

    def _text_to_features(self, text: str) -> np.ndarray:
        """
        Convert text to feature vector for neural network.

        Creates a simple feature vector based on keyword counts and
        text statistics.

        Args:
            text: Input text.

        Returns:
            np.ndarray: Feature vector.
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)

        # Feature vector: keyword counts + statistics
        features = np.zeros(32, dtype=np.float32)

        # Keyword counts (normalized by length)
        word_count = max(len(words), 1)
        features[0] = sum(1 for w in words if w in CALM_KEYWORDS) / word_count
        features[1] = sum(1 for w in words if w in HAPPY_KEYWORDS) / word_count
        features[2] = sum(1 for w in words if w in SAD_KEYWORDS) / word_count
        features[3] = sum(1 for w in words if w in ANGRY_KEYWORDS) / word_count
        features[4] = sum(1 for w in words if w in SARCASTIC_KEYWORDS) / word_count

        # Punctuation features
        features[5] = text.count('!') / max(len(text), 1)
        features[6] = text.count('?') / max(len(text), 1)
        features[7] = text.count('...') / max(len(text), 1)

        # Capitalization
        features[8] = sum(1 for c in text if c.isupper()) / max(len(text), 1)

        # Text length features
        features[9] = min(len(words) / 50.0, 1.0)
        features[10] = min(len(text) / 200.0, 1.0)

        return features

    def get_emotion_name(self, emotion_vec: np.ndarray) -> str:
        """
        Get the dominant emotion name from an emotion vector.

        Args:
            emotion_vec: Emotion vector of shape (6,).

        Returns:
            str: Name of the dominant emotion.
        """
        idx = int(np.argmax(emotion_vec))
        return EMOTION_LABELS[idx]

    def get_emotion_intensity(self, emotion_vec: np.ndarray) -> float:
        """
        Get the intensity of the dominant emotion.

        Args:
            emotion_vec: Emotion vector of shape (6,).

        Returns:
            float: Intensity value (0-1) of the dominant emotion.
        """
        return float(np.max(emotion_vec))
