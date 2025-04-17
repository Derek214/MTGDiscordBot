from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker
from datamodel import Base, Deck

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

    return {"cards": image_urls}

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
        "message": "Deck updated successfully" if existing_deck else "Deck created successfully"
    }