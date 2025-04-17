import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests

API_URL = "http://localhost:8000"

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
    
    response = requests.get(API_URL + "/get_card_image", params={"card_name": card_name})
    
    if response.status_code == 200:
        await ctx.send(response.text)
    else:
        await ctx.send("Error retrieving card data.")

@bot.command(name="deckview")
async def deckview(ctx, *, deck_name: str):
    response = requests.get(API_URL + "/view_deck", params={"deck_name": deck_name})
    
    if response.status_code == 200:
        image_url = response.json().get("cards")
        for image in image_url:
            await ctx.send(f"{image}")   
    else:
        await ctx.send("Error retrieving card data.")
    

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


@bot.command(name="builddeck")
async def builddeck(ctx, *, deck_name: str):
    # Wait for Next Sent Message
    await ctx.send(f"Please send the decklist for '{deck_name}' in the format: Card1" + "{" +"Card 2"+ "{"+"Card3 ...")
    msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=25.0)
    decklist_message = msg.content
    #API Call To Create Deck
    response = requests.post(API_URL + "/build_deck", json={"deck_name": deck_name, "cards": decklist_message, "creator_name": str(ctx.author)})
    if response.status_code == 200:
        await ctx.send(f"Deck '{deck_name}' created successfully!")
    else:
        await ctx.send("Error creating deck.")
        
@bot.command(name="deletedeck")
async def deletedeck(ctx, *, deck_name: str):
    # Make sure user wants to delete deck
    print
        
@bot.command(name="editdeck")
async def editdeck(ctx, *, deck_name: str):
    # Make sure user is editing the right deck
    print
    # Figure out a loop for editing the deck X number of times

@bot.command(name="botinfo")
async def botinfo(ctx):
    commandops = [
        "/card <card_name> - Get card image",
        "/deckview <deck_name> - View deck",
        "/random - Get a random card",
        "/newcomideas <colorset> <creaturetype>- Sends new ",
        "/builddeck <deck_name> - Build a new deck",
        "/editdeck <deck_name> - Edit deck if you created it",
        "/deletedeck <deck_name> - Delete deck if you created it"
    ]
    await ctx.send("\n".join(commandops))

@bot.command(name="newcomideas")
async def newcomideas(ctx,*, colorset: str, creattype: str):
    response = requests.get(API_URL + "/newcomideas", params={"colorset": colorset , "creattype": creattype})
    # At the Endpoint /newcomideas, send colorset and creattype as params
    # Search Scryfall based on parameters Legendary, Colorset, And Creature Type
    # Receive back list of cards as JSON
    if response.status_code == 200:
        card_data = response.json()
        card_name = card_data.get("name")
        card_image_url = card_data.get("image_url")
        await ctx.send(f"New Ideas: {card_name}\n{card_image_url}")
    else:
        await ctx.send("Error retrieving newcomer ideas.")
bot.run(TOKEN)
