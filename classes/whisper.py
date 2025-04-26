import logging
import whisper
import sounddevice as sd
import numpy as np
import torch
import webrtcvad
import collections
import sys
import os
import constants as constant


class WhisperTranscriber:
    def __init__(self):
        logging.info("Loading Whisper model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            # Get the base directory for the application
            if getattr(sys, "frozen", False):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(
                    os.path.dirname(os.path.dirname(__file__))
                )

            # Initialize Whisper with the correct model path
            self.model = whisper.load_model(
                "base",
                device=self.device,
                download_root=os.path.join(base_path, "whisper", "assets"),
            )
            logging.info(f"Whisper model loaded on {self.device}.")
        except Exception as e:
            logging.error(f"Failed to load Whisper model: {e}")
            raise
        self.vad = webrtcvad.Vad(2)  # Aggressiveness from 0 to 3
        self.stream = None

        self.audio_input_index = constant.Audio.AUDIO_INPUT_INDEX

    def get_voice_input(self):
        logging.info("Listening for voice input with VAD...")
        sample_rate = 16000
        frame_duration = 30  # ms
        num_padding_frames = 10
        threshold = 0.9  # Ratio of voiced frames needed

        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False
        voiced_frames = []

        try:
            with sd.InputStream(
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
                device=self.audio_input_index,
                # Explicitly use default input device
                latency="low",
            ) as stream:
                while True:
                    data, overflowed = stream.read(
                        int(sample_rate * frame_duration / 1000)
                    )
                    if overflowed:
                        logging.warning("Audio buffer overflowed")

                    is_speech = self.vad.is_speech(data.tobytes(), sample_rate)
                    if not triggered:
                        ring_buffer.append((data.tobytes(), is_speech))
                        num_voiced = len(
                            [f for f, speech in ring_buffer if speech]
                        )
                        if num_voiced > threshold * num_padding_frames:
                            triggered = True
                            voiced_frames.extend([f for f, s in ring_buffer])
                            ring_buffer.clear()
                    else:
                        voiced_frames.append(data.tobytes())
                        ring_buffer.append((data.tobytes(), is_speech))
                        num_unvoiced = len(
                            [f for f, speech in ring_buffer if not speech]
                        )
                        if num_unvoiced > threshold * num_padding_frames:
                            break  # End of speech
                    if (
                        len(voiced_frames) > sample_rate * 10
                    ):  # Limit recording to 10 seconds
                        logging.info("Max recording duration reached.")
                        break

        except Exception as e:
            logging.error(f"Error during voice input: {e}")
            return None

        if not voiced_frames:
            logging.info("No speech detected.")
            return None

        audio_data = b"".join(voiced_frames)
        audio_array = (
            np.frombuffer(audio_data, dtype="int16")
              .astype(np.float32) / 32768.0
        )

        logging.info("Transcribing voice input...")
        try:
            result = self.model.transcribe(
                audio_array, fp16=torch.cuda.is_available()
            )
            text = result["text"].strip()
            logging.info(f"Transcribed text: {text}")
            return text
        except Exception as e:
            logging.error(f"Error during transcription: {e}")
            return None
