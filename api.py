from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import requests
from sqlalchemy import create_engine, select, or_
from sqlalchemy.orm import sessionmaker
from datamodel import Base, Deck
import random

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

    return {"cards": image_urls, "creator_name": deck.creator_name}

@app.get("/newcomideas")
async def newcomideas(
    colorset: str = Query(default=None),
    creaturetype: str = Query(default=None)
    ):
    
    base_url = "https://api.scryfall.com/cards/search"
    
    # Build query parameters
    query = "t:legendary t:creature"
    if colorset:
        query += f" c:{colorset}"  
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