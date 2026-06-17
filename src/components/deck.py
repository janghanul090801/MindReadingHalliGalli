from collections import deque

class Deck:
    def __init__(self):
        self.cards = deque()

    def enqueue(self, card):
        self.cards.append(card)

    def dequeue(self):
        if self.isEmpty():
            return None
        return self.cards.popleft()

    def peek(self):
        if self.isEmpty():
            return None
        return self.cards[0]

    def isEmpty(self):
        return len(self.cards) == 0

    def size(self):
        return len(self.cards)