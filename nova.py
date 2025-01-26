import logging

def run_code():
    from classes.whisper import WhisperTranscriber
    from classes.system_prompt import SystemPrompt
    from classes.json_wrapper import JsonWrapper
    from classes.osc import VRChatOSC
    import constants as constant
    from openai import OpenAI
    import datetime
    import pyttsx3
    # import http_server
    import re
    import os
    import sounddevice as sd
    import soundfile as sf

    osc = VRChatOSC(constant.LOCAL_IP, constant.VRC_PORT)
    transcriber = WhisperTranscriber()

    # Send message to VRChat to indicate that the system is starting
    osc.send_message("System Loading")
    osc.set_typing_indicator(True)

    # Get the system prompt
    system_prompt = SystemPrompt.get_full_prompt("normal")

    # Set up history
    now = datetime.datetime.now()

    history = [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"Today is {now.strftime('%Y-%m-%d')}"},
        {"role": "user", "content": "Hey"},
    ]

    # Set up LLM
    openai_client = OpenAI(
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )

    def play_tts(text, output_device_index=constant.AUDIO_OUTPUT_INDEX):
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'Zira' in voice.name:
                engine.setProperty('voice', voice.id)
                break
        engine.setProperty('rate', 200)  # Speed of speech
        engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

        file_path = "tts_output.wav"

        if os.path.exists(file_path):
            os.remove("tts_output.wav")

        engine.save_to_file(text, file_path)
        engine.runAndWait()

        def play_audio(file_path, output_device_index):
            data, samplerate = sf.read(file_path, always_2d=False)
            sd.play(data, samplerate, device=output_device_index)
            sd.wait()

        play_audio(file_path, output_device_index)

    def chunk_text(text):
        """
        Args:
            text (string): The text to break down.

        Returns:
            string: Text chunk.

        Split the text by sentence-ending punctuation
        """
        chunks = re.split(r'(?<=[.,;:!?]) +', text)
        return chunks

    # Main logic
    while True:
        # Creates model parameters
        completion = openai_client.chat.completions.create(
            model=constant.MODEL_ID,
            messages=history,
            temperature=constant.LM_TEMPERATURE,
            stream=True,
        )

        new_message = {"role": "assistant", "content": ""}

        osc.send_message("Thinking")
        osc.set_typing_indicator(True)

        buffer = ""
        full_response = ""

        for chunk in completion:
            osc.set_typing_indicator(True)
            if chunk.choices[0].delta.content:
                buffer += chunk.choices[0].delta.content
                sentence_chunks = chunk_text(buffer)
                while len(sentence_chunks) > 1:
                    sentence = sentence_chunks.pop(0)
                    full_response += f" {sentence}"
                    print(f"AI: {sentence}")
                    osc.send_message(sentence)
                    play_tts(sentence)
                buffer = sentence_chunks[0]

        if buffer:
            osc.set_typing_indicator(True)
            full_response += f" {buffer}"
            print(f"AI: {buffer}")
            osc.send_message(buffer)
            play_tts(buffer)
            new_message["content"] = full_response

        osc.set_typing_indicator(False)

        JsonWrapper.write(constant.HISTORY_PATH, new_message)

        # Get user speech input
        user_speech = ""

        while not user_speech:
            user_speech = transcriber.start_listening()
            if not user_speech:
                logging.info("No speech detected, waiting for input...")

        logging.info(f"HUMAN: {user_speech}")

        JsonWrapper.write(constant.HISTORY_PATH, user_speech)
