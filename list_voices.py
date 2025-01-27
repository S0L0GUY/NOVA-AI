'''
List all of the voices available for pyttsx3 on this system.
'''
import pyttsx3


engine = pyttsx3.init()

voices = engine.getProperty('voices')
for voice in voices:
    print(
        f"ID: {voice.id}\n"
        f"Name: {voice.name}\n"
        f"Gender: {voice.gender}\n"
        f"Language: {voice.languages}\n"
    )
