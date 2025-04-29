import whisper
import sounddevice as sd
import numpy as np
import torch
import webrtcvad
import collections
import constants as constant


class WhisperTranscriber:
    def __init__(self):
        print("\033[95mLoading Whisper model...\033[0m")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            # Initialize Whisper with the correct model path
            self.model = whisper.load_model(
                "base",
                device=self.device,
            )
            print(f"\033[35mWhisper model loaded on {self.device}.\033[0m")
        except Exception as e:
            print(f"\033[38;5;55mFailed to load Whisper model: {e}\033[0m")
            raise
        self.vad = webrtcvad.Vad(2)  # Aggressiveness from 0 to 3
        self.stream = None

        self.audio_input_index = constant.Audio.AUDIO_INPUT_INDEX

    def get_voice_input(self):
        print("\033[38;5;55mListening for voice input with VAD...\033[0m")
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
                        print("\033[38;5;55mAudio buffer overflowed\033[0m")

                    # Ensure audio data is in 16-bit PCM format
                    audio_data = data.flatten().astype(np.int16).tobytes()
                    is_speech = self.vad.is_speech(audio_data, sample_rate)
                    if not triggered:
                        ring_buffer.append((data.tobytes(), is_speech))
                        num_voiced = len(
                            [frame for frame, speech in ring_buffer if speech]
                        )

                        if num_voiced > threshold * num_padding_frames:
                            triggered = True
                            voiced_frames.extend(
                                [frame for frame, _ in ring_buffer]
                            )
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
                        print(
                            (
                                "\033[38;5;55mMax recording duration reached."
                                "\033[0m"
                            )
                        )
                        break

        except Exception as e:
            print(f"\033[38;5;55mError during voice input: {e}\033[0m")
            return None

        if not voiced_frames:
            print("\033[38;5;55mNo speech detected.\033[0m")
            return None

        audio_data = b"".join(voiced_frames)
        audio_array = (
            np.frombuffer(audio_data, dtype="int16")
              .astype(np.float32) / 32768.0
        )

        print("\033[38;5;55mTranscribing voice input...\033[0m")
        try:
            result = self.model.transcribe(
                audio_array, fp16=torch.cuda.is_available()
            )
            text = result["text"].strip()
            return text
        except Exception as e:
            print(f"\033[38;5;92mError during transcription: {e}\033[0m")
            return None
