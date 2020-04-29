import discord
import youtube_dl
import asyncio
from discord.ext import commands
import queue
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

videoqueue = queue.Queue(maxsize = 10)
now_playing = ""
play_author = ""

class info():
    def __init__(self, context, url):
        self.context = context
        self.url = url

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
        if 'entries' in playdata:
            playdata = playdata['entries'][0]
        filename = playdata['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=playdata)

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="help")
    await ctx.send(embed=embed)

@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, url):
    async with ctx.typing():
        if videoqueue.empty() && not ctx.voice_client.is_playing():
            await start(ctx, *, url)
        elif ctx.voice_client.is_playing() && not videoqueue.full():
            temp = info(ctx, url)
            videoqueue.put(temp)
        else:
            ctx.send("queue full")
@bot.command()
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to vc")
    ctx.voice_client.source.volume = volume / 100
    await ctx.send("volume change done")

@bot.command()
async def skip(ctx):
    if ctx.author = play_author:
        ctx.voice_client.stop()
    else:
        pass


async def join(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("not connected to a voice channel")
            raise commands.CommandError("not connected to a voice channel")

async def start(ctx, *, url):
    player = await ytsource.get_url_data(url, loop=self.bot.loop, stream=True)
    await join(ctx)
    ctx.voice_client.play(player)
    ctx.send(f"""Now playing: {url}""")
    now_playing = url
    play_author = ctx.author

bot.run(token)
