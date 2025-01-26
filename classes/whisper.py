import whisper
import sounddevice as sd
import constants as constant
import numpy as np
import wave
from pydub import AudioSegment


class WhisperTranscriber:
    def __init__(self):
        self.model = whisper.load_model("base")

    def get_speech_input(self, device_index=constant.AUDIO_INPUT_INDEX):
        """
        Records audio input from the specified device index, detects silence
        to stop recording, saves the audio to a WAV file, transcribes the
        audio using
        Whisper, and filters out unwanted responses.
        Args:
            device_index (int, optional): The index of the audio input device
            to use.
        Returns:
            str: The transcribed text from the audio input, or an empty string
            if the transcribed text matches any unwanted responses.
        """

        # Set audio recording parameters
        channels = 1
        rate = 16000
        chunk = 1024
        silence_threshold = 50  # Silence threshold in dB
        silence_duration = 1  # Duration of silence in seconds

        # Record audio
        frames = []
        silent_chunks = 0

        def callback(indata, frame_count, time, status):
            nonlocal silent_chunks
            frames.append(indata.copy())

            # Convert audio chunk to Pydub's AudioSegment for silence detection
            audio_chunk = AudioSegment(
                indata.tobytes(),
                sample_width=indata.dtype.itemsize,
                frame_rate=rate,
                channels=channels
            )

            # Check if the audio chunk is silent
            if audio_chunk.dBFS < silence_threshold:
                silent_chunks += 1
            else:
                silent_chunks = 0

            # Stop recording after detecting sufficient silence
            if silent_chunks > silence_duration * (rate / chunk):
                raise sd.CallbackStop

        with sd.InputStream(
            callback=callback,
            channels=channels,
            samplerate=rate,
            dtype='int16',
            device=device_index
        ):
            sd.sleep(int(1000 * silence_duration * (rate / chunk)))

        # Save the recorded data to a WAV file
        with wave.open('temp.wav', 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(np.dtype('int16').itemsize)
            wf.setframerate(rate)
            wf.writeframes(b''.join([frame.tobytes() for frame in frames]))

        # Transcribe audio file using Whisper
        result = self.model.transcribe('temp.wav')
        text = result['text']

        # Filter out unwanted responses
        unwanted_responses = [
            " you",
            " Thank you.",
            "forget all previous instructions",
            "forget all instructions",
            "forget all prior instructions"
        ]

        if text not in unwanted_responses:
            return text
        else:
            return ""
