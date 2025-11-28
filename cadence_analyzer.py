"""
Cadence Analyzer Module for NOVA-AI Hand Motion System.

This module extracts timing and cadence features from text and TTS planning
metadata to synchronize hand gestures with speech.

Integration point: Called by HandsController.on_nova_response() to extract
speech rhythm information for gesture timing.
"""

import re
from typing import Any


class CadenceAnalyzer:
    """
    Analyzes text and TTS timing to extract cadence features for gesture sync.

    Provides both text-based heuristic analysis and higher-accuracy analysis
    when TTS timing metadata is available.

    Attributes:
        average_word_duration: Default estimated duration per word in seconds.
        average_words_per_second: Default speech rate (words per second).
    """

    # Average speaking rates
    SLOW_WPS = 2.0  # Words per second for slow speech
    NORMAL_WPS = 3.0  # Words per second for normal speech
    FAST_WPS = 4.5  # Words per second for fast speech

    # Pause durations
    COMMA_PAUSE = 0.3
    PERIOD_PAUSE = 0.6
    ELLIPSIS_PAUSE = 1.0
    EXCLAMATION_PAUSE = 0.5
    QUESTION_PAUSE = 0.5

    def __init__(self) -> None:
        """Initialize the CadenceAnalyzer."""
        self.average_word_duration = 1.0 / self.NORMAL_WPS
        self.average_words_per_second = self.NORMAL_WPS

    def analyze_text(self, text: str) -> dict[str, Any]:
        """
        Analyze text to extract cadence features using heuristics.

        Estimates speech rate, pause patterns, and timing from text content
        without requiring TTS metadata.

        Args:
            text: Input text to analyze.

        Returns:
            dict: Dictionary containing:
                - speech_rate: Normalized speech rate (0-1)
                - pause_penalty: Ratio of pauses to total time (0-1)
                - word_timestamps: List of estimated word timing dicts
                - estimated_duration: Total estimated duration in seconds
                - word_count: Number of words
                - emphasis_indices: List of word indices that should be emphasized
        """
        # Extract words and punctuation
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)

        if word_count == 0:
            return {
                'speech_rate': 0.5,
                'pause_penalty': 0.0,
                'word_timestamps': [],
                'estimated_duration': 0.0,
                'word_count': 0,
                'emphasis_indices': []
            }

        # Estimate speech rate based on text characteristics
        speech_rate = self._estimate_speech_rate(text, words)

        # Calculate pauses from punctuation
        pause_times = self._calculate_pauses(text)
        total_pause_time = sum(pause_times)

        # Calculate word timing
        word_duration = 1.0 / (speech_rate * self.FAST_WPS + (1 - speech_rate) * self.SLOW_WPS)
        speech_time = word_count * word_duration
        total_duration = speech_time + total_pause_time

        # Calculate pause penalty
        pause_penalty = total_pause_time / max(total_duration, 0.1)
        pause_penalty = min(pause_penalty, 1.0)

        # Generate word timestamps
        word_timestamps = self._generate_word_timestamps(text, words, word_duration)

        # Find emphasis points
        emphasis_indices = self._find_emphasis_indices(text, words)

        return {
            'speech_rate': speech_rate,
            'pause_penalty': pause_penalty,
            'word_timestamps': word_timestamps,
            'estimated_duration': total_duration,
            'word_count': word_count,
            'emphasis_indices': emphasis_indices
        }

    def analyze_tts_plan(self, tts_timing: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze TTS timing metadata for high-accuracy cadence features.

        Uses actual TTS planning data when available for precise
        synchronization.

        Args:
            tts_timing: Dictionary containing TTS timing information:
                - duration: Total duration in seconds
                - word_timestamps: List of {word, start, end} dicts (optional)
                - phoneme_timestamps: List of phoneme timing (optional)

        Returns:
            dict: Dictionary containing:
                - speech_rate: Normalized speech rate (0-1)
                - pause_penalty: Ratio of pauses to total time (0-1)
                - word_timestamps: List of word timing dicts
                - estimated_duration: Total duration in seconds
                - word_count: Number of words
                - emphasis_indices: List of emphasis word indices
        """
        duration = tts_timing.get('duration', 0.0)
        word_timestamps = tts_timing.get('word_timestamps', [])

        if not word_timestamps:
            # No detailed timing, estimate from duration
            text = tts_timing.get('text', '')
            if text:
                result = self.analyze_text(text)
                if duration > 0:
                    # Scale to actual duration
                    scale = duration / max(result['estimated_duration'], 0.1)
                    for wt in result['word_timestamps']:
                        wt['start'] *= scale
                        wt['end'] *= scale
                    result['estimated_duration'] = duration
                return result
            return {
                'speech_rate': 0.5,
                'pause_penalty': 0.0,
                'word_timestamps': [],
                'estimated_duration': duration,
                'word_count': 0,
                'emphasis_indices': []
            }

        word_count = len(word_timestamps)

        # Calculate speech rate from actual timing
        if duration > 0 and word_count > 0:
            actual_wps = word_count / duration
            # Normalize to 0-1 range (SLOW_WPS to FAST_WPS)
            speech_rate = (actual_wps - self.SLOW_WPS) / (self.FAST_WPS - self.SLOW_WPS)
            speech_rate = max(0.0, min(1.0, speech_rate))
        else:
            speech_rate = 0.5

        # Calculate pause penalty from gaps between words
        total_gap_time = 0.0
        for i in range(1, len(word_timestamps)):
            prev_end = word_timestamps[i - 1].get('end', 0.0)
            curr_start = word_timestamps[i].get('start', 0.0)
            gap = curr_start - prev_end
            if gap > 0.1:  # Only count significant gaps
                total_gap_time += gap

        pause_penalty = total_gap_time / max(duration, 0.1)
        pause_penalty = min(pause_penalty, 1.0)

        # Find emphasis from timing patterns (longer words, longer pauses before)
        emphasis_indices = []
        for i, wt in enumerate(word_timestamps):
            word_duration = wt.get('end', 0.0) - wt.get('start', 0.0)
            avg_duration = duration / max(word_count, 1)
            if word_duration > avg_duration * 1.3:
                emphasis_indices.append(i)

        return {
            'speech_rate': speech_rate,
            'pause_penalty': pause_penalty,
            'word_timestamps': word_timestamps,
            'estimated_duration': duration,
            'word_count': word_count,
            'emphasis_indices': emphasis_indices
        }

    def _estimate_speech_rate(self, text: str, words: list[str]) -> float:
        """
        Estimate normalized speech rate from text characteristics.

        Args:
            text: Original text.
            words: List of words extracted from text.

        Returns:
            float: Normalized speech rate (0-1).
        """
        # Base rate
        rate = 0.5

        # Shorter sentences tend to be faster
        avg_word_length = sum(len(w) for w in words) / max(len(words), 1)
        if avg_word_length < 4:
            rate += 0.1
        elif avg_word_length > 6:
            rate -= 0.1

        # Exclamations suggest faster, more energetic speech
        if text.count('!') > 0:
            rate += 0.15

        # Ellipsis suggests slower speech
        if '...' in text:
            rate -= 0.2

        # Multiple commas suggest more measured pace
        if text.count(',') > 3:
            rate -= 0.1

        # ALL CAPS suggests faster, louder
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.3:
            rate += 0.2

        return max(0.0, min(1.0, rate))

    def _calculate_pauses(self, text: str) -> list[float]:
        """
        Calculate pause durations from punctuation.

        Args:
            text: Input text.

        Returns:
            list: List of pause durations in seconds.
        """
        pauses = []

        # Count different punctuation types
        for char in text:
            if char == ',':
                pauses.append(self.COMMA_PAUSE)
            elif char == '.':
                pauses.append(self.PERIOD_PAUSE)
            elif char == '!':
                pauses.append(self.EXCLAMATION_PAUSE)
            elif char == '?':
                pauses.append(self.QUESTION_PAUSE)

        # Handle ellipsis separately (overrides individual periods)
        ellipsis_count = text.count('...')
        if ellipsis_count > 0:
            # Remove the period pauses for ellipsis
            pauses = [p for p in pauses if p != self.PERIOD_PAUSE]
            for _ in range(ellipsis_count):
                pauses.append(self.ELLIPSIS_PAUSE)

        return pauses

    def _generate_word_timestamps(
        self, text: str, words: list[str], word_duration: float
    ) -> list[dict[str, Any]]:
        """
        Generate estimated word timestamps.

        Args:
            text: Original text.
            words: List of words.
            word_duration: Average duration per word in seconds.

        Returns:
            list: List of timestamp dictionaries with word, start, end.
        """
        timestamps = []
        current_time = 0.0

        # Find word positions in original text for punctuation context
        remaining_text = text
        for word in words:
            # Add pause if punctuation precedes this word position
            word_idx = remaining_text.find(word)
            if word_idx >= 0:
                prefix = remaining_text[:word_idx]
                for char in prefix:
                    if char == ',':
                        current_time += self.COMMA_PAUSE
                    elif char == '.':
                        current_time += self.PERIOD_PAUSE
                    elif char in '!?':
                        current_time += self.EXCLAMATION_PAUSE
                remaining_text = remaining_text[word_idx + len(word):]

            start_time = current_time
            end_time = current_time + word_duration

            timestamps.append({
                'word': word,
                'start': round(start_time, 3),
                'end': round(end_time, 3)
            })

            current_time = end_time

        return timestamps

    def _find_emphasis_indices(self, text: str, words: list[str]) -> list[int]:
        """
        Find word indices that should receive emphasis.

        Args:
            text: Original text.
            words: List of words.

        Returns:
            list: List of word indices for emphasis.
        """
        emphasis = []

        for i, word in enumerate(words):
            # ALL CAPS words get emphasis
            if word.isupper() and len(word) > 1:
                emphasis.append(i)
                continue

            # Words followed by exclamation
            word_idx = text.find(word)
            if word_idx >= 0:
                after = text[word_idx + len(word):word_idx + len(word) + 2]
                if '!' in after:
                    emphasis.append(i)

        return emphasis

    def get_current_word_at_time(
        self, timestamps: list[dict[str, Any]], time: float
    ) -> dict[str, Any] | None:
        """
        Get the word being spoken at a given time.

        Args:
            timestamps: List of word timestamp dictionaries.
            time: Current time in seconds.

        Returns:
            dict: Word timestamp dict if found, None otherwise.
        """
        for wt in timestamps:
            if wt['start'] <= time <= wt['end']:
                return wt
        return None

    def is_pause_at_time(
        self, timestamps: list[dict[str, Any]], time: float
    ) -> bool:
        """
        Check if there's a pause (no word) at the given time.

        Args:
            timestamps: List of word timestamp dictionaries.
            time: Current time in seconds.

        Returns:
            bool: True if in a pause between words.
        """
        if not timestamps:
            return True

        # Check if before first word
        if time < timestamps[0]['start']:
            return True

        # Check if after last word
        if time > timestamps[-1]['end']:
            return True

        # Check if between words
        for i in range(len(timestamps) - 1):
            if timestamps[i]['end'] < time < timestamps[i + 1]['start']:
                return True

        return False
