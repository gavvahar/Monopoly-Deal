"""
Game logic for Monopoly Deal (functional, no classes).
"""

import random

# ---------------- Card / Deck ----------------


def create_deck():
    """Create a shuffled deck with enough cards for multiplayer games."""
    # Create enough cards for up to 5 players (5 players x 5 cards = 25 minimum)
    deck = [{"name": f"Property {i}", "card_type": "property"} for i in range(1, 21)]
    deck += [{"name": f"Money {i}", "card_type": "money"} for i in range(1, 21)]
    deck += [{"name": f"Action {i}", "card_type": "action"} for i in range(1, 11)]
    random.shuffle(deck)
    return deck


# ---------------- State Management ----------------


def start_game(player_names):
    """
    Start a new game; return game state dict.
    state = {
        'players': [ { 'name': str, 'hand': [cards], 'properties': [cards] }, ... ],
        'deck': [cards],
        'started': bool,
        'current_player_idx': int
    }
    """
    deck = create_deck()
    players = []
    for name in player_names:
        player = {
            "name": name,
            "hand": [deck.pop() for _ in range(5)],
            "properties": [],
        }
        players.append(player)
    return {"players": players, "deck": deck, "started": True, "current_player_idx": 0}


# ---------------- Game Actions ----------------


def draw_card(state):
    """Draw a card for current player."""
    if not state["deck"]:
        return "Deck is empty!"
    player = state["players"][state["current_player_idx"]]
    player["hand"].append(state["deck"].pop())
    return f"{player['name']} drew a card."


def play_card(state, card_idx):
    """Play a card from current player's hand."""
    player = state["players"][state["current_player_idx"]]
    hand = player["hand"]
    if card_idx < 0 or card_idx >= len(hand):
        return "Invalid card index."
    card = hand.pop(card_idx)
    if card["card_type"] == "property":
        player["properties"].append(card)
        if len(player["properties"]) >= 3:
            state["started"] = False
            return f"{player['name']} wins!"
        return f"{player['name']} played {card['name']} as property."
    if card["card_type"] == "money":
        return f"{player['name']} played {card['name']} as money."
    return "Unknown card type."


def next_turn(state):
    """Advance to next player's turn."""
    state["current_player_idx"] = (state["current_player_idx"] + 1) % len(
        state["players"]
    )


# ---------------- Optional Helper ----------------


def current_player(state):
    """Return current player dict."""
    return state["players"][state["current_player_idx"]]
