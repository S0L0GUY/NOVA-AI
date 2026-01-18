"""
Voice Detection and Transcription System
Provides real-time voice detection and transcription using WebRTC VAD
and faster-whisper for offline transcription.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import sounddevice as sd
import soundfile as sf
from scipy.signal import resample

import webrtcvad
import speech_recognition as sr
from faster_whisper import WhisperModel

import constants as constant

logger = logging.getLogger(__name__)


class VoiceDetector:
    """
    Detects voice activity using WebRTC VAD (Voice Activity Detection).
    """

    def __init__(self, sample_rate: int = 16000, frame_duration_ms: int = 20, aggressiveness: int = 2):
        """
        Initialize the voice detector.

        Args:
            sample_rate (int): Sample rate in Hz (16000 or 8000)
            frame_duration_ms (int): Frame duration in milliseconds (10, 20, or 30)
            aggressiveness (int): VAD aggressiveness (0-3, higher = more aggressive)
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.vad = webrtcvad.Vad(aggressiveness)
        self.frame_size = int(sample_rate * frame_duration_ms / 1000)
        logger.info("Voice detector initialized: sample_rate=%s, frame_duration=%sms", sample_rate, frame_duration_ms)

    def is_speech(self, audio_data: np.ndarray) -> bool:
        """
        Detect if audio contains speech.

        Args:
            audio_data (np.ndarray): Audio data as float array

        Returns:
            bool: True if speech is detected, False otherwise
        """
        try:
            # Convert float32 to int16 for VAD
            if audio_data.dtype == np.float32:
                audio_int16 = (audio_data * 32767).astype(np.int16)
            else:
                audio_int16 = audio_data.astype(np.int16)

            # Pad if necessary
            if len(audio_int16) < self.frame_size:
                audio_int16 = np.pad(audio_int16, (0, self.frame_size - len(audio_int16)))

            # Check for speech
            return self.vad.is_speech(audio_int16[:self.frame_size].tobytes(), self.sample_rate)
        except Exception as e:
            logger.error("Voice detection error: %s", e)
            return False


