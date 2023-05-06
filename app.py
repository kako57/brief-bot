# imports
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

from cohere_functions import generate, identify_emotion

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

async def rundown_helper(ctx, num):
    messages = []
    input = ""

    # needs to be in chronological order
    async for msg in ctx.channel.history(limit=num+1):
        messages.insert(0, msg)

    # ignore the command call itself
    messages.pop()

    for msg in messages:
        input += msg.author.name.strip() + ': "' + msg.content.strip() + '"\n'
    print(input)

    response = generate(input)
    return response

@bot.event
async def on_ready():
    activity = discord.Game(name="!commands", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bot is ready!")

# bot commands
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def commands(ctx):
    await ctx.send('''
    **SUPPORTED COMMANDS**\n!ping: Play pingpong with BriefBot.\n\n!commands: Shows commands (this message).\n\n!summarize <message>: Summarizes **<message>**. Only supports messages of length greater than 250.\n\n!rundown <number>: Summarizes the last **<number>** messages in this channel. Only supports long conversations.\n\n!emotion <message>: Attempts to classify the emotion of <message>.
    ''')

@bot.command()
async def summarize(ctx, *, args=None):
    response = generate("".join(args))
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

@bot.command()
async def emotion(ctx, *, args=None):
    response = identify_emotion("".join(args))
    await ctx.send(response)

@bot.command()
async def move(ctx):
    ''' move the bot to the voice channel you are in '''

    # check first if the user is in a voice channel
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel!")
        return

    channel = ctx.author.voice.channel

    # check if voice client already exists
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)

@bot.command()
async def record(ctx):
    # first, try joining the voice channel
    await move(ctx)

    # check if the bot is already recording
    if ctx.voice_client.is_recording():
        await ctx.send("Already recording!")
        return

    # start recording
    ctx.voice_client.start_recording("recording.wav")

@bot.command()
async def stop(ctx):
    # check if the bot is recording
    if not ctx.voice_client.is_recording():
        await ctx.send("Not recording!")
        return

    # stop recording
    ctx.voice_client.stop_recording()

    # save the recording
    ctx.voice_client.save_recording("recording.wav")

    # disconnect from the voice channel
    await ctx.voice_client.disconnect()

    # TODO: show a menu for the user to choose what to do with the recording
    # await ctx.send("Recording saved! What would you like to do with it?")
    # await ctx.send("1. Play the recording\n2. Summarize the recording\n3. Identify the emotion of the recording")

# run the bot!
bot.run(TOKEN)
