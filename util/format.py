

from src.settings import CardInfo

card_values = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 10,
    'J': 11,
    'Q': 12,
    'K': 13
}

# in accord with foundation piles'index
card_suits = {
    'Hearts': 0,
    'Diamonds': 1,
    'Spades': 2,
    'Clubs': 3
}


class FormatCard:
    def __init__(self, cardinfo: CardInfo):
        self.color: int = 0 if cardinfo['code']['color'] == 'red' else 1
        self.rank: int = card_values[cardinfo['code']['rank']]
        self.suit: int = card_suits[cardinfo['code']['suit']]
    
    def __eq__(self, other) -> bool:
        if isinstance(other, FormatCard):
            return (self.rank == other.rank and self.suit == other.suit)
        else: return False