class WhisperTranscriber:
    """
    A comprehensive voice transcription system with voice detection.
    Uses faster-whisper for efficient offline transcription and WebRTC VAD
    for voice activity detection.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "auto",
        language: str = "en",
        sample_rate: int = 16000,
        input_device_index: Optional[int] = None,
        silence_timeout: float = 2.0,
        min_speech_duration: float = 0.3
    ):
        """
        Initialize the WhisperTranscriber.

        Args:
            model_size (str): Whisper model size ('tiny', 'base', 'small', 'medium', 'large')
            device (str): Device to use ('auto', 'cuda', 'cpu')
            language (str): Language code (default: 'en' for English)
            sample_rate (int): Sample rate in Hz (default: 16000)
            input_device_index (int, optional): Audio input device index
            silence_timeout (float): Seconds of silence to end recording
            min_speech_duration (float): Minimum speech duration to process
        """
        self.model_size = model_size
        self.device = device
        self.language = language
        self.sample_rate = sample_rate
        self.input_device_index = input_device_index or constant.Audio.AUDIO_INPUT_INDEX
        self.silence_timeout = silence_timeout
        self.min_speech_duration = min_speech_duration

        # Initialize models
        logger.info("Loading Whisper model '%s'...", model_size)
        try:
            self.model = WhisperModel(model_size, device=device, compute_type="float32")
        except Exception as e:
            logger.error("Failed to load Whisper model: %s", e)
            self.model = None

        self.voice_detector = VoiceDetector(sample_rate=self.sample_rate, aggressiveness=2)
        self.recognizer = sr.Recognizer()

        # Recording state
        self.is_recording = False
        self.audio_buffer = []

        logger.info("WhisperTranscriber initialized successfully")

    def detect_voice_and_record(self, max_duration: float = 30.0) -> Optional[np.ndarray]:
        """
        Detect voice activity and record audio until silence is detected.

        Args:
            max_duration (float): Maximum recording duration in seconds

        Returns:
            np.ndarray: Recorded audio data, or None if no speech detected
        """
        logger.info("Waiting for voice activity...")
        print("\033[94m[LISTENING]\033[0m Waiting for speech...")

        try:
            with sd.InputStream(
                device=self.input_device_index,
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.sample_rate // 100  # 10ms blocks
            ) as stream:
                audio_data = []
                silence_frames = 0
                speech_detected = False
                max_frames = int(max_duration * self.sample_rate / (self.sample_rate // 100))
                silence_frames_threshold = int(self.silence_timeout * 100)

                while len(audio_data) < max_frames:
                    chunk, _ = stream.read(self.sample_rate // 100)
                    audio_data.append(chunk)

                    # Detect speech
                    has_speech = self.voice_detector.is_speech(chunk.flatten())

                    if has_speech:
                        speech_detected = True
                        silence_frames = 0
                        print("\033[92m●\033[0m", end="", flush=True)
                    else:
                        if speech_detected:
                            silence_frames += 1
                            print("\033[90m○\033[0m", end="", flush=True)

                            # End recording after sustained silence
                            if silence_frames > silence_frames_threshold:
                                print("\n\033[94m[LISTENING]\033[0m Recording complete")
                                break

                if not speech_detected:
                    logger.warning("No speech detected")
                    print("\n\033[93m[WARNING]\033[0m No speech detected")
                    return None

                # Combine audio data
                audio_array = np.concatenate(audio_data)
                logger.info("Recorded %.2f seconds of audio", len(audio_array) / self.sample_rate)
                return audio_array

        except Exception as e:
            logger.error("Error during voice detection and recording: %s", e)
            print(f"\033[91m[ERROR]\033[0m Recording failed: {e}")
            return None

    def transcribe_audio(self, audio_data: np.ndarray) -> Dict[str, Any]:
        """
        Transcribe audio data using Whisper.

        Args:
            audio_data (np.ndarray): Audio data as numpy array

        Returns:
            Dict[str, Any]: Transcription result with metadata
        """
        if self.model is None:
            return {
                "success": False,
                "text": None,
                "error": "Whisper model not loaded",
                "language": None,
                "duration": None
            }

        try:
            # Save to temporary file
            temp_file = Path("/tmp/audio_temp.wav")
            temp_file.parent.mkdir(parents=True, exist_ok=True)

            # Normalize audio
            if audio_data.dtype == np.float32:
                audio_norm = np.clip(audio_data, -1.0, 1.0)
            else:
                audio_norm = (audio_data / np.max(np.abs(audio_data))).astype(np.float32)

            sf.write(str(temp_file), audio_norm, self.sample_rate)

            # Transcribe
            logger.info("Transcribing audio...")
            segments, info = self.model.transcribe(str(temp_file), language=self.language)

            # Extract text
            text = "".join([segment.text for segment in segments]).strip()

            # Clean up
            temp_file.unlink()

            if not text:
                return {
                    "success": False,
                    "text": None,
                    "error": "No speech recognized",
                    "language": info.language,
                    "duration": len(audio_data) / self.sample_rate
                }

            logger.info("Transcription: %s", text)
            return {
                "success": True,
                "text": text,
                "error": None,
                "language": info.language,
                "duration": len(audio_data) / self.sample_rate
            }

        except Exception as e:
            logger.error("Transcription error: %s", e)
            return {
                "success": False,
                "text": None,
                "error": str(e),
                "language": None,
                "duration": None
            }

    def record_and_transcribe(self, max_duration: float = 30.0) -> Dict[str, Any]:
        """
        Record audio with voice detection and transcribe it.

        Args:
            max_duration (float): Maximum recording duration in seconds

        Returns:
            Dict[str, Any]: Transcription result with metadata
        """
        # Step 1: Detect voice and record
        audio_data = self.detect_voice_and_record(max_duration)

        if audio_data is None:
            return {
                "success": False,
                "text": None,
                "error": "No audio recorded",
                "language": None,
                "duration": None
            }

        # Step 2: Transcribe
        return self.transcribe_audio(audio_data)

    def transcribe_file(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe an audio file.

        Args:
            audio_file_path (str): Path to the audio file

        Returns:
            Dict[str, Any]: Transcription result with metadata
        """
        try:
            file_path = Path(audio_file_path)
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_file_path}",
                    "text": None,
                    "language": None,
                    "duration": None
                }

            # Load audio file
            audio_data, sr_file = sf.read(str(file_path))

            # Resample if necessary
            if sr_file != self.sample_rate:
                num_samples = int(len(audio_data) * self.sample_rate / sr_file)
                audio_data = resample(audio_data, num_samples)

            return self.transcribe_audio(audio_data)

        except Exception as e:
            logger.error("File transcription error: %s", e)
            return {
                "success": False,
                "text": None,
                "error": str(e),
                "language": None,
                "duration": None
            }

    def set_language(self, language_code: str):
        """
        Set the transcription language.

        Args:
            language_code (str): Language code (e.g., 'en', 'es', 'fr')
        """
        self.language = language_code
        logger.info("Language set to: %s", language_code)

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages.

        Returns:
            list: List of language codes
        """
        return [
            "en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh", "ja",
            "ko", "ar", "hi", "th", "vi", "tr", "pl", "uk", "sv", "da"
        ]
