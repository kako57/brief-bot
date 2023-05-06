import os

import discord
from dotenv import load_dotenv

import cohere

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

co = cohere.Client(API_KEY)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!ping'):
        await message.channel.send('Pong!')
        return
    
    if message.content.startswith('!cohere'):
        response = await generate(" ".join(message.content.split()[1:]))
        await message.channel.send(response)
        return
        
async def generate(message):
    print("message:", message)
    response = co.summarize( 
        text=message,
        length='auto',
        format='auto',
        model='summarize-xlarge',
        additional_command='',
        temperature=0.3,
    )
    print("response:", response.summary)
    return response.summary

client.run(TOKEN)
