from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker
from datamodel import Base, Deck
import random
import time
from typing import Optional
import re

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./decks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
session_factory = sessionmaker(bind=engine)
session = session_factory()

class DeckRequest(BaseModel):
    creator_name: str
    deck_name: str
    cards: str

app = FastAPI()
DB_PATH = "decks.db"

# Regex for valid color sets (e.g., w, ub, wubrg)
try:
    color_regex = re.compile(r"(?i)^(?!.*(.).*\1)[wubrg]{1,5}$")
except re.error as e:
    raise ValueError(f"Invalid regex pattern: {e}")
    
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
async def random_card():
    image_url = get_random_card()
    if 'error' in image_url:
        raise HTTPException(status_code=404, detail=image_url)
    return {"image_url": image_url}

@app.get("/view_deck")
async def view_deck(deck_name: str):
    deck = session.query(Deck).filter(Deck.deck_name == deck_name).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    card_names = [name.strip() for name in deck.cards.split("|") if name.strip()]
    image_urls = []

    for name in card_names:
        time.sleep(.2)
        image_url = search_card(name)
        if "error" not in image_url:
            image_urls.append({
                "card_name": name,
                "image_url": image_url
            })
        else:
            image_urls.append({
                "card_name": name,
                "image_url": None,
            })

    return {"cards": image_urls, "creator_name": deck.creator_name}

@app.get("/decklist")
async def decklist(deck_name: str):
    deck = session.query(Deck).filter(Deck.deck_name == deck_name).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    card_names = [name.strip() for name in deck.cards.split("|") if name.strip()]
    name_list = []

    for name in card_names:
        name_list.append({
            "card_name": name
        })

    return {"cards": name_list, "creator_name": deck.creator_name}

@app.get("/decklist")
async def decklist(deck_name: str):
    print(deck_name)
@app.get("/comidea")
async def newcomideas(
    colorset: Optional[str] = Query(default=None),
    creaturetype: Optional[str] = Query(default=None)
    ):
    
    base_url = "https://api.scryfall.com/cards/search"
    
    if (creaturetype == "not_there"):
        creaturetype = None
        
    # Build query parameters
    query = "t:legendary t:creature"
    if colorset:
        if not color_regex.fullmatch(colorset.lower()):
            return {"error": f"Invalid color input: '{colorset}'. Must be a combination of 'w', 'u', 'b', 'r', 'g' with no repeats (e.g., 'ub', 'wrg')."}
        query += f" c:{colorset.lower()}" 
        query += f" coloridentity={colorset.lower()}"
        query += f" -color>{colorset.lower()}"  
    if creaturetype:
        query += f" t:{creaturetype}"
        
    params = {"q": query.strip()}

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        card_data = response.json()
        
        # Extract names properly
        cards = [card['name'] for card in card_data.get("data", [])]

        if cards:  # Ensure there's at least one match
            card = random.choice(cards)
            
            return search_card(card)
        else:
            return "error: No Matching Cards Found"
        
@app.get("/all_decks")
async def all_decks():
    decks = session.query(Deck).all()
    return [
        {"deck_name": deck.deck_name, "creator_name": deck.creator_name}
        for deck in decks
    ]

@app.post("/build_deck")
async def build_deck(deck: DeckRequest):
    existing_deck = session.query(Deck).filter(Deck.deck_name == deck.deck_name).first()

    if existing_deck:
        existing_deck.creator_name = deck.creator_name
        existing_deck.cards = deck.cards
    else:
        new_deck = Deck(
            creator_name=deck.creator_name,
            deck_name=deck.deck_name,
            cards=deck.cards
        )
        session.add(new_deck)

    session.commit()

    return {
        "message": "Deck created successfully"
    }
    
    
@app.put("/edit_deck")
async def edit_deck(deck: DeckRequest):
    existing_deck = session.query(Deck).filter(Deck.deck_name == deck.deck_name).first()

    if existing_deck:
        existing_deck.deck_name = deck.deck_name
        existing_deck.cards = deck.cards
    else:
        return "error: No deck found"

    session.commit()
    
    return {
        "message": "Deck updated successfully"
    }
    
    
@app.delete("/delete_deck")
async def delete_deck(deck_name: str):
    deck = session.query(Deck).filter(Deck.deck_name == deck_name).first()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    session.delete(deck)
    session.commit()

    return {"message": f"Deck '{deck_name}' has been deleted successfully."}