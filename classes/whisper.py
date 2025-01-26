import whisper
import pyaudio
import wave
from pydub import AudioSegment
import logging

class WhisperTranscriber:
    def __init__(self):
        self.model = whisper.load_model("base")

    def get_speech_input(self):
        """
        Records audio input from the microphone, detects silence to stop
        recording, saves the audio to a WAV file, transcribes the audio using
        Whisper, and filters out unwanted responses.
        Returns:
            str: The transcribed text from the audio input, or an empty string
            if the transcribed text matches any unwanted responses.
        """

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Set audio recording parameters
        format = pyaudio.paInt16
        channels = 1
        rate = 16000
        chunk = 1024
        silence_threshold = -50  # Adjusted silence threshold in dB
        silence_duration = 0.5  # Adjusted duration of silence in seconds

        # Open the audio stream
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)

        # Record audio
        frames = []
        silent_chunks = 0

        while True:
            data = stream.read(chunk)
            frames.append(data)

            # Convert audio chunk to Pydub's AudioSegment for silence detection
            audio_chunk = AudioSegment(
                data,
                sample_width=p.get_sample_size(format),
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
                break

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save the recorded data to a WAV file
        with wave.open('temp.wav', 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))

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
            logging.info(f"Transcribed text: {text}")
            return text
        else:
            logging.info("Unwanted response detected.")
            return ""

    def start_listening(self):
        """
        Starts listening for speech input and returns the transcribed text.
        Returns:
            str: The transcribed text from the audio input.
        """
        logging.info("Listening for speech input...")
        return self.get_speech_input()
