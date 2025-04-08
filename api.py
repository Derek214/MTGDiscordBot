from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()
    
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

@app.get("/get_card_image")
async def get_card_image(card_name: str):
    image_url = search_card(card_name)
    if 'error' in image_url:
        raise HTTPException(status_code=404, detail=image_url)
    return {"image_url": image_url}