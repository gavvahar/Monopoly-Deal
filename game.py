"""
Game logic for the car-themed deck (functional, no classes).
"""

import random
import cards

# ---------------- Card / Deck ----------------


def create_deck():
    """Create a shuffled deck using the canonical car-themed cards."""
    raw_deck = cards.shuffle_deck()
    normalized = []
    for card in raw_deck:
        normalized_card = {
            "name": card["name"],
            "card_type": card["type"],
            "value": card.get("value", 0),
        }
        if "description" in card:
            normalized_card["description"] = card["description"]
        if "color" in card:
            normalized_card["color"] = card["color"]
        if "colors" in card:
            normalized_card["colors"] = list(card["colors"])
        normalized.append(normalized_card)
    random.shuffle(normalized)
    return normalized


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
    card_type = card["card_type"]
    if card_type == "property":
        player["properties"].append(card)
        if len(player["properties"]) >= 3:
            state["started"] = False
            return f"{player['name']} wins!"
        return f"{player['name']} played {card['name']} as property."
    if card_type == "money":
        return f"{player['name']} banked {card['name']}."
    if card_type == "action":
        return f"{player['name']} played action card {card['name']}."
    if card_type == "wild":
        return f"{player['name']} placed wild card {card['name']}."
    if card_type == "rent":
        return f"{player['name']} prepared rent card {card['name']}."
    return f"{player['name']} played {card['name']}."


def next_turn(state):
    """Advance to next player's turn."""
    state["current_player_idx"] = (state["current_player_idx"] + 1) % len(
        state["players"]
    )


# ---------------- Optional Helper ----------------


def current_player(state):
    """Return current player dict."""
    return state["players"][state["current_player_idx"]]
