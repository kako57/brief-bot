import cohere

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
