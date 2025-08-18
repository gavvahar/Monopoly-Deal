"""
Game logic for Monopoly Deal.
"""


class Card:
    """Represents a Monopoly Deal card."""

    def __init__(self, name, card_type):
        self.name = name
        self.card_type = card_type


class Player:
    """Represents a player in Monopoly Deal."""

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.properties = []


class MonopolyGame:
    """Main Monopoly Deal game class."""

    def __init__(self):
        self.players = []
        self.deck = []
        self.started = False
        self.current_player_idx = 0

    def start_game(self, player_names):
        """Start a new game with the given player names."""
        self.players = [Player(name) for name in player_names]
        self.deck = self.create_deck()
        self.started = True
        self.current_player_idx = 0
        for player in self.players:
            player.hand = [self.deck.pop() for _ in range(5)]

    def create_deck(self):
        """Create a simple deck for demo purposes."""
        # Simple deck for demo
        deck = [Card(f"Property {i}", "property") for i in range(1, 11)]
        deck += [Card(f"Money {i}", "money") for i in range(1, 11)]
        import random

        random.shuffle(deck)
        return deck

    def draw_card(self):
        """Draw a card for the current player."""
        if not self.deck:
            return "Deck is empty!"
        player = self.players[self.current_player_idx]
        player.hand.append(self.deck.pop())
        return f"{player.name} drew a card."

    def play_card(self, card_idx):
        """Play a card from the current player's hand."""
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
        if card.card_type == "money":
            return f"{player.name} played {card.name} as money."
        return "Unknown card type."

    def next_turn(self):
        """Advance to the next player's turn."""
        next_idx = self.current_player_idx + 1
        self.current_player_idx = next_idx % len(self.players)
