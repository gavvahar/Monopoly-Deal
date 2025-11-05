"""
Monopoly Deal card definitions and deck builder.
"""

from collections import Counter
import random

ALL_PROPERTY_COLORS = [
    "Brown",
    "Light Blue",
    "Pink",
    "Orange",
    "Red",
    "Yellow",
    "Green",
    "Dark Blue",
    "Railroads",
    "Utilities",
]

PROPERTY_SET_DEFINITIONS = {
    "Brown": [
        ("Mediterranean Avenue", 1),
        ("Baltic Avenue", 1),
    ],
    "Light Blue": [
        ("Oriental Avenue", 1),
        ("Vermont Avenue", 1),
        ("Connecticut Avenue", 1),
    ],
    "Pink": [
        ("St. Charles Place", 2),
        ("States Avenue", 2),
        ("Virginia Avenue", 2),
    ],
    "Orange": [
        ("St. James Place", 2),
        ("Tennessee Avenue", 2),
        ("New York Avenue", 2),
    ],
    "Red": [
        ("Kentucky Avenue", 3),
        ("Indiana Avenue", 3),
        ("Illinois Avenue", 3),
    ],
    "Yellow": [
        ("Atlantic Avenue", 3),
        ("Ventnor Avenue", 3),
        ("Marvin Gardens", 3),
    ],
    "Green": [
        ("Pacific Avenue", 4),
        ("North Carolina Avenue", 4),
        ("Pennsylvania Avenue", 4),
    ],
    "Dark Blue": [
        ("Park Place", 4),
        ("Boardwalk", 4),
    ],
    "Railroads": [
        ("Reading Railroad", 2),
        ("Pennsylvania Railroad", 2),
        ("B&O Railroad", 2),
        ("Short Line", 2),
    ],
    "Utilities": [
        ("Electric Company", 2),
        ("Water Works", 2),
    ],
}

PROPERTY_WILD_DEFINITIONS = [
    {
        "name": "Wild Brown/Light Blue",
        "colors": ("Brown", "Light Blue"),
        "value": 4,
        "count": 1,
    },
    {
        "name": "Wild Pink/Orange",
        "colors": ("Pink", "Orange"),
        "value": 2,
        "count": 2,
    },
    {
        "name": "Wild Red/Yellow",
        "colors": ("Red", "Yellow"),
        "value": 3,
        "count": 2,
    },
    {
        "name": "Wild Green/Dark Blue",
        "colors": ("Green", "Dark Blue"),
        "value": 4,
        "count": 2,
    },
    {
        "name": "Wild Light Blue/Railroad",
        "colors": ("Light Blue", "Railroads"),
        "value": 4,
        "count": 1,
    },
    {
        "name": "Wild Railroad",
        "colors": ("Railroads",),
        "value": 2,
        "count": 2,
    },
    {
        "name": "Wild Railroad/Utility",
        "colors": ("Railroads", "Utilities"),
        "value": 2,
        "count": 1,
    },
    {
        "name": "Wild Utility",
        "colors": ("Utilities",),
        "value": 2,
        "count": 1,
    },
    {
        "name": "Property Wild (Any Color)",
        "colors": tuple(ALL_PROPERTY_COLORS),
        "value": 0,
        "count": 2,
    },
]

MONEY_CARD_DEFINITIONS = {
    "1M": {"count": 6, "value": 1, "type": "money"},
    "2M": {"count": 5, "value": 2, "type": "money"},
    "3M": {"count": 3, "value": 3, "type": "money"},
    "4M": {"count": 3, "value": 4, "type": "money"},
    "5M": {"count": 2, "value": 5, "type": "money"},
    "10M": {"count": 1, "value": 10, "type": "money"},
}

ACTION_CARD_DEFINITIONS = {
    "Deal Breaker": {"count": 2, "value": 5, "type": "action"},
    "Sly Deal": {"count": 3, "value": 3, "type": "action"},
    "Forced Deal": {"count": 4, "value": 3, "type": "action"},
    "Debt Collector": {"count": 3, "value": 3, "type": "action"},
    "It’s My Birthday": {"count": 3, "value": 2, "type": "action"},
    "Pass Go": {"count": 10, "value": 1, "type": "action"},
    "Double the Rent": {"count": 2, "value": 1, "type": "action"},
    "House": {"count": 3, "value": 3, "type": "action"},
    "Hotel": {"count": 2, "value": 4, "type": "action"},
    "Just Say No": {"count": 3, "value": 4, "type": "action"},
}

RENT_CARD_DEFINITIONS = {
    "Rent Brown/Light Blue": {"count": 2, "value": 1, "type": "rent"},
    "Rent Pink/Orange": {"count": 2, "value": 1, "type": "rent"},
    "Rent Red/Yellow": {"count": 2, "value": 1, "type": "rent"},
    "Rent Green/Dark Blue": {"count": 2, "value": 1, "type": "rent"},
    "Rent Railroad/Utility": {"count": 2, "value": 1, "type": "rent"},
    "Rent Wild (Any Color)": {"count": 3, "value": 3, "type": "rent"},
}


def money_cards():
    """Return dictionary of money cards."""
    return {name: dict(data) for name, data in MONEY_CARD_DEFINITIONS.items()}


def property_cards():
    """Return dictionary of property cards keyed by card name."""
    cards = {}
    for color, entries in PROPERTY_SET_DEFINITIONS.items():
        for name, value in entries:
            cards[name] = {
                "count": 1,
                "value": value,
                "type": "property",
                "color": color,
            }
    return cards


def property_wilds():
    """Return dictionary of property wild cards keyed by card name."""
    cards = {}
    for wild in PROPERTY_WILD_DEFINITIONS:
        cards[wild["name"]] = {
            "count": wild["count"],
            "value": wild["value"],
            "type": "wild",
            "colors": list(wild["colors"]),
        }
    return cards


def action_cards():
    """Return dictionary of action cards."""
    return {name: dict(data) for name, data in ACTION_CARD_DEFINITIONS.items()}


def rent_cards():
    """Return dictionary of rent cards."""
    return {name: dict(data) for name, data in RENT_CARD_DEFINITIONS.items()}


def _expand_group(deck, definitions):
    for name, data in definitions.items():
        count = data["count"]
        template = {k: v for k, v in data.items() if k != "count"}
        template["name"] = name
        for _ in range(count):
            card = dict(template)
            if "colors" in template:
                card["colors"] = list(template["colors"])
            deck.append(card)


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
        _expand_group(deck, group)
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
