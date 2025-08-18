"""
Monopoly Deal card definitions and deck builder.
"""

from collections import Counter
import random


def money_cards():
    """Return dictionary of money cards."""
    return {
        "1M": {"count": 6, "value": 1, "type": "money"},
        "2M": {"count": 5, "value": 2, "type": "money"},
        "3M": {"count": 3, "value": 3, "type": "money"},
        "4M": {"count": 3, "value": 4, "type": "money"},
        "5M": {"count": 2, "value": 5, "type": "money"},
        "10M": {"count": 1, "value": 10, "type": "money"},
    }


def property_cards():
    """Return dictionary of property cards."""
    return {
        "Mediterranean Avenue": {"count": 1, "value": 1, "type": "property"},
        "Baltic Avenue": {"count": 1, "value": 1, "type": "property"},
        "Oriental Avenue": {"count": 1, "value": 1, "type": "property"},
        "Vermont Avenue": {"count": 1, "value": 1, "type": "property"},
        "Connecticut Avenue": {"count": 1, "value": 1, "type": "property"},
        "St. Charles Place": {"count": 1, "value": 2, "type": "property"},
        "States Avenue": {"count": 1, "value": 2, "type": "property"},
        "Virginia Avenue": {"count": 1, "value": 2, "type": "property"},
        "St. James Place": {"count": 1, "value": 2, "type": "property"},
        "Tennessee Avenue": {"count": 1, "value": 2, "type": "property"},
        "New York Avenue": {"count": 1, "value": 2, "type": "property"},
        "Kentucky Avenue": {"count": 1, "value": 3, "type": "property"},
        "Indiana Avenue": {"count": 1, "value": 3, "type": "property"},
        "Illinois Avenue": {"count": 1, "value": 3, "type": "property"},
        "Atlantic Avenue": {"count": 1, "value": 3, "type": "property"},
        "Ventnor Avenue": {"count": 1, "value": 3, "type": "property"},
        "Marvin Gardens": {"count": 1, "value": 3, "type": "property"},
        "Pacific Avenue": {"count": 1, "value": 4, "type": "property"},
        "North Carolina Avenue": {"count": 1, "value": 4, "type": "property"},
        "Pennsylvania Avenue": {"count": 1, "value": 4, "type": "property"},
        "Park Place": {"count": 1, "value": 4, "type": "property"},
        "Boardwalk": {"count": 1, "value": 4, "type": "property"},
        "Reading Railroad": {"count": 1, "value": 2, "type": "property"},
        "Pennsylvania Railroad": {"count": 1, "value": 2, "type": "property"},
        "B&O Railroad": {"count": 1, "value": 2, "type": "property"},
        "Short Line": {"count": 1, "value": 2, "type": "property"},
        "Electric Company": {"count": 1, "value": 2, "type": "property"},
        "Water Works": {"count": 1, "value": 2, "type": "property"},
    }


def property_wilds():
    """Return dictionary of property wild cards."""
    return {
        "Blue/Green Wild": {"count": 1, "value": 4, "type": "wild"},
        "Railroad/Utility Wild": {"count": 1, "value": 2, "type": "wild"},
        "Property Wild (Any Color)": {
            "count": 2,
            "value": 0,
            "type": "wild",
        },
    }


def action_cards():
    """Return dictionary of action cards."""
    return {
        "Deal Breaker": {"count": 2, "value": 5, "type": "action"},
        "Sly Deal": {"count": 3, "value": 3, "type": "action"},
        "Forced Deal": {"count": 4, "value": 3, "type": "action"},
        "Debt Collector": {"count": 3, "value": 3, "type": "action"},
        "It’s My Birthday": {"count": 3, "value": 2, "type": "action"},
        "Pass Go": {"count": 10, "value": 1, "type": "action"},
        "Double the Rent": {"count": 3, "value": 1, "type": "action"},
        "House": {"count": 3, "value": 3, "type": "action"},
        "Hotel": {"count": 2, "value": 4, "type": "action"},
        "Just Say No": {"count": 6, "value": 4, "type": "action"},
    }


def rent_cards():
    """Return dictionary of rent cards."""
    return {
        "Rent Brown/Light Blue": {"count": 2, "value": 1, "type": "rent"},
        "Rent Pink/Orange": {"count": 2, "value": 1, "type": "rent"},
        "Rent Red/Yellow": {"count": 2, "value": 1, "type": "rent"},
        "Rent Green/Dark Blue": {"count": 2, "value": 1, "type": "rent"},
        "Rent Railroad/Utility": {"count": 2, "value": 1, "type": "rent"},
        "Rent Wild (Any Color)": {"count": 3, "value": 3, "type": "rent"},
    }


def build_deck():
    """Return the full deck of 110 cards as a list of dicts."""
    deck = []

    for group in (
        money_cards(),
        property_cards(),
        property_wilds(),
        action_cards(),
        rent_cards(),
    ):
        for card, data in group.items():
            deck.extend(
                [{"name": card, "value": data["value"], "type": data["type"]}]
                * data["count"]
            )

    return deck


def shuffle_deck():
    """Return a shuffled deck."""
    deck = build_deck()
    random.shuffle(deck)
    return deck


if __name__ == "__main__":
    deck_list = build_deck()
    print(f"Total cards: {len(deck_list)}")
    print(Counter(c["type"] for c in deck_list))
