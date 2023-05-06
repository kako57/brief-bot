#!/usr/bin/env python3

import speech_recognition as sr

def transcribe(audio_file):
    r = sr.Recognizer()

    print("Recognizer init time: ", end - start)

    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    return r.recognize_sphinx(audio)

# if __name__  == "__main__":
#     print(transcribe("english.wav"))
