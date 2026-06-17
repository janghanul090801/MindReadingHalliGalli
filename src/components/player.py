from .deck import Deck
from .card_pile import CardPile

class Player:
    def __init__(self, name):
        self.name = name
        self.deck = Deck()
        self.cardPile = CardPile()

    def drawCard(self):
        card = self.deck.dequeue()
        if card is not None:
            self.cardPile.push(card)
        return card
    
    def getCard(self, card):
        self.deck.enqueue(card)

    def getNextCard(self):
        return self.deck.peek()

    def isCardExist(self):
        return self.deck.isEmpty()

    def getCardsCount(self):
        return self.deck.size()