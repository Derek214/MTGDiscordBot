from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import sqlite3

app = FastAPI()
DB_PATH = "MagicTheGathering.db"
    
class CardRequest(BaseModel):
    card_name: str

def search_card(card_name: str):
    url = f"https://api.scryfall.com/cards/named?fuzzy={card_name.replace(' ', '%20')}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('image_uris', {}).get('normal')
        if image_url:
            return image_url
        else:
            return "error: Image not found"
    else:
        return "error: Card not found"
    
def get_random_card():
    # Fetches a completely random Magic card
    url = "https://api.scryfall.com/cards/random"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data.get('image_uris', {}).get('normal')
        if image_url:
            return image_url
        else:
            return "error: Image not found"
    else:
        return "error: Card not found"

@app.get("/get_card_image")
async def get_card_image(card_name: str):
    image_url = search_card(card_name)
    if 'error' in image_url:
        raise HTTPException(status_code=404, detail=image_url)
    return {"image_url": image_url}

@app.get("/random")
async def random():
    image_url = get_random_card()
    if 'error' in image_url:
        raise HTTPException(status_code=404, detail=image_url)
    return {"image_url": image_url}

"""
@app.get("/view_deck")
async def view_deck(deck_name: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT deck_name, cards FROM decks WHERE LOWER(deck_name) = LOWER(?)", (deck_name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            deck_name, cards = row
            card_list = [card.strip() for card in cards.split(',')]
            return {"deck_name": deck_name, "cards": card_list}
        else:
            raise HTTPException(status_code=404, detail="Deck not found")

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
"""