"""
Game logic for the car-themed Monopoly Deal (functional, no classes).
"""

import random
import cards
import rules

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


# ---------------- Helpers ----------------


def _find_player(state, name):
    """Return player dict by name, or None."""
    for p in state["players"]:
        if p["name"] == name:
            return p
    return None


def _player_idx(state, name):
    """Return player index by name, or None."""
    for i, p in enumerate(state["players"]):
        if p["name"] == name:
            return i
    return None


def _count_color(player, color):
    """Count properties a player owns in a given color (including assigned wilds)."""
    return sum(1 for c in player["properties"] if c.get("color") == color)


def _is_complete_set(player, color):
    """Return True if player has a complete set of the given color."""
    return rules.is_full_set(color, _count_color(player, color))


def _check_win(state, player):
    """Check if player has won (3 complete sets). Returns result message."""
    if count_complete_sets(player) >= 3:
        state["started"] = False
        return f"{player['name']} wins with 3 complete sets!"
    return None


def _undo_play(state, hand, card_idx, card):
    """Return card to hand and undo play count increment."""
    hand.insert(card_idx, card)
    state["plays_this_turn"] -= 1


def count_complete_sets(player):
    """Count the number of complete color sets a player owns."""
    set_sizes = rules.get_set_sizes()
    color_counts = {}
    for card in player["properties"]:
        color = card.get("color")
        if color and color in set_sizes:
            color_counts[color] = color_counts.get(color, 0) + 1
    return sum(
        1 for color, cnt in color_counts.items() if rules.is_full_set(color, cnt)
    )


# ---------------- Auto-Payment ----------------


def _auto_pay(state, payer_idx, collector_idx, amount):
    """
    Transfer payment from payer to collector (bank first, then properties).
    Uses the greedy algorithm: largest denomination first to minimize card count.
    Returns amount actually transferred (may exceed amount due; no change given).
    """
    payer = state["players"][payer_idx]
    collector = state["players"][collector_idx]

    paid = 0
    moved = []

    # Pay from bank (largest first)
    bank_sorted = sorted(
        range(len(payer["bank"])),
        key=lambda i: payer["bank"][i].get("value", 0),
        reverse=True,
    )
    take_bank = []
    for i in bank_sorted:
        if paid >= amount:
            break
        take_bank.append(i)
        paid += payer["bank"][i].get("value", 0)
    for i in sorted(take_bank, reverse=True):
        moved.append(payer["bank"].pop(i))

    # Pay from properties if still short (largest value first)
    if paid < amount:
        props_sorted = sorted(
            range(len(payer["properties"])),
            key=lambda i: payer["properties"][i].get("value", 0),
            reverse=True,
        )
        take_props = []
        for i in props_sorted:
            if paid >= amount:
                break
            take_props.append(i)
            paid += payer["properties"][i].get("value", 0)
        for i in sorted(take_props, reverse=True):
            moved.append(payer["properties"].pop(i))

    # All transferred cards go to collector's bank
    collector["bank"].extend(moved)
    return paid


# ---------------- State Management ----------------


def start_game(player_names):
    """
    Start a new game; return game state dict.
    state = {
        'players': [ { 'name', 'hand', 'properties', 'bank' }, ... ],
        'deck': [cards],
        'started': bool,
        'current_player_idx': int,
        'draws_done': bool,
        'plays_this_turn': int,
        'double_rent_count': int,
        'houses': { player_idx: { color: True } },
        'hotels': { player_idx: { color: True } },
    }
    """
    deck = create_deck()
    players = []
    for name in player_names:
        player = {
            "name": name,
            "hand": [deck.pop() for _ in range(5)],
            "properties": [],
            "bank": [],
        }
        players.append(player)
    n = len(players)
    return {
        "players": players,
        "deck": deck,
        "started": True,
        "current_player_idx": 0,
        "draws_done": False,
        "plays_this_turn": 0,
        "double_rent_count": 0,
        "houses": {i: {} for i in range(n)},
        "hotels": {i: {} for i in range(n)},
    }


# ---------------- Game Actions ----------------


def draw_card(state):
    """Draw a card for current player."""
    if not state["deck"]:
        return "Deck is empty!"
    player = state["players"][state["current_player_idx"]]
    player["hand"].append(state["deck"].pop())
    return f"{player['name']} drew a card."


