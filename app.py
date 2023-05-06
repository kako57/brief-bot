# imports
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import cohere

import traceback

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
        return "Must be longer than 250 characters!"
    else:
        return await generate_long(message)

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

async def rundown_helper(ctx, num):
    messages = []
    input = ""

    # needs to be in chronological order
    async for msg in ctx.channel.history(limit=num+1):
        messages.append(msg)

    # ignore the command call itself
    messages.pop(0)

    for msg in messages:
        input += msg.author.name.strip() + ': "' + msg.content.strip() + '"\n'
    print(input)

    response = await generate(input)
    return response

# bot commands
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def summarize(ctx, *, args=None):
    response = await generate("".join(args))
    await ctx.send(response)

@bot.command()
async def rundown(ctx, *, args=None):
    print("rundown args:", args)
    if args is None:
        print("No args provided")
        response = "Format: !rundown <number>"
    else:
        args_split = args.split(" ")
        if len(args_split) > 1:
            print("Too many args:", len(args_split))
            response = "Format: !rundown <number>"
        else:
            try:
                print("args_split[0]:", args_split[0])
                num = int(args_split[0].strip())
                if num > 100:
                    response = "That's quite a lot of messages! :astonished:\nMax is 100."
                else:
                    response = await rundown_helper(ctx, num)
            except ValueError:
                response = "Format: !rundown <number>"
            except:
                response = "Something went wrong!"
                traceback.print_exc()
    await ctx.send(response)

# run the bot!
bot.run(TOKEN)
