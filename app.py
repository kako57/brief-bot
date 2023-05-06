# imports
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import cohere

# loading .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')

# setting up discord client
intents = discord.Intents.default()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# setting up cohere client
co = cohere.Client(API_KEY)

# cohere functions
async def generate(message):
    print("message:", message)
    if len(message) < 250:
        await ctx.send("Must be longer than 250 characters!")
    else:
        return await generate_short(message)

async def generate_short(message):
    response = co.summarize(
        text=message,
        length='auto',
        format='auto',
        model='summarize-medium',
        additional_command='',
        temperature=0.3,
    )
    print("response:", response.summary)
    return response.summary

async def generate_long(message):
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

# bot commands
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def summarize(ctx, *, args=None):
    response = await generate(" ".join(args))
    await ctx.send(response)

# run the bot!
bot.run(TOKEN)
