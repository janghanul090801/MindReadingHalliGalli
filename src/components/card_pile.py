class CardPile:
    def __init__(self):
        self.cards = []

    def push(self, card):
        self.cards.append(card)

    def pop(self):
        if len(self.cards) == 0:
            return None
        return self.cards.pop()

    def top(self):
        if len(self.cards) == 0:
            return None
        return self.cards[-1]

    def clear(self):
        result = self.cards[:]
        self.cards.clear()
        return result