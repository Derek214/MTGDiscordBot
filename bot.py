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
        deck = "" 
        for image in image_url:
            image = image.get("image_url")
            deck += f"{image}  "
        await ctx.send(f"{deck}")  
    else:
        await ctx.send("Error retrieving card data.")
    

@bot.command(name="random")
async def random(ctx):
    response = requests.get(API_URL + "/random")
    if response.status_code == 200:
        card_data = response.json()
        card_name = card_data.get("name")
        card_image_url = card_data.get("image_url")
        await ctx.send(f"{card_image_url}")
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
    # Check if the user is the creator of the deck
    response = requests.get(API_URL + "/view_deck", params={"deck_name": deck_name})
    if response.status_code == 200:
        deck_data = response.json()
        creator_name = str(deck_data.get("creator_name"))
        await ctx.send(creator_name)
        if str(ctx.author) == creator_name:
            await ctx.send(f"Are you sure you want to delete the deck '{deck_name}'? Type 'yes' to confirm.")
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]
            try:
                msg = await bot.wait_for('message', check=check, timeout=25.0)
                if msg.content.lower() == "yes":
                    response = requests.delete(API_URL + "/delete_deck", params={"deck_name": deck_name})
                    if response.status_code == 200:
                        await ctx.send(f"Deck '{deck_name}' deleted successfully!")
                    else:
                        await ctx.send("Error deleting deck.")
                else:
                    await ctx.send("Deck deletion canceled.")
            except TypeError:
                await ctx.send("No response received. Deck deletion canceled.")
        else:
            await ctx.send("You are not the creator of this deck and cannot delete it.")
    else:
        await ctx.send("Error retrieving deck data.")
        
@bot.command(name="editdeck")
async def editdeck(ctx, *, deck_name: str):
    # Make sure user is editing the right deck
    # Figure out a loop for editing the deck X number of times
    response = requests.get(API_URL + "/view_deck", params={"deck_name": deck_name})
    if response.status_code == 200:
        deck_data = response.json()
        creator_name = deck_data.get("creator_name")
        if ctx.author == creator_name:
            await ctx.send(f"Please send the new decklist for '{deck_name}' in the format: Card1" + "{" +"Card 2"+ "{"+"Card3 ...")
            msg = await bot.wait_for('message', check=lambda message: message.author == ctx.author and message.channel == ctx.channel, timeout=25.0)
            decklist_message = msg.content
            response = requests.put(API_URL + "/edit_deck", json={"deck_name": deck_name, "cards": decklist_message})
            if response.status_code == 200:
                await ctx.send(f"Deck '{deck_name}' edited successfully!")
            else:
                await ctx.send("Error editing deck.")
        else:
            await ctx.send("You are not the creator of this deck and cannot edit it.")

@bot.command(name="botinfo")
async def botinfo(ctx):
    commandops = [
        "/card <card_name> - Get card image",
        "/deckview <deck_name> - View deck",
        "/randomcard - Get a random card",
        "/newcomideas <colorset> <creaturetype>- Sends new ideas for commander based on colorset and creature type",
        "/builddeck <deck_name> - Build a new deck",
        "/editdeck <deck_name> - Edit deck if you created it",
        "/deletedeck <deck_name> - Delete deck if you created it"
    ]
    await ctx.send("\n".join(commandops))

@bot.command(name="newcomideas")
async def newcomideas(ctx, colorset: str, creaturetype: str):
    response = requests.get(API_URL + "/newcomideas", params={"colorset": colorset, "creaturetype": creaturetype})
    if response.status_code == 200:
        ideas = response.json()
        await ctx.send(f"New Commander Ideas:\n{ideas}")
    else:
        await ctx.send("Error retrieving new commander ideas.")
bot.run(TOKEN)
