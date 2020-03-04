import discord
import youtube_dl

from discord.ext import commands
vc = ""
bot = commands.Bot(command_prefix='.')
bot.remove_command('help')
token = 'Njg0NjUwMDk1MTgxOTU1MTA0.Xl9Nyg.-tzleGbfV8flXyYo0Xa4d9BFYWg'

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

bot.run(token)
