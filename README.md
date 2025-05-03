# MTGDiscordBot
Discord bot, API, and Database intended for use by a Magic the Gathering Commander Discord Community
# Commands
- botinfo -
        Displays all bot commands
- alldecks -
        Displays all decks along with who created them
- builddeck -
        This command allows users to input a decklist with each card separated by a "{" character. Adds to the decks.db database
- card -
        Allows users to search the Scryfall API for a card based on the name input after card command. Uses the fuzzy search to make card searching as easy as possible
- comidea -
        Allows users to input a color combination and a creature type and returns images for a Legendary Creature matching the parameters
- viewdeck -
        Allows users to input a deckname and returns images of all cards in the deck
- decklist -
        Allows users to input a deckname and returns a list of all cards in the deck
- random -
        Retrieves a random card from the Scryfall API using the random endpoint
- editdeck -
        Edit a deck within the database if you are the deck creator
- deletedeck -
        Delete a deck within the database if you are the creator 