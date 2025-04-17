# MTGDiscordBot
Discord bot, API, and Database intended for use by a Magic the Gathering Commander Discord Community
# Commands
- builddeck 
        This command allows users to input a decklist with each card separated by a "{" character. Adds to the decks.db database.
- card
        Allows users to search the Scryfall API for a card based on the name input after card command. Uses the fuzzy search to make card searching as easy as possible.
- random
        Retrieves a random card from the Scryfall API using the random endpoint.
- deckview
        Allows users to view decks in the database by inputting the name. Returns each cards image successively.
- newcomideas
        Allows users to input a color combination and a creature type and returns images for Legendary Creatures matching those parameters.
- botinfo
        Returns informations about all bot commands
- editdeck
        Edit decks within the database if you are the deck creator
- deletedeck
        Deletes deck within the database if you are the owner. 