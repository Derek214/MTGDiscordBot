from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Deck(Base):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    creator_name = Column(String, nullable=False)
    deck_name = Column(String, nullable=False)
    cards = Column(String, nullable=False)

    def __init__(self, creator_name: str, deck_name: str, cards: str, deck_id: int = None):
        self.id = deck_id
        self.creator_name = creator_name
        self.deck_name = deck_name
        self.cards = cards

    def __repr__(self):
        return f"Deck(id={self.id}, creator='{self.creator_name}', name='{self.deck_name}', cards='{self.cards})"
