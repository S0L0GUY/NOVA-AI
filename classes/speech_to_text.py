import collections
import io
import wave

import numpy as np
import sounddevice as sd
import torch
import webrtcvad
from faster_whisper import WhisperModel
from google import genai

import constants as constant


class SpeechToTextHandler:
    def __init__(self) -> None:
        """
        Initializes the Whisper class.
        This constructor sets up the Whisper model for speech recognition,
        configures the device (CPU or GPU) for processing, and initializes
        a WebRTC Voice Activity Detector (VAD) with a specified aggressiveness
        level.
        Attributes:
            device (str): The device to run the model on, either 'cuda' (GPU)
            or 'cpu'. model (whisper.Model): The Whisper model instance loaded
            for speech recognition. vad (webrtcvad.Vad): The WebRTC Voice
            Activity Detector instance. stream: Placeholder for the audio
            stream (not initialized in this constructor).
            audio_input_index: Index of the audio input device, retrieved from
            constants.
        Raises:
            Exception: If the Whisper model fails to load, an exception is
            raised with the error details.
        """

        print("\033[95mLoading Whisper model (faster-whisper)...\033[0m")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            # Initialize faster-whisper WhisperModel
            compute_type = "float16" if self.device == "cuda" else "float32"
            self.model = WhisperModel(
                constant.SpeechRecognitionConfig.MODEL_SIZE,
                device=self.device,
                compute_type=compute_type,
            )
            print(f"\033[35mFaster-Whisper model loaded on {self.device} (compute_type={compute_type}).\033[0m")
        except Exception as e:
            print(f"\033[38;5;55mFailed to load Faster-Whisper model: {e}\033[0m")
            raise
        self.genai = genai.Client(api_key=constant.LLM_API.API_KEY)
        self.prompt = "Generate a transcript of the speech."
        self.vad = webrtcvad.Vad(constant.SpeechRecognitionConfig.VAD_AGGRESSIVENESS)
        self.stream = None

        self.audio_input_index = constant.Audio.AUDIO_INPUT_INDEX

    def get_voice_input(self, osc) -> str:
        """
        Captures voice input using Voice Activity Detection (VAD) and
        transcribes it into text. This method listens for voice input through
        the specified audio input device, processes the audio data to detect
        speech using VAD, and transcribes the detected speech into text using
        a speech-to-text model.
        Returns:
            str: The transcribed text from the voice input if successful.
            None: If no speech is detected or an error occurs during
            processing.
        Raises:
            Exception: If an error occurs during audio input or transcription.
        Notes:
            - The method uses a sample rate of 16 kHz and processes audio in
            30 ms frames.
            - A threshold ratio of voiced frames is used to determine the
            start and end of speech.
            - The recording duration is limited to a maximum of 10 seconds.
            - The transcription is performed using a preloaded speech-to-text
            model.
        Example:
            text = self.get_voice_input()
            if text:
                print(f"Transcribed text: {text}")
                print("No speech detected or an error occurred.")
        """

        print("\033[38;5;55mListening for voice input with VAD...\033[0m")
        sample_rate = constant.SpeechRecognitionConfig.SAMPLE_RATE
        frame_duration = constant.SpeechRecognitionConfig.FRAME_DURATION_MS  # ms
        num_padding_frames = constant.SpeechRecognitionConfig.NUM_PADDING_FRAMES
        threshold = constant.SpeechRecognitionConfig.VOICE_THRESHOLD

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
                    data, overflowed = stream.read(int(sample_rate * frame_duration / 1000))
                    if overflowed:
                        print("\033[38;5;55mAudio buffer overflowed\033[0m")

                    # Ensure audio data is in 16-bit PCM format
                    audio_data = data.flatten().astype(np.int16).tobytes()
                    is_speech = self.vad.is_speech(audio_data, sample_rate)
                    if not triggered:
                        ring_buffer.append((data.tobytes(), is_speech))
                        num_voiced = len([frame for frame, speech in ring_buffer if speech])

                        if num_voiced > threshold * num_padding_frames:
                            triggered = True
                            voiced_frames.extend([frame for frame, _ in ring_buffer])
                            ring_buffer.clear()
                    else:
                        voiced_frames.append(data.tobytes())
                        ring_buffer.append((data.tobytes(), is_speech))
                        num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                        if num_unvoiced > threshold * num_padding_frames:
                            break  # End of speech
                    max_dur = constant.SpeechRecognitionConfig.MAX_RECORDING_DURATION
                    max_frames = sample_rate * max_dur
                    if len(voiced_frames) > max_frames:
                        print(("\033[38;5;55mMax recording duration reached." "\033[0m"))
                        break

        except Exception as e:
            print(f"\033[38;5;55mError during voice input: {e}\033[0m")
            return ""

        if not voiced_frames:
            print("\033[38;5;55mNo speech detected.\033[0m")
            return ""

        audio_data = b"".join(voiced_frames)

        if constant.SpeechRecognitionConfig.QUEUED_MODEL == "whisper":
            return self.transcribe_audio_whisper(osc, audio_data)
        elif constant.SpeechRecognitionConfig.QUEUED_MODEL == "genai":
            return self.transcribe_audio_genai(osc, audio_data)
        else:
            print("\033[38;5;55mInvalid transcription model specified.\033[0m")
            return ""

    def transcribe_audio_whisper(self, osc, audio_data: bytes) -> str:
        audio_array = np.frombuffer(audio_data, dtype="int16").astype(np.float32) / 32768.0

        print("\033[38;5;55mTranscribing voice input with faster-whisper...\033[0m")
        osc.send_message("Thinking")
        osc.set_typing_indicator(True)
        try:
            # faster-whisper returns (segments, info). segments is an iterator of Segment
            segments, info = self.model.transcribe(audio_array, beam_size=5)
            # Convert segments iterator to a list and check if it's empty
            segments_list = list(segments)
            if not segments_list:
                return ""
            text_parts = [segment.text for segment in segments_list]
            text = " ".join(text_parts).strip()
            return text
        except Exception as e:
            print(f"\033[38;5;92mError during transcription: {e}\033[0m")
            return ""

    def transcribe_audio_genai(self, osc, audio_data: bytes):
        print("\033[38;5;55mTranscribing voice input with GenAI...\033[0m")
        # Convert raw PCM int16 bytes to a WAV file in-memory and upload it
        file_obj = io.BytesIO()
        with wave.open(file_obj, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(constant.SpeechRecognitionConfig.SAMPLE_RATE)
            wf.writeframes(audio_data)
        file_obj.seek(0)
        file_obj.name = "speech.wav"

        myfile = self.genai.files.upload(file=file_obj, config={"mime_type": "audio/wav"})
        response = self.genai.models.generate_content(model="gemini-2.5-flash", contents=[self.prompt, myfile])

        return response.text

    def get_user_input(self, osc) -> str:
        """
        Wrapper method to get voice input using the preferred transcription
        method.
        Returns:
            str: The transcribed text from the voice input.
        """

        return self.get_voice_input(osc)
