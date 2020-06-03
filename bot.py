import discord
import youtube_dl
import asyncio
from discord.ext import commands
import queue
bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'))
bot.remove_command('help')

token = ''

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
    'source_address': '0.0.0.0',
    'audio_quality': '0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

videoqueue = queue.Queue(maxsize=10)
now_playing = ""
play_author = ""
voiceclient = None
get_pl = 0
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
        playdata = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in playdata:
            playdata = playdata['entries'][0]

        filename = playdata['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), playdata=playdata)

@bot.command()
async def help(ctx):
    embed=discord.Embed(title="help")
    embed.add_field(name = "help", value = "display this help", inline = False)
    embed.add_field(name = "play", value = "play a video on websites that youtube_dl supports or search on youtube", inline = False)
    embed.add_field(name = "disconnect", value = "disconnect from voice", inline = False)
    embed.add_field(name = "volume", value = "change the volume of the music played by the bot 0 - 100, default 50", inline = False)
    embed.add_field(name = "nowplaying", value = "show what is playing now, aliases: np now_playing", inline = False)
    embed.add_field(name = "playlist", value = "show playlist, aliases: pl playqueue", inline = False)
    await ctx.send(embed=embed)

@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, *, url):
    async with ctx.typing():
        await join(ctx)
        if videoqueue.empty() and (not ctx.voice_client.is_playing()):
            await start(ctx, url)
        elif ctx.voice_client.is_playing() and (not videoqueue.full()):
            temp = info(ctx, url)
            videoqueue.put(temp)
        else:
            await tx.send("queue full")
@bot.command()
async def volume(ctx, volume: int):
    if ctx.voice_client is None:
        return await ctx.send("Not connected to vc")
    ctx.voice_client.source.volume = volume / 100
    await ctx.send("volume change done")

@bot.command()
async def skip(ctx):
    if ctx.author.id == play_author_id:
        ctx.voice_client.stop()
    else:
        pass

@bot.command(aliases=['np', 'now_playing'])
async def nowplaying(ctx):
    await ctx.send(f"""Now playing: {now_playing}""")

@bot.command(aliases=['playqueue', 'pl'])
async def playlist(ctx):
    get_pl = 1
    if not videoqueue.empty():
        embed = discord.Embed(title="playlist")
        i = videoqueue.qsize()
        number = 0
        while i > 0:
            temp = videoqueue.get()
            title_temp = ytdl.extract_info(temp.url, download=False)
            if 'entries' in title_temp:
                title_temp = title_temp['entries'][0]
            title_temp = title_temp['title']
            number += 1
            embed.add_field(name=f"""{number}""", inline=False, value=f"""{title_temp}: \n {temp.url}""")
            videoqueue.put(temp)
            i -= 1
        await ctx.send(embed=embed)
    else:
        await ctx.send("playlist is empty")
    get_pl = 0

async def join(ctx):
    if ctx.voice_client is None:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("not connected to a voice channel")
            raise commands.CommandError("not connected to a voice channel")

async def start(ctx, url):
    player = await yt_source.get_url_data(url, loop=bot.loop, stream=True)
    ctx.voice_client.play(player)
    await ctx.send(f"""Now playing: {url}""")
    global now_playing 
    global play_author_id
    global voiceclient
    now_playing = url
    play_author_id = ctx.author.id
    voiceclient = ctx.voice_client

async def playqueue_check(): 
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        await asyncio.sleep(1)
        if voiceclient is not None:
            if not voiceclient.is_playing() and not videoqueue.empty() and get_pl == 0:
                videoinfo = videoqueue.get()
                await start(videoinfo.context, videoinfo.url)
        

bot.loop.create_task(playqueue_check())
bot.run(token)
