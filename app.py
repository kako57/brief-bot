# imports
import os
from dotenv import load_dotenv

import discord
from discord.ext import commands

import discord.voice_client
import discord.sinks

from cohere_functions import generate, identify_emotion_v2

import traceback

from ntranscribe import transcribe


# loading .env
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# setting up discord client
intents = discord.Intents.default()
intents.message_content = True
# client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

connections = {}

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
    response = '''**SUPPORTED COMMANDS**
!ping: Play pingpong with BriefBot.

!commands: Shows commands (this message).

!summarize <message>: Summarizes **<message>**. Only supports messages of length greater than 250.

!rundown <number>: Summarizes the last **<number>** messages in this channel. Only supports long conversations.

!emotion <message>: Attempts to classify the emotion of **<message>**.
    '''
    await ctx.send(response)

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
    response = identify_emotion_v2("".join(args))
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
async def leave(ctx):
    ''' leave the voice channel '''
    await ctx.voice_client.disconnect()

# callback function after recording has finished
async def after_record(sink, channel, *args):
    recorded_users = [
        f"<@{user_id}>"
        for user_id, _ in sink.audio_data.items()
    ]

    await sink.vc.disconnect()

    files = []
    transcripts = []
    for user_id, audio in sink.audio_data.items():
        print(audio.file)
        files.append(discord.File(audio.file, f"{user_id}.{sink.encoding}"))
        # audio.file.seek(0)
        # create a temporary wav file just so we can transcribe it
        # TODO: convert to mono channel
        filename = f"{user_id}.wav"
        with open(filename, "wb") as f:
            print(f.name)
            f.write(audio.file.read())
        transcripts.append(f'{user_id}:\n{transcribe(filename)}')
        os.remove(filename)

    for transcript in transcripts:
        await channel.send(transcript)

    await channel.send(
        f"finished recording audio for: {', '.join(recorded_users)}.",
        files=files
    )  # Send a message with the accumulated files.

@bot.command()
async def record(ctx):
    voice = ctx.author.voice

    if not voice:
        await ctx.send("You are not in a voice channel!")
        return

    vc = await voice.channel.connect()

    connections.update({ctx.guild.id: vc})

    vc.start_recording(
        discord.sinks.WaveSink(),
        after_record,
        ctx.channel
    )

    await ctx.send("Recording...")

@bot.command()
async def stop(ctx):
    if ctx.guild.id in connections:
        vc = connections[ctx.guild.id]
        vc.stop_recording()

        del connections[ctx.guild.id]

        # await ctx.delete()
    else:
        await ctx.respond("I am currently not recording here.")

# run the bot!
bot.run(TOKEN)
