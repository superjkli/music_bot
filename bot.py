import discord
import youtube_dl
import asyncio
from discord.ext import commands
vc = ""
bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'))
bot.remove_command('help')
token = 'Njg0NjUwMDk1MTgxOTU1MTA0.Xl9Nyg.-tzleGbfV8flXyYo0Xa4d9BFYWg'

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class yt_source(discord.PCMVolumeTransformer):
    def __init__(self, source, playdata, volume = 0.5):
        super().__init__(source, volume)
        self.playdata = playdata
        self.url = playdata.get('url')
        self.title = playdata.get('title')

    @classmethod
    async def get_url_data(cls, url, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        playdata = await loop.run_in_executor(None, extract_info_from_ytdl(url, stream))
        if 'entries' in data:
            data = data['entries'][0]

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="help")
    await ctx.send(embed=embed)

@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    vc = await channel.connect()

@bot.command()
async def disconnect(ctx):
    guild = ctx.message.guild
    await guild.voice_client.disconnect()

@bot.command()
async def play(ctx, url):
    pass

bot.run(token)
