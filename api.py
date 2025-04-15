from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker
from datamodel import Deck

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./decks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
session_factory = sessionmaker(bind=engine)

# Initialize the database session
session = session_factory()

# from models import Base


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

@app.get("/view_deck")
async def view_deck(deck_name: str):
    deck = session.query(Deck).filter(Deck.deck_name == deck_name).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    card_names = [name.strip() for name in deck.cards.split("{") if name.strip()]
    image_urls = []

    for name in card_names:
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

    return {image_urls}

@app.put("/build_deck")
async def view_deck(deck_name: str, creator_name: str, cards: str):
    existing_deck = session.query(Deck).filter(Deck.deck_name == deck_name).first()
    
    if existing_deck:
        # Update the existing deck
        existing_deck.creator_name = creator_name
        existing_deck.cards = cards
    else:
        # Create a new deck
        new_deck = Deck(
            deck_name=deck_name,
            creator_name=creator_name,
            cards=cards
        )
        session.add(new_deck)

    # Commit the changes
    session.commit()

    return {
        "message": "Deck saved successfully"
    }