def bank_action_card(state, card_idx):
    """Bank an action or rent card as money (its face value). Counts as 1 play."""
    actor_idx = state["current_player_idx"]
    player = state["players"][actor_idx]
    hand = player["hand"]
    if card_idx < 0 or card_idx >= len(hand):
        return "Invalid card index."
    max_plays = rules.get_turn_limits()["max_plays"]
    if state.get("plays_this_turn", 0) >= max_plays:
        return f"You have already played {max_plays} cards this turn."
    card = hand[card_idx]
    if card["card_type"] not in ("action", "rent"):
        return "Only action and rent cards can be banked this way."
    hand.pop(card_idx)
    state["plays_this_turn"] += 1
    player["bank"].append(card)
    return f"{player['name']} banked {card['name']} as {card['value']}M."


def play_card(
    state,
    card_idx,
    target_player_name=None,
    target_card_idx=None,
    target_color=None,
    own_card_idx=None,
):
    """Play a card from current player's hand."""
    actor_idx = state["current_player_idx"]
    player = state["players"][actor_idx]
    hand = player["hand"]

    if card_idx < 0 or card_idx >= len(hand):
        return "Invalid card index."

    max_plays = rules.get_turn_limits()["max_plays"]
    if state.get("plays_this_turn", 0) >= max_plays:
        return f"You have already played {max_plays} cards this turn."

    card = hand.pop(card_idx)
    state["plays_this_turn"] += 1
    card_type = card["card_type"]

    if card_type == "money":
        player["bank"].append(card)
        return f"{player['name']} banked {card['name']} (+{card['value']}M)."

    if card_type == "property":
        player["properties"].append(card)
        win = _check_win(state, player)
        if win:
            return win
        return f"{player['name']} played {card['name']} as property."

    if card_type == "wild":
        valid_colors = card.get("colors", [])
        if len(valid_colors) == 1:
            # Only one option — assign automatically
            card["color"] = valid_colors[0]
        elif target_color and target_color in valid_colors:
            card["color"] = target_color
        else:
            _undo_play(state, hand, card_idx, card)
            return f"Choose a color for {card['name']}: {', '.join(valid_colors)}"
        player["properties"].append(card)
        win = _check_win(state, player)
        if win:
            return win
        return f"{player['name']} placed {card['name']} as {card['color']} property."

    if card_type == "action":
        return _handle_action(
            state,
            card,
            actor_idx,
            card_idx,
            hand,
            target_player_name,
            target_card_idx,
            target_color,
            own_card_idx,
        )

    if card_type == "rent":
        return _handle_rent(
            state,
            card,
            actor_idx,
            card_idx,
            hand,
            target_player_name,
            target_color,
        )

    return f"{player['name']} played {card['name']}."


# ---------------- Action Card Handlers ----------------


def _handle_action(
    state,
    card,
    actor_idx,
    card_idx,
    hand,
    target_player_name,
    target_card_idx,
    target_color,
    own_card_idx,
):
    """Execute an action card effect."""
    actor = state["players"][actor_idx]
    name = card["name"]

    # Green Light (Pass Go): draw 2 cards immediately
    if name == "Green Light":
        drawn = 0
        for _ in range(2):
            if state["deck"]:
                actor["hand"].append(state["deck"].pop())
                drawn += 1
        return f"{actor['name']} played Green Light and drew {drawn} card(s)."

    # Turbo Charge (Double The Rent): double the next rent charged
    if name == "Turbo Charge":
        state["double_rent_count"] = state.get("double_rent_count", 0) + 1
        return f"{actor['name']} played Turbo Charge! Next rent is doubled."

    # Track Day Fees (It's My Birthday): all opponents pay 2M
    if name == "Track Day Fees":
        msgs = []
        for i, opp in enumerate(state["players"]):
            if i != actor_idx:
                paid = _auto_pay(state, i, actor_idx, 2)
                msgs.append(f"{opp['name']} paid {paid}M")
        return f"{actor['name']} played Track Day Fees! " + ", ".join(msgs) + "."

    # Repo Notice (Debt Collector): one target pays 5M
    if name == "Repo Notice":
        if not target_player_name:
            _undo_play(state, hand, card_idx, card)
            return "Repo Notice requires a target player."
        target_idx = _player_idx(state, target_player_name)
        if target_idx is None or target_idx == actor_idx:
            _undo_play(state, hand, card_idx, card)
            return "Invalid target player."
        paid = _auto_pay(state, target_idx, actor_idx, 5)
        return (
            f"{actor['name']} served Repo Notice to "
            f"{state['players'][target_idx]['name']}! Collected {paid}M."
        )

    # Garage Upgrade (House): add a house to actor's complete set
    if name == "Garage Upgrade":
        eligible = [
            c
            for c in rules.get_build_eligible_colors()
            if _is_complete_set(actor, c)
            and not state["houses"].get(actor_idx, {}).get(c, False)
            and not state["hotels"].get(actor_idx, {}).get(c, False)
        ]
        if not eligible:
            _undo_play(state, hand, card_idx, card)
            return "No eligible complete set to build a house on."
        if not target_color or target_color not in eligible:
            _undo_play(state, hand, card_idx, card)
            return f"Choose a color set for the house: {', '.join(eligible)}"
        state["houses"].setdefault(actor_idx, {})[target_color] = True
        return f"{actor['name']} built a house on {target_color} (+3M rent)!"

    # Luxury Showroom (Hotel): add a hotel to a housed complete set
    if name == "Luxury Showroom":
        eligible = [
            c
            for c in rules.get_build_eligible_colors()
            if _is_complete_set(actor, c)
            and state["houses"].get(actor_idx, {}).get(c, False)
            and not state["hotels"].get(actor_idx, {}).get(c, False)
        ]
        if not eligible:
            _undo_play(state, hand, card_idx, card)
            return "No eligible complete set with a house to upgrade to hotel."
        if not target_color or target_color not in eligible:
            _undo_play(state, hand, card_idx, card)
            return f"Choose a color set for the hotel: {', '.join(eligible)}"
        state["hotels"].setdefault(actor_idx, {})[target_color] = True
        return f"{actor['name']} built a hotel on {target_color} (+4M rent)!"

    # Garage Takeover (Deal Breaker): steal a complete set from an opponent
    if name == "Garage Takeover":
        if not target_player_name or not target_color:
            _undo_play(state, hand, card_idx, card)
            return "Garage Takeover requires a target player and color set."
        target_idx = _player_idx(state, target_player_name)
        if target_idx is None or target_idx == actor_idx:
            _undo_play(state, hand, card_idx, card)
            return "Invalid target player."
        target = state["players"][target_idx]
        if not _is_complete_set(target, target_color):
            _undo_play(state, hand, card_idx, card)
            return f"{target['name']} does not have a complete {target_color} set."
        # Move all cards of that color from target to actor
        stolen = [c for c in target["properties"] if c.get("color") == target_color]
        target["properties"] = [
            c for c in target["properties"] if c.get("color") != target_color
        ]
        actor["properties"].extend(stolen)
        # Transfer house/hotel
        if state["houses"].get(target_idx, {}).get(target_color):
            state["houses"].setdefault(actor_idx, {})[target_color] = True
            state["houses"][target_idx].pop(target_color, None)
        if state["hotels"].get(target_idx, {}).get(target_color):
            state["hotels"].setdefault(actor_idx, {})[target_color] = True
            state["hotels"][target_idx].pop(target_color, None)
        win = _check_win(state, actor)
        if win:
            return f"{actor['name']} stole {target['name']}'s {target_color} set! {win}"
        return f"{actor['name']} stole {target['name']}'s complete {target_color} set!"

    # Sneak Swap (Sly Deal): steal one property not in a complete set
    if name == "Sneak Swap":
        if not target_player_name or target_card_idx is None:
            _undo_play(state, hand, card_idx, card)
            return "Sneak Swap requires a target player and their property index."
        target_idx = _player_idx(state, target_player_name)
        if target_idx is None or target_idx == actor_idx:
            _undo_play(state, hand, card_idx, card)
            return "Invalid target player."
        target = state["players"][target_idx]
        if target_card_idx < 0 or target_card_idx >= len(target["properties"]):
            _undo_play(state, hand, card_idx, card)
            return "Invalid property index."
        stolen = target["properties"][target_card_idx]
        stolen_color = stolen.get("color", "")
        if stolen_color and _is_complete_set(target, stolen_color):
            _undo_play(state, hand, card_idx, card)
            return "Cannot steal from a complete set."
        target["properties"].pop(target_card_idx)
        actor["properties"].append(stolen)
        win = _check_win(state, actor)
        if win:
            return (
                f"{actor['name']} stole {stolen['name']} from {target['name']}! {win}"
            )
        return f"{actor['name']} stole {stolen['name']} from {target['name']}!"

    # Tow Trade (Forced Deal): swap your property for theirs (not from complete sets)
    if name == "Tow Trade":
        if not target_player_name or target_card_idx is None or own_card_idx is None:
            _undo_play(state, hand, card_idx, card)
            return "Tow Trade requires a target player, their property index, and your property index."
        target_idx = _player_idx(state, target_player_name)
        if target_idx is None or target_idx == actor_idx:
            _undo_play(state, hand, card_idx, card)
            return "Invalid target player."
        target = state["players"][target_idx]
        if target_card_idx < 0 or target_card_idx >= len(target["properties"]):
            _undo_play(state, hand, card_idx, card)
            return "Invalid target property index."
        if own_card_idx < 0 or own_card_idx >= len(actor["properties"]):
            _undo_play(state, hand, card_idx, card)
            return "Invalid own property index."
        their_card = target["properties"][target_card_idx]
        their_color = their_card.get("color", "")
        if their_color and _is_complete_set(target, their_color):
            _undo_play(state, hand, card_idx, card)
            return "Cannot swap a property from a complete set."
        own_prop = actor["properties"][own_card_idx]
        own_color = own_prop.get("color", "")
        if own_color and _is_complete_set(actor, own_color):
            _undo_play(state, hand, card_idx, card)
            return "Cannot swap a property from your own complete set."
        # Execute swap
        target["properties"][target_card_idx] = own_prop
        actor["properties"][own_card_idx] = their_card
        win = _check_win(state, actor)
        if win:
            return f"{actor['name']} swapped {own_prop['name']} for {their_card['name']}! {win}"
        return f"{actor['name']} swapped {own_prop['name']} for {their_card['name']}."

    # Cut the Engine (Just Say No): response-only card, cannot be played proactively
    if name == "Cut the Engine":
        _undo_play(state, hand, card_idx, card)
        return "Cut the Engine can only be played in response to an action. Use 'Bank' to bank it as 4M."

    return f"{actor['name']} played {card['name']}."


