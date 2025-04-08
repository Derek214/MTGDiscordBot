import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

API_URL = "http://localhost:8000/get_card_image"

load_dotenv() 
TOKEN = os.getenv("DISCORD_TOKEN") 

bot = commands.Bot(command_prefix='/', intents=discord.Intents.default())

CARD_CHANNEL_ID = 1359304823903748156

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')
            
    async def on_message(ctx):
        await ctx.channel.send('Card data here!')
        
        

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)


@bot.command(name="cardsearch")
async def on_message(ctx):
    message = ctx.message 
    if message.channel.id != CARD_CHANNEL_ID:
        return
    
    if message.author == bot.user:
        return

    if message.content.startswith('/card'):
        card_name = message.content[len("/card "):].strip()
        response = requests.get(API_URL, params={"card_name": card_name})
        await ctx.channel.send(response)
        await ctx.channel.send('Card data here!')
     
@bot.command()   
async def info(ctx):
    await ctx.send(f"Command usd by: {ctx.author}")
    await ctx.send(f"In channel: {ctx.channel.name}")
    await ctx.send(f"In server: {ctx.guild.name}")
    
        
bot.run(TOKEN)
