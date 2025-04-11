import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker
import requests

API_URL = "http://localhost:8000/get_card_image"

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./decks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
session_factory = sessionmaker(bind=engine)

# Initialize the database session
session = session_factory()

# from models import Base

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

@bot.command(name="deckview")
async def deckview(ctx, *, deckname: str):
    # Split the decklist into individual card names
    #decklist = session.execute(select(Deck).where(Deck.name == deckname)).scalar_one_or_none()
    decklist = "Card 1 {Card 2 {Card 3"  # Placeholder for actual decklist retrieval
    if not decklist:
        await ctx.send("Deck not found.")
        return
    card_names = decklist.split("{")
    for card in card_names:
        card = card.strip()
        if card:
            await ctx.send(f"{card}")

@bot.command(name="random")
async def random(ctx):
    response = requests.get(API_URL + "/random")
    if response.status_code == 200:
        card_data = response.json()
        card_name = card_data.get("name")
        card_image_url = card_data.get("image_url")
        await ctx.send(f"Random Card: {card_name}\n{card_image_url}")
    else:
        await ctx.send("Error retrieving random card.")

bot.run(TOKEN)