# ---------------- Rent Card Handlers ----------------


def _handle_rent(
    state,
    card,
    actor_idx,
    card_idx,
    hand,
    target_player_name,
    target_color,
):
    """Execute a rent card effect."""
    actor = state["players"][actor_idx]
    rent_colors = rules.rent_colors_for_card(card["name"])
    is_wild_rent = card["name"] == "Rent Wild (Any Collection)"

    # Determine which color to charge rent for
    if not target_color or target_color not in rent_colors:
        _undo_play(state, hand, card_idx, card)
        eligible = [c for c in rent_colors if _count_color(actor, c) > 0]
        if not eligible:
            return "You have no properties matching this rent card."
        return f"Choose a color to charge rent on: {', '.join(eligible)}"

    owned = _count_color(actor, target_color)
    if owned == 0:
        _undo_play(state, hand, card_idx, card)
        return f"You have no {target_color} properties to charge rent on."

    has_house = state.get("houses", {}).get(actor_idx, {}).get(target_color, False)
    has_hotel = state.get("hotels", {}).get(actor_idx, {}).get(target_color, False)
    double_count = state.get("double_rent_count", 0)
    rent_amount = rules.compute_rent(
        target_color, owned, has_house, has_hotel, double_count
    )

    # Consume any double-rent multiplier
    state["double_rent_count"] = 0

    if is_wild_rent:
        # Wild rent targets one specified opponent
        if not target_player_name:
            _undo_play(state, hand, card_idx, card)
            return "Wild rent requires a target player."
        target_idx = _player_idx(state, target_player_name)
        if target_idx is None or target_idx == actor_idx:
            _undo_play(state, hand, card_idx, card)
            return "Invalid target player."
        paid = _auto_pay(state, target_idx, actor_idx, rent_amount)
        return (
            f"{actor['name']} charged {rent_amount}M {target_color} rent to "
            f"{state['players'][target_idx]['name']} (paid {paid}M)."
        )
    else:
        # Regular rent targets all opponents
        msgs = []
        for i, opp in enumerate(state["players"]):
            if i != actor_idx:
                paid = _auto_pay(state, i, actor_idx, rent_amount)
                msgs.append(f"{opp['name']} paid {paid}M")
        return (
            f"{actor['name']} charged {rent_amount}M {target_color} rent! "
            + ", ".join(msgs)
            + "."
        )


# ---------------- Turn Management ----------------


def next_turn(state):
    """End current player's turn (enforce hand limit), advance to next player."""
    finishing_player = state["players"][state["current_player_idx"]]
    hand_limit = rules.get_turn_limits()["hand_limit"]
    # Auto-discard lowest-value cards down to hand limit
    while len(finishing_player["hand"]) > hand_limit:
        min_idx = min(
            range(len(finishing_player["hand"])),
            key=lambda i: finishing_player["hand"][i].get("value", 0),
        )
        finishing_player["hand"].pop(min_idx)

    state["current_player_idx"] = (state["current_player_idx"] + 1) % len(
        state["players"]
    )
    state["draws_done"] = False
    state["plays_this_turn"] = 0
    state["double_rent_count"] = 0


# ---------------- Optional Helper ----------------


def current_player(state):
    """Return current player dict."""
    return state["players"][state["current_player_idx"]]
