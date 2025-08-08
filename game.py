class Card:
    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.properties = []


class MonopolyGame:
    def __init__(self):
        self.players = []
        self.deck = []
        self.started = False
        self.current_player_idx = 0

    def start_game(self, player_names):
        self.players = [Player(name) for name in player_names]
        self.deck = self.create_deck()
        self.started = True
        self.current_player_idx = 0
        for player in self.players:
            player.hand = [self.deck.pop() for _ in range(5)]

    def create_deck(self):
        # Simple deck for demo
        deck = [Card(f"Property {i}", "property") for i in range(1, 11)]
        deck += [Card(f"Money {i}", "money") for i in range(1, 11)]
        import random

        random.shuffle(deck)
        return deck

    def draw_card(self):
        if not self.deck:
            return "Deck is empty!"
        player = self.players[self.current_player_idx]
        player.hand.append(self.deck.pop())
        return f"{player.name} drew a card."

    def play_card(self, card_idx):
        player = self.players[self.current_player_idx]
        if card_idx < 0 or card_idx >= len(player.hand):
            return "Invalid card index."
        card = player.hand.pop(card_idx)
        if card.card_type == "property":
            player.properties.append(card)
            if len(player.properties) >= 3:
                self.started = False
                return f"{player.name} wins!"
            return f"{player.name} played {card.name} as property."
        elif card.card_type == "money":
            return f"{player.name} played {card.name} as money."
        return "Unknown card type."

    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
