import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

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

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)


@bot.event
async def on_message(message):
    if message.channel.id != CARD_CHANNEL_ID:
        return
    
    if message.author == bot.user:
        return

    if message.content.startswith('/card'):
        await message  #API call to get card data
        await message.channel.send('Card data here!')
