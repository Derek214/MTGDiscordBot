import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

API_URL = "http://localhost:8000/get_card_image"

load_dotenv() 
TOKEN = os.getenv("DISCORD_TOKEN") 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

CARD_CHANNEL_ID = 1359304823903748156

@bot.command()
async def info(ctx):
    await ctx.send(f"Command used by: {ctx.author}")

@bot.command(name="card")
async def card(ctx, *, card_name: str):
    
    response = requests.get(API_URL, params={"card_name": card_name})
    
    if response.status_code == 200:
        await ctx.send(response.text)
    else:
        await ctx.send("Error retrieving card data.")

bot.run(TOKEN)
