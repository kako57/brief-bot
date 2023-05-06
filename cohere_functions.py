# imports
import os
from dotenv import load_dotenv

import cohere

load_dotenv()
API_KEY = os.getenv('API_KEY')

# setting up cohere client
co = cohere.Client(API_KEY)

# cohere functions
def generate(message):
    print("message:", message)
    if len(message) < 250:
        return "Must be longer than 250 characters!"
    else:
        return generate_long(message)

def generate_short(message):
    response = co.summarize(
        text=message,
        length='auto',
        format='auto',
        model='summarize-medium',
        additional_command='',
        temperature=0.5,
    )
    print("response:", response.summary)
    return response.summary

def generate_long(message):
    print("message:", message)
    response = co.summarize(
        text=message,
        length='auto',
        format='auto',
        model='summarize-xlarge',
        additional_command='',
        temperature=0.5,
    )
    print("response:", response.summary)
    return response.summary

def identify_emotion(message):
    if message is None:
        return "Format: !emotion <message>"
    response = co.classify(
        model='96ad5ed9-d43a-49e7-b0da-79d5b2c9555d-ft',
        inputs=[message]
    )
    return response.classifications[0].prediction.capitalize() + "!"

def identify_emotion_v2(message):
    if message is None:
        return "Format: !emotion <message>"
    response = co.classify(
        model='5092799e-cf8d-4129-b81f-04417e54d3b2-ft',
        inputs=[message]
    )
    dict = {0:'Sadness!', 1:'Joy!', 2:'Love!', 3:'Anger!', 4:'Fear!'}
    return dict.get(int(response.classifications[0].prediction